import os
import io
import time
import pickle
from pathlib import Path
from contextlib import redirect_stdout

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


def load_matcher_counter(path: Path):
    matcher = safe_load_pickle(path)
    if matcher is None:
        return None
    return getattr(matcher, "counter", None)


def run_pipeline():
    import analysis
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    start = time.time()
    with redirect_stdout(buf):
        analysis.run()
    elapsed = time.time() - start
    logs = buf.getvalue()
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

    # Refresh
    with c4:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.toast("Cache cleared. Data will reload.", icon="✅")
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
        with st.spinner("Running pipeline…"):
            try:
                elapsed, logs = run_pipeline()
                st.session_state.last_run_logs = logs
                st.session_state.last_run_time = elapsed
                st.cache_data.clear()
                st.success(f"Pipeline completed in {elapsed:.1f}s")
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
    st.subheader("Amazon Matcher Results")
    st.caption(
        "The matching algorithm reconciles Amazon product purchases with "
        "credit-card charges. This table shows how many charges each rule resolved."
    )

    counter = load_matcher_counter(MATCHER_PATH)
    if counter is None:
        st.info("No matcher data found (matcher.pkl missing or unreadable). Run the pipeline first.")
    else:
        try:
            cdf = pd.DataFrame(
                {"Rule": list(counter.keys()), "Charges Reconciled": list(counter.values())}
            )
            cdf = cdf.sort_values("Charges Reconciled", ascending=False)

            total_reconciled = cdf["Charges Reconciled"].sum()
            st.metric("Total Charges Reconciled", f"{total_reconciled:,}")

            st.dataframe(cdf, use_container_width=True, height=360, hide_index=True)
        except Exception:
            st.write(counter)


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
