# PAED AlphaLens

**Precision · Accuracy · Efficiency · Depth**

*Don't Just Trust the Signal. Test the Evidence.*

## 01 — The Research Question

Why do apparently profitable trading strategies sometimes fail when tested rigorously?

## 02 — The Problem

Look-ahead bias, overfitting, data leakage and unrealistic market assumptions can make historical trading results look more convincing than they are.

## 03 — Our Approach

Reproducible mathematical investigation, statistical verification and, as the next development milestone, autonomous research using an NVIDIA open-source model served through Nebius.

## 04 — The Implementation

Python code, financial calculations, automated tests and measurable results. The current prototype uses a Streamlit interface and a **synthetic, pre-labelled** case of look-ahead bias with a clean timing control.

### Implemented

- Deterministic strategy-return, transaction-cost and Sharpe-ratio calculations.
- Correction of a deliberately future-aware synthetic signal by delaying it one period.
- Before-and-after equity curves and a downloadable JSON evidence report.
- Four unit tests and a GitHub Actions test workflow.

**Current limitation:** NVIDIA Nemotron/Nebius integration and autonomous detection of previously unknown research flaws are **not implemented yet**. The present demonstration knows which synthetic case has look-ahead bias. Simulated returns are not proof of actual investment performance.

## 05 — Evidence and Evaluation

What works, what fails, what remains uncertain and how the findings can be reproduced.

### Run locally

Python 3.11 or newer:

```bash
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

Passing these unit tests shows that specified code behaviours work; it does not establish accuracy on real market research. Future evaluation will use held-out clean and flawed cases, with precision, recall, false positives, and independently checked explanations.

## 06 — My Learning Journey

The financial mathematics, software engineering and quantitative research principles learned while developing AlphaLens.

- **Precision:** Distinguish information available before a trade from future information.
- **Accuracy:** Independently verify calculations rather than rely on a language model's unsupported claims.
- **Efficiency:** Prefer focused, repeatable tests over unnecessary computational complexity.
- **Depth:** Understand the statistical assumptions, market context, limitations and consequences of a research conclusion.

### Development roadmap

1. Integrate NVIDIA Nemotron through Nebius and validate actual inference requests.
2. Build an agent that selects authorised investigation tools and evaluates evidence without access to case labels.
3. Benchmark on independent clean and flawed research cases.
4. Expand reproducible evidence reports and deploy a public demonstration.

## Responsible Use and License

AlphaLens is an educational research prototype, not financial or investment advice. The project uses the MIT License; see [LICENSE](LICENSE).
