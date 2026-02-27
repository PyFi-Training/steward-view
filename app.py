import os
import io
import sys
import time
import pickle
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------
# App config
# ----------------------------
st.set_page_config(
    page_title="Steward View (PyFi) — Streamlit",
    page_icon="📊",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "data" / "output"
CSV_PATH = OUTPUT_DIR / "labeled_data.csv"
MATCHER_PATH = OUTPUT_DIR / "matcher.pkl"

# Chart thresholds (mirrors src/analysis/config/charts.py)
CATEGORY_MIN = 500
VENDOR_MIN = 500

# Pipeline steps in order
PIPELINE_STEPS = [
    ("load_data", "Loading data files"),
    ("tag",       "Tagging transactions"),
    ("clean",     "Cleaning data"),
    ("combine",   "Combining & matching Amazon orders"),
    ("label",     "Labeling transactions with OpenAI"),
    ("analyze",   "Analyzing results"),
]


# ----------------------------
# Helpers
# ----------------------------
def get_api_key_from_secrets() -> str:
    if "OPENAI_API_KEY" in st.secrets:
        return str(st.secrets["OPENAI_API_KEY"]).strip()
    return ""


def validate_api_key(key: str) -> tuple[bool, str]:
    key = (key or "").strip()
    if not key:
        return False, "Empty"
    if any(ch in key for ch in ["\n", "\r", "\t"]):
        return False, "Key contains newlines/tabs. Paste ONLY the key."
    try:
        key.encode("ascii")
    except UnicodeEncodeError:
        return False, "Key contains non-ASCII characters. Paste ONLY the OpenAI key."
    if not (key.startswith("sk-") or key.startswith("sess-") or key.startswith("rk-")):
        return False, "Key doesn't look like an OpenAI key (expected sk-... / sess-... / rk-...)."
    return True, "OK"


def set_api_key(key: str) -> None:
    key = (key or "").strip()
    ok, msg = validate_api_key(key)
    if ok:
        os.environ["OPENAI_API_KEY"] = key
    else:
        os.environ.pop("OPENAI_API_KEY", None)
        if key:
            st.error(f"Invalid API key: {msg}")


@st.cache_data(show_spinner=False)
def load_output_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def safe_load_pickle(path: Path):
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def load_matcher(path: Path):
    """Load the full Matcher object from pickle."""
    return safe_load_pickle(path)


def _count_amazon_orders(data):
    """Extract the number of Amazon order dates from pipeline data."""
    try:
        amzn = data.get("amzn") or data.get("prods")
        if amzn is not None and "date" in amzn.columns:
            return amzn["date"].nunique()
    except Exception:
        pass
    return None


def _count_combined_rows(data):
    """Extract the number of rows in the combined table."""
    try:
        combined = data.get("combined")
        if combined is not None:
            return len(combined)
    except Exception:
        pass
    return None


def run_pipeline_with_progress():
    """Run the pipeline step-by-step with Streamlit progress indicators."""
    from analysis.run.helpers import load_data, tag, clean, combine, label, analyze

    step_functions = {
        "load_data": load_data,
        "tag": tag,
        "clean": clean,
        "combine": combine,
        "label": label,
        "analyze": analyze,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_logs = []
    data = None
    total_steps = len(PIPELINE_STEPS)

    progress_bar = st.progress(0, text="Starting pipeline...")
    status_container = st.status("Running pipeline...", expanded=True)

    start = time.time()

    for i, (step_key, step_desc) in enumerate(PIPELINE_STEPS):
        progress_pct = i / total_steps
        progress_bar.progress(progress_pct, text=f"Step {i+1}/{total_steps}: {step_desc}")

        step_fn = step_functions[step_key]
        step_start = time.time()

        # Show context-aware detail for heavy steps
        if step_key == "combine":
            n_orders = _count_amazon_orders(data) if data else None
            detail = f" ({n_orders} Amazon orders)" if n_orders else ""
            status_container.write(f"⏳ **{step_desc}**{detail}...")
        elif step_key == "label":
            n_rows = _count_combined_rows(data) if data else None
            detail = f" ({n_rows} rows)" if n_rows else ""
            status_container.write(f"⏳ **{step_desc}**{detail}...")
        else:
            status_container.write(f"⏳ **{step_desc}**...")

        # Capture stdout; discard stderr (tqdm writes \r-based progress
        # to stderr which only captures the initial 0% line — misleading)
        buf = io.StringIO()
        devnull = open(os.devnull, "w")
        try:
            with redirect_stdout(buf), patch.object(sys, "stderr", devnull):
                if step_key == "load_data":
                    data = step_fn()
                elif step_key == "analyze":
                    step_fn(data)
                else:
                    data = step_fn(data)
        except Exception:
            progress_bar.progress(progress_pct, text=f"❌ Failed at: {step_desc}")
            status_container.update(label="Pipeline failed", state="error", expanded=True)
            raise
        finally:
            devnull.close()

        step_elapsed = time.time() - step_start
        step_logs = buf.getvalue()

        # Filter out tqdm progress bar lines that leak into stdout
        # (tqdm.auto falls back to stdout in non-interactive environments)
        if step_logs.strip():
            import re
            filtered_lines = []
            for line in step_logs.strip().split("\n"):
                # Skip lines that look like tqdm output: "description: XX%|..."
                # or lines with bar_format patterns like "n_fmt/total_fmt"
                if re.search(r'\d+%\|', line) or re.search(r'\d+/\d+\s*\[', line):
                    continue
                if line.strip():
                    filtered_lines.append(line)
            if filtered_lines:
                all_logs.append(f"--- {step_desc} ---\n" + "\n".join(filtered_lines))

        status_container.write(f"  ✅ **{step_desc}** — done ({step_elapsed:.1f}s)")

    elapsed = time.time() - start
    progress_bar.progress(1.0, text=f"✅ Pipeline complete ({elapsed:.1f}s)")
    status_container.update(label=f"Pipeline complete ({elapsed:.1f}s)", state="complete", expanded=False)

    logs = "\n".join(all_logs)
    return elapsed, logs


def run_chat_question(question: str):
    from analysis.inspect import Chat
    chat = Chat()
    buf = io.StringIO()
    with redirect_stdout(buf):
        ret = chat.msg(question)
    printed = buf.getvalue().strip()
    returned = ret.strip() if isinstance(ret, str) else ""
    return returned, printed


def clear_output_files():
    """Delete output files so students start from scratch."""
    deleted = []
    for path in [CSV_PATH, MATCHER_PATH]:
        if path.exists():
            try:
                path.unlink()
                deleted.append(path.name)
            except Exception:
                pass
    return deleted


# ----------------------------
# Chart builders (from CSV data)
# ----------------------------
def merge_small_groups(df: pd.DataFrame, group_col: str, amount_col: str, min_threshold: float) -> pd.DataFrame:
    """Merge groups below threshold into 'Other', matching pipeline logic."""
    totals = df.groupby(group_col)[amount_col].sum().reset_index()
    totals.loc[totals[amount_col] < min_threshold, group_col] = "Other"
    totals = totals.groupby(group_col)[amount_col].sum().reset_index()
    totals = totals.sort_values(amount_col, ascending=False)
    return totals


def build_spend_by_spender_chart(df: pd.DataFrame):
    """Pie chart: spending by spender."""
    if "spender" not in df.columns or "amount" not in df.columns:
        st.warning("Missing 'spender' or 'amount' column — cannot build chart.")
        return
    data = df.groupby("spender")["amount"].sum().reset_index()
    data = data.sort_values("amount", ascending=False)
    fig = px.pie(
        data,
        names="spender",
        values="amount",
        title="Spending by Spender",
        hole=0,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="label+percent+value",
        texttemplate="%{label}<br>%{percent}<br>$%{value:,.2f}",
    )
    fig.update_layout(showlegend=True, height=500)
    st.plotly_chart(fig, use_container_width=True)


def build_spend_by_category_chart(df: pd.DataFrame):
    """Pie chart: spending by category (small categories merged into Other)."""
    if "category" not in df.columns or "amount" not in df.columns:
        st.warning("Missing 'category' or 'amount' column — cannot build chart.")
        return
    data = merge_small_groups(df, "category", "amount", CATEGORY_MIN)
    fig = px.pie(
        data,
        names="category",
        values="amount",
        title="Spending by Category",
        hole=0,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="label+percent+value",
        texttemplate="%{label}<br>%{percent}<br>$%{value:,.2f}",
    )
    fig.update_layout(showlegend=True, height=500)
    st.plotly_chart(fig, use_container_width=True)


def build_spend_by_vendor_chart(df: pd.DataFrame):
    """Bar chart: spending by vendor (small vendors merged into Other)."""
    if "vendor" not in df.columns or "amount" not in df.columns:
        st.warning("Missing 'vendor' or 'amount' column — cannot build chart.")
        return
    data = merge_small_groups(df, "vendor", "amount", VENDOR_MIN)
    data = data.sort_values("amount", ascending=True)  # horizontal bar, ascending for readability
    fig = px.bar(
        data,
        x="amount",
        y="vendor",
        orientation="h",
        title="Spending by Vendor",
        labels={"amount": "Total Spending ($)", "vendor": "Vendor"},
    )
    fig.update_traces(
        texttemplate="$%{x:,.2f}",
        textposition="outside",
    )
    fig.update_layout(
        height=max(400, len(data) * 35),
        yaxis=dict(categoryorder="total ascending"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# Header / Top Bar
# ----------------------------
st.title("📊 Steward View — Streamlit Runner")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns([1.6, 1.2, 1.2, 1.0], vertical_alignment="center")

    # API key input
    with c1:
        secret_key = get_api_key_from_secrets()
        api_key_input = st.text_input(
            "OpenAI API Key (required to run pipeline)",
            value=secret_key,
            type="password",
            help="Paste your OpenAI API key (e.g., sk-...). Required to run the pipeline. "
                 "You can also set OPENAI_API_KEY in Streamlit Secrets.",
        )
        clear = st.button("Clear key", use_container_width=True)
        if clear:
            api_key_input = ""
            os.environ.pop("OPENAI_API_KEY", None)
            st.toast("Key cleared.", icon="✅")

        if api_key_input:
            ok, msg = validate_api_key(api_key_input)
            if ok:
                st.success("API key looks valid.")
            else:
                st.warning(msg)
        set_api_key(api_key_input)

    # Run button
    with c2:
        st.write("")
        st.write("")
        run_btn = st.button("▶️ Run analysis.run()", use_container_width=True)

    # File status
    with c3:
        st.write("**Outputs**")
        csv_exists = CSV_PATH.exists()
        matcher_exists = MATCHER_PATH.exists()
        st.caption(f"{'✅' if csv_exists else '⚠️'} labeled_data.csv")
        st.caption(f"{'✅' if matcher_exists else '⚠️'} matcher.pkl")

    # Refresh — clears output files and cache so students start over
    with c4:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh data", use_container_width=True):
            deleted = clear_output_files()
            st.cache_data.clear()
            if deleted:
                st.toast(f"Deleted: {', '.join(deleted)}. Cache cleared.", icon="🗑️")
            else:
                st.toast("No output files to delete. Cache cleared.", icon="✅")
        st.write("")


# ----------------------------
# Pipeline run
# ----------------------------
if "last_run_logs" not in st.session_state:
    st.session_state.last_run_logs = ""
if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = None

if run_btn:
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("An OpenAI API key is required to run the pipeline. Paste your key above.")
    else:
        try:
            elapsed, logs = run_pipeline_with_progress()
            st.session_state.last_run_logs = logs
            st.session_state.last_run_time = elapsed
            st.cache_data.clear()
            if logs.strip():
                with st.expander("📜 Console logs (latest run)", expanded=False):
                    st.text_area("Output", logs, height=260)
                    st.download_button(
                        "⬇️ Download logs",
                        data=logs.encode("utf-8"),
                        file_name="pipeline_logs.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
            else:
                st.info("No console output captured.")
        except Exception as e:
            st.error("Pipeline failed. See error below.")
            st.exception(e)
elif st.session_state.last_run_time is not None:
    st.caption(f"Last run: {st.session_state.last_run_time:.1f}s")


# ----------------------------
# Tabs
# ----------------------------
tab_charts, tab_stats, tab_data, tab_matcher, tab_qa = st.tabs(
    ["📊 Charts", "📈 Stats", "📄 Data Explorer", "🔗 Matcher", "💬 Q&A"]
)


# ----------------------------
# Tab: Charts
# ----------------------------
with tab_charts:
    st.subheader("Spending Charts")

    if not CSV_PATH.exists():
        st.info("No output CSV yet. Run the pipeline first to generate charts.")
    else:
        df = load_output_csv(str(CSV_PATH))

        # Cast amount to numeric
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        # Spender pie chart
        build_spend_by_spender_chart(df)

        st.divider()

        # Category and vendor side by side
        chart_left, chart_right = st.columns(2)
        with chart_left:
            build_spend_by_category_chart(df)
        with chart_right:
            build_spend_by_vendor_chart(df)


# ----------------------------
# Tab: Stats
# ----------------------------
with tab_stats:
    st.subheader("Financial Summary")

    if not CSV_PATH.exists():
        st.info("Run the pipeline first so the CSV exists.")
    else:
        df = load_output_csv(str(CSV_PATH))

        # Cast amount to numeric
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        # Time period
        if "date" in df.columns:
            start_date = df["date"].min()
            end_date = df["date"].max()
            st.caption(f"Time Period: {start_date} to {end_date}")

        st.divider()

        # Key metrics row
        k1, k2, k3 = st.columns(3)
        if "amount" in df.columns:
            total_spend = df["amount"].sum()
            k1.metric("Total Spending", f"${total_spend:,.2f}")
        k2.metric("Transactions", f"{len(df):,}")
        if "account" in df.columns:
            k3.metric("Accounts", f"{df['account'].nunique()}")

        st.divider()

        # Spending by account
        if "account" in df.columns and "amount" in df.columns:
            st.write("**Spending by Account**")
            account_totals = (
                df.groupby("account")["amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            account_totals.columns = ["Account", "Total Spending"]
            account_totals["Total Spending"] = account_totals["Total Spending"].apply(
                lambda x: f"${x:,.2f}"
            )
            st.dataframe(account_totals, use_container_width=True, hide_index=True)

        st.divider()

        # Spending by spender
        if "spender" in df.columns and "amount" in df.columns:
            st.write("**Spending by Spender**")
            spender_totals = (
                df.groupby("spender")["amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            spender_totals.columns = ["Spender", "Total Spending"]
            spender_totals["Total Spending"] = spender_totals["Total Spending"].apply(
                lambda x: f"${x:,.2f}"
            )
            st.dataframe(spender_totals, use_container_width=True, hide_index=True)

        st.divider()

        # Top categories
        if "category" in df.columns and "amount" in df.columns:
            st.write("**Top 10 Categories**")
            cat_totals = (
                df.groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            cat_totals.columns = ["Category", "Total Spending"]
            cat_totals["Total Spending"] = cat_totals["Total Spending"].apply(
                lambda x: f"${x:,.2f}"
            )
            st.dataframe(cat_totals, use_container_width=True, hide_index=True)

        st.divider()

        # Top vendors
        if "vendor" in df.columns and "amount" in df.columns:
            st.write("**Top 10 Vendors**")
            vendor_totals = (
                df.groupby("vendor")["amount"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            vendor_totals.columns = ["Vendor", "Total Spending"]
            vendor_totals["Total Spending"] = vendor_totals["Total Spending"].apply(
                lambda x: f"${x:,.2f}"
            )
            st.dataframe(vendor_totals, use_container_width=True, hide_index=True)


# ----------------------------
# Tab: Data Explorer
# ----------------------------
with tab_data:
    st.subheader("Output Dataset")

    if not CSV_PATH.exists():
        st.warning("No output CSV yet. Click **Run analysis.run()** above.")
    else:
        df = load_output_csv(str(CSV_PATH))

        with st.container(border=True):
            f1, f2, f3, f4 = st.columns([1.4, 1.4, 1.0, 1.0], vertical_alignment="center")

            with f1:
                cols_default = df.columns.tolist()[:12]
                cols = st.multiselect(
                    "Columns",
                    df.columns.tolist(),
                    default=cols_default,
                    help="Select which columns to display.",
                )
            with f2:
                search = st.text_input(
                    "Search (contains, any column)",
                    value="",
                    placeholder="e.g., Walmart, Visa, refund, etc.",
                )
            with f3:
                only_missing = st.checkbox("Only rows with any missing", value=False)
            with f4:
                row_limit = st.number_input(
                    "Row limit", min_value=50, max_value=20000, value=1000, step=50
                )

        view = df.copy()
        if only_missing:
            view = view[view.isna().any(axis=1)]
        if search.strip():
            s = search.strip().lower()
            mask = (
                view.astype(str)
                .apply(lambda r: r.str.lower().str.contains(s, na=False))
                .any(axis=1)
            )
            view = view[mask]
        if cols:
            view = view[cols]

        st.caption(
            f"Loaded: `{CSV_PATH}` · Rows: {len(df):,} · Showing: {min(len(view), int(row_limit)):,}"
        )
        st.dataframe(view.head(int(row_limit)), use_container_width=True, height=520)

        d1, d2 = st.columns([1, 1])
        with d1:
            st.download_button(
                "⬇️ Download full labeled_data.csv",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="labeled_data.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                "⬇️ Download filtered view",
                data=view.to_csv(index=False).encode("utf-8"),
                file_name="labeled_data_filtered.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ----------------------------
# Tab: Matcher
# ----------------------------
with tab_matcher:
    st.subheader("Amazon Order Matcher")
    st.caption(
        "The matcher reconciles Amazon product purchases (from order history) "
        "with bank charges (from credit card statements). It replaces vague "
        "\"AMAZON\" bank charges with itemized product-level records so the "
        "pipeline can classify spending by actual product category."
    )

    matcher_obj = load_matcher(MATCHER_PATH)
    if matcher_obj is None:
        st.info("No matcher data found (matcher.pkl missing or unreadable). Run the pipeline first.")
    else:
        # ---- Summary metrics ----
        counter = getattr(matcher_obj, "counter", None)
        pmts = getattr(matcher_obj, "pmts", None)
        prods = getattr(matcher_obj, "prods", None)

        if counter:
            st.write("**How it works**")
            st.markdown(
                "The matcher tries three strategies per Amazon order, in order:\n\n"
                "1. **match_all_products** — Does the total cost of all products in "
                "the order equal a single bank charge?\n"
                "2. **match_single_products** — Does any single product's cost match "
                "a bank charge?\n"
                "3. **match_product_combos** — Does any combination of products' costs "
                "match a bank charge?\n"
            )

            st.divider()

            # Top-line metrics
            m1, m2, m3, m4 = st.columns(4)
            total_reconciled = sum(counter.values())
            m1.metric("Charges Reconciled", f"{total_reconciled:,}")
            if pmts:
                n_filtered = len(getattr(pmts, "filtered", []))
                n_unmatched_pmts = len(getattr(pmts, "unmatched", []))
                m2.metric("Amazon Bank Charges", f"{n_filtered:,}")
                m3.metric("Unmatched Charges", f"{n_unmatched_pmts:,}")
            if prods:
                n_prods = len(getattr(prods, "original", []))
                m4.metric("Products in Order History", f"{n_prods:,}")

            st.divider()

            # Strategy breakdown
            st.write("**Reconciliation by Strategy**")
            cdf = pd.DataFrame(
                {"Strategy": list(counter.keys()), "Charges Reconciled": list(counter.values())}
            )
            # Make strategy names more readable
            name_map = {
                "match_all_products": "Match All Products (whole order = one charge)",
                "match_single_products": "Match Single Products (one product = one charge)",
                "match_product_combos": "Match Product Combos (subset of products = one charge)",
            }
            cdf["Strategy"] = cdf["Strategy"].map(name_map).fillna(cdf["Strategy"])
            cdf = cdf.sort_values("Charges Reconciled", ascending=False)
            st.dataframe(cdf, use_container_width=True, hide_index=True)

        st.divider()

        # ---- Matched Products detail table ----
        st.write("**Matched Products (itemized)**")
        st.caption(
            "These are the individual Amazon product rows that successfully matched "
            "to bank charges and replaced them in the final dataset."
        )

        if prods is not None:
            prods_original = getattr(prods, "original", None)
            prods_matched_idx = getattr(prods, "matched", None)

            if prods_original is not None and prods_matched_idx is not None and len(prods_matched_idx) > 0:
                try:
                    matched_products = prods_original.loc[prods_matched_idx].copy()
                    # Select the most useful columns if they exist
                    display_cols = [c for c in ["date", "description", "amount", "quantity"] if c in matched_products.columns]
                    if not display_cols:
                        display_cols = matched_products.columns.tolist()
                    matched_display = matched_products[display_cols].copy()
                    if "amount" in matched_display.columns:
                        matched_display["amount"] = pd.to_numeric(matched_display["amount"], errors="coerce")
                        matched_display = matched_display.sort_values("amount", ascending=False)
                    st.dataframe(matched_display, use_container_width=True, height=400, hide_index=True)
                    st.caption(f"{len(matched_display):,} matched product rows")
                except Exception as e:
                    st.warning(f"Could not display matched products: {e}")
            else:
                st.info("No matched products found in the matcher data.")

            # ---- Unmatched Products ----
            prods_unmatched_idx = getattr(prods, "unmatched", None)
            if prods_original is not None and prods_unmatched_idx is not None and len(prods_unmatched_idx) > 0:
                st.divider()
                st.write("**Unmatched Products**")
                st.caption(
                    "These products from Amazon order history could not be matched "
                    "to any bank charge. This can happen when Amazon splits or "
                    "combines charges in unexpected ways."
                )
                try:
                    unmatched_products = prods_original.loc[prods_unmatched_idx].copy()
                    display_cols = [c for c in ["date", "description", "amount", "quantity"] if c in unmatched_products.columns]
                    if not display_cols:
                        display_cols = unmatched_products.columns.tolist()
                    unmatched_display = unmatched_products[display_cols].copy()
                    if "amount" in unmatched_display.columns:
                        unmatched_display["amount"] = pd.to_numeric(unmatched_display["amount"], errors="coerce")
                    st.dataframe(unmatched_display, use_container_width=True, height=300, hide_index=True)
                    st.caption(f"{len(unmatched_display):,} unmatched product rows")
                except Exception:
                    pass

        # ---- Unmatched Payments ----
        if pmts is not None:
            pmts_filtered = getattr(pmts, "filtered", None)
            pmts_unmatched_idx = getattr(pmts, "unmatched", None)
            if pmts_filtered is not None and pmts_unmatched_idx is not None and len(pmts_unmatched_idx) > 0:
                st.divider()
                st.write("**Unmatched Amazon Bank Charges**")
                st.caption(
                    "These are Amazon-related bank charges that could not be matched "
                    "to any product in the order history. They remain as-is in the "
                    "final dataset (labeled by the LLM instead)."
                )
                try:
                    unmatched_pmts = pmts_filtered.loc[pmts_unmatched_idx].copy()
                    display_cols = [c for c in ["date", "description", "amount"] if c in unmatched_pmts.columns]
                    if not display_cols:
                        display_cols = unmatched_pmts.columns.tolist()
                    unmatched_pmt_display = unmatched_pmts[display_cols].copy()
                    if "amount" in unmatched_pmt_display.columns:
                        unmatched_pmt_display["amount"] = pd.to_numeric(unmatched_pmt_display["amount"], errors="coerce")
                    st.dataframe(unmatched_pmt_display, use_container_width=True, height=300, hide_index=True)
                    st.caption(f"{len(unmatched_pmt_display):,} unmatched bank charges")
                except Exception:
                    pass


# ----------------------------
# Tab: Q&A
# ----------------------------
with tab_qa:
    st.subheader("Ask a Question (uses OpenAI)")
    st.caption(
        "This uses the repo's `analysis.inspect.Chat` to answer questions about the "
        "output CSV using an OpenAI model with Python execution."
    )

    q1, q2 = st.columns([1.4, 1.0], vertical_alignment="center")
    with q1:
        question = st.text_input(
            "Question about the output CSV",
            value="",
            placeholder="e.g., What's the most common merchant?",
        )
    with q2:
        st.write("")
        ask = st.button("💬 Ask", use_container_width=True)

    if ask:
        if not os.environ.get("OPENAI_API_KEY"):
            st.error(
                "An OpenAI API key is required. Add it in Secrets or paste a valid key above."
            )
        elif not CSV_PATH.exists():
            st.error("Run the pipeline first so the CSV exists.")
        elif not question.strip():
            st.error("Type a question first.")
        else:
            try:
                with st.spinner("Thinking…"):
                    returned, printed = run_chat_question(question.strip())

                if returned:
                    st.success(returned)
                elif printed:
                    st.success(printed)
                else:
                    st.warning("The Chat method did not return or print any text.")
            except Exception as e:
                st.error("Chat failed. See error below.")
                st.exception(e)
