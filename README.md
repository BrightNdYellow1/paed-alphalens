# 🔬 PAED AlphaLens
**Precision · Accuracy · Efficiency · Depth**

**Don't Just Trust the Claim. Test the Evidence.**

A research validation prototype investigating whether seemingly successful trading backtests rely on information unavailable at the time of a trade.

## What's implemented
- Streamlit interface with synthetic demonstration and clean control.
- Deterministic calculations for strategy returns, transaction costs and Sharpe ratio.
- Future-aware signal correction and side-by-side comparison.
- Downloadable JSON evidence report, tests and reproducible sample data.

**Important:** NVIDIA Nemotron/Nebius integration and autonomous flaw discovery are **not implemented yet**. Cases have known synthetic labels, and example performance is not evidence of a profitable trading strategy.

## Run locally
Python 3.11+:
```bash
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

## Learning journey
**Precision:** distinguish decision-time information from hindsight.
**Accuracy:** reproduce calculations independently.
**Efficiency:** run focused experiments.
**Depth:** explain statistical assumptions, limitations and risk.

## Next goals
Integrate NVIDIA open-source Nemotron inference on Nebius; develop agent-directed tool selection; benchmark clean and flawed cases; deploy live; produce a public demonstration.

Educational research only; not financial advice. Licensed MIT.
