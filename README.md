# Steward View — A Python Demo for Finance Professionals

This is a teaching repository that demonstrates how Python solves real-world finance problems that Excel cannot.

Using a single Jupyter notebook as its entry point, the program ingests raw household transactions of a fictional couple (“Jack & Jill”), cleans and enriches them, produces summary statistics and charts, and writes one consolidated CSV. It also lets users investigate the result conversationally with an OpenAI model equipped with the Code Interpreter (Python) tool.

---

## Who is this for?

This repo is for finance professionals and students who want a clear, hands-on example of Python’s value beyond spreadsheets.

---

## What does it do?

Run the top-level `run()` function to execute the full pipeline:

1. **Load** raw data.
2. **Tag** sources.
3. **Clean** data.
4. **Combine** separate sources into one table with:
   - A **custom matching algorithm** that reconciles irregularly billed Amazon product purchases with the corresponding credit-card charges — enabling precise categorization of otherwise generic “AMZN” expenses. This operation is **not replicable in Excel**.
5. **Label** transactions with:
   - **Vendor and category inference** from bank statement descriptions using the OpenAI API. This program issues hundreds of calls **asynchronously with `asyncio`** for speed.

**Outputs**

- **Statistics:** Total spending and spending by account
- **Charts:** Spending by spender, category, and vendor
- **CSV:** One fully tagged / cleaned / combined / labeled dataset for downstream analysis

After the pipeline runs, users can **chat with the data** (inside the notebook) using an OpenAI model (itself equipped with Python) to answer ad hoc analytical questions.

---

## Why Python (vs. Excel)?

Python is uniquely useful for enhancing and automating data analysis. This repo demonstrates the following advantages:

- **Automation:** Repeatably execute a complex workflow in one call (`run()`)
- **Custom Logic:** Solve a difficult matching problem with a purpose-built algorithm that spreadsheets cannot replicate
- **Low-Level Control of AI**: Deploy LLMs with precision for reliable results tailored to your needs
- **Speed:** Process hundreds of API calls in parallel with `asyncio`
- **Quality:** Iterate using robust GitHub version control and flag problems with automatic testing
- **Modularity:** Combine bite-sized components into infinitely complex (and capable) systems

For a thorough comparison of Python and its alternatives, see the results of our research in [this 14-minute video on our YouTube channel](https://www.youtube.com/watch?v=ZrdV9xvTDBk).

---

## Repository layout

```
data/                 # sample Jack & Jill inputs and program outputs
notebooks/
  demo.ipynb          # start here
src/
  analysis/
    config/           # settings (e.g. model choice)
    inspect/          # chat interface & helpers for notebook analysis
    run/              # the data processing pipeline
    utilities/        # small, focused helpers
tests/                # automated tests
```

The codebase is composed of many small, minimally complex files to make each piece approachable for non-programmers.

---

## Quick start

### 1) Configure your OpenAI API key
To run the program yourself, you will need to:
1. Create a free OpenAI developer account by visiting [OpenAI's developer site](platform.openai.com),
2. Add your payment information to your OpenAI account by going to Your profile > Billing,
3. Get an OpenAI API key by going to Your profile > API keys, and
4. Bind your key to a GitHub secret environment variable named **OPENAI_API_KEY** by logging into GitHub and going to Settings > Codespaces > Secrets.

Running the whole program once (including asking one chat question) with GPT 5 Mini (the default model) costs about $0.03. Loading $5.00 onto your OpenAI developer account will give you more than enough credit to explore this repo.

### 2) Install the program

Install the program by opening `notebooks/demo.ipynb` and executing the first code cell:
```bash
pip install ..
```

### 3) Run the pipeline in the notebook

To run the data processing pipeline, execute:

```python
import analysis

analysis.run()  # Loads, tags, cleans, combines, labels, prints stats, shows charts, and writes a CSV
```

The function prints summary stats, renders charts, and writes one consolidated CSV containing the processed dataset (which the chat tool uses to answer questions).

---

## Conversational analysis (after `run()`)

The Chat object allows you to ask questions of the CSV with an OpenAI model that can execute Python against the file. Each Chat instance represents one continuous conversation.

```python
from analysis.inspect import Chat

chat = Chat()  # Uses the pipeline’s CSV output
chat.msg("What is the combined spending in the top three categories?")
chat.msg("How about the top five?")
```

To change the model, adjust the configuration (see next section).

---

## Configuration

In `src/analysis/config/`, you can find program settings such as:
- LLM model selection
- LLM instructions
- Expense categories
- Chart modifiers

---

## Inspecting the Amazon matcher (optional)

The `analysis.inspect` module includes the `load_matcher()` function for reviewing the Amazon reconciliation. This function loads the `Matcher` instance output by the `run()` function. This `Matcher` instance has a `counter` attribute that records the activity of the matching algorithm:

```python
from analysis.inspect import load_matcher

matcher = load_matcher()
matcher.counter  # A record of the number of charges reconciled with each matching rule
```

This is an educational aid for understanding the custom algorithm.

---

## Cost, privacy, and performance

- **API cost:** Labeling uses hundreds of OpenAI API calls. Changing the model will change the cost of running the program. You may want to review [OpenAI's pricing page](https://openai.com/api/pricing/) before adjusting this setting.
- **Privacy:** This program only sends the fields necessary for labeling to the OpenAI API. The included dataset is fictional.
- **Speed:** The pipeline uses `asyncio` to issue requests concurrently. If you hit rate limits, wait a minute before running the program again.

---

## License

PyFi students may use the contents of this repository for private, personal projects but may not publicly redistribute any part of this repository (or derivatives) or use any part of this repository for commercial projects. For full license details, see this repository's `LICENCE.txt`.
