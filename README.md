# PAED AlphaLens

**Precision · Accuracy · Efficiency · Depth**

*Don't Just Trust the Signal. Test the Evidence.*

## 01: The Research Question

Why do apparently profitable trading strategies sometimes fail when tested rigorously?

## 02: The Problem

Look ahead bias, overfitting, data leakage and unrealistic market assumptions can make historical trading results look more convincing than they are.

## 03: Our Approach

Reproducible mathematical investigation, statistical verification and a prototype NVIDIA Nemotron investigation workflow through Nebius Token Factory. The live connection still requires an API key and successful runtime verification.

## 04: The Implementation

Python code, financial calculations, automated tests and measurable results. The current prototype uses a Streamlit interface and a **synthetic, labelled in advance** case of look ahead bias with a clean timing control.

### Implemented

* Deterministic strategy return, transaction cost and Sharpe ratio calculations.
* Correction of a deliberately future aware synthetic signal by delaying it one period.
* Before and after equity curves and a downloadable JSON evidence report.
* Automated unit tests covering financial calculations, agent safeguards, labelled synthetic evaluation and application structure.
* A two stage Nemotron workflow that proposes approved tests, runs deterministic Python diagnostics, and interprets their results when configured with a Nebius API key.

**Current limitation:** The agent integration code exists but a successful live Nebius inference request has not yet been verified. Autonomous discovery of previously unknown market flaws has not been validated. The present demonstration knows which synthetic case has look ahead bias. Simulated returns are not proof of actual investment performance.

## 05: Evidence and Evaluation

What works, what fails, what remains uncertain and how the findings can be reproduced.

### Research modules

* **Research Trial:** reproducible look ahead example and timing corrected Sharpe comparison.
* **Nemotron Investigator:** two stage model planning and interpretation separated by allowlisted Python tools. Requires live API configuration; the public demo must not claim verified AI inference until tested.
* **Bond Risk:** fixed coupon annual cashflow price, duration, convexity and yield stress.
* **Portfolio Stress:** two holding demonstration of deterministic parallel yield shocks.
* **Evidence Benchmark:** labelled synthetic cases and accuracy, precision, recall, false positive counts; not a real market or LLM benchmark.
* **Macro Scenarios:** explicit inflation, policy rate and growth shocks; not empirical forecasts.
* **Research Claim Audit:** keyword extraction from user pasted text; every claim remains UNVERIFIED and source is fingerprinted.

### Run locally

Python 3.11 or newer:

```bash
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

Passing these unit tests shows that specified code behaviours work; it does not establish accuracy on real market research. The 40-case sample benchmark with 20 positive and 20 negative deliberately constructed examples produced 100% synthetic accuracy, precision and recall. Because the classifier signature closely matches the data construction, this is a software baseline, not a credible estimate of real-world predictive accuracy. Future evaluation requires independent challenge sets, manual ground truth and separate measures for model explanation faithfulness.

## 06: My Learning Journey

The financial mathematics, software engineering and quantitative research principles learned while developing AlphaLens.

* **Precision:** Distinguish information available before a trade from future information.
* **Accuracy:** Independently verify calculations rather than rely on a language model's unsupported claims.
* **Efficiency:** Prefer focused, repeatable tests over unnecessary computational complexity.
* **Depth:** Understand the statistical assumptions, market context, limitations and consequences of a research conclusion.

### Development roadmap

1. Verify live NVIDIA Nemotron requests through Nebius using a private API key.
2. Evaluate the existing agent against independent, labelled test cases and verify explanations.
3. Benchmark on independent clean and flawed research cases.
4. Expand reproducible evidence reports and deploy a public demonstration.

## Responsible Use and License

AlphaLens is an educational research prototype, not financial or investment advice. The project uses the MIT License; see [LICENSE](LICENSE).

## Run the Nemotron investigator

The Streamlit app includes a **Nemotron Investigator** tab. Set `NEBIUS_API_KEY` as a Codespaces secret or host secret; never commit credentials. The default configured model is `nvidia/nemotron-3-super-120b-a12b`, with the Nebius US Central endpoint. Confirm your account has access to the selected model and available credits. An API call may incur usage charges.

On a Codespace, pull the latest changes, install dependencies, and run `python -m streamlit run app.py`. Select **Nemotron Investigator** and click **Investigate with NVIDIA**. It requires live API access. The numeric tools do not execute code generated by the language model.

The current time alignment audit is a synthetic diagnostic based on statistical alignment, **not proof of information leakage** without verified publication and trade timestamps.

## Competition submission checklist

1. Confirm green CI for the latest main-branch commit.
2. Verify a successful **live** Nebius API response using an available NVIDIA Nemotron model. Record model identifier and timestamp; verify Token Factory endpoint and account quota independently. Never expose an API key in commits or demo recordings.
3. Deploy **app.py** from the public repository to Streamlit Community Cloud, adding the NEBIUS_API_KEY secret in the host settings. Check the public app in an incognito window.
4. Capture a short, real run of the research trial and the model-guided investigation, showing the tool trace, counterfactual, confidence limitations and downloadable evidence.
5. Record a public demo video under three minutes, publish it, complete Devpost requirements, and verify the submitted URLs.

### Recommended three-minute demonstration

* **00:00–00:20** Research question: can we trust seemingly profitable strategy backtests?
* **00:20–01:05** Run the future-aware synthetic case; reveal reported and corrected Sharpe with charts.
* **01:05–01:45** Run live NVIDIA Nemotron investigation if the connection has been verified; show the approved tests, deterministic evidence and model's grounded explanation. Do not pretend an offline result is live AI.
* **01:45–02:15** Show the clean control and synthetic benchmark, with truthful scope limitations.
* **02:15–02:45** Demonstrate bond or portfolio rate risk and explain who benefits.
* **02:45–03:00** Highlight source traceability, responsible AI constraints and repeatable tests.

### Deployment

Use the repository's `app.py` as the main file and `requirements.txt` for dependency installation. Streamlit Community Cloud provides public hosting once an authorized account links this GitHub repository. The app works in deterministic mode without a Nebius API key; that **does not satisfy** the NVIDIA runtime integration requirement by itself.

### Release notes and constraints

No secure account system, persistent storage or verified real-market forecasts are claimed. The app is a bounded, reproducible educational quantitative research prototype. GitHub tests do not substitute for checking the public Streamlit interface and the live AI endpoint.
