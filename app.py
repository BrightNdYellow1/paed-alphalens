import json
import os
import streamlit as st
from alphalens.core import synthetic_case, investigate, report_json
from alphalens.agent import investigate_with_agent
from alphalens.fixed_income import Bond, price, risk_measures, rate_shock

st.set_page_config(page_title="PAED AlphaLens", page_icon="📊", layout="wide")
st.title("PAED AlphaLens")
st.caption("Precision · Accuracy · Efficiency · Depth")
st.subheader("Don't Just Trust the Signal. Test the Evidence.")
st.write("Investigate quantitative trading hypotheses with reproducible Python and NVIDIA Nemotron.")
case = st.radio("Select research trial", ["The Strategy That Knew Tomorrow", "Clean timing control"])
cost = st.slider("Trading cost in basis points", 0.0, 20.0, 1.0, 0.5)
df = synthetic_case(case.startswith("The Strategy"))
t1, t2, t3 = st.tabs(["Research Trial", "Nemotron Investigator", "Bond Risk Laboratory"])
with t1:
    st.caption("Known labelled synthetic case. The result is not discovered autonomously.")
    if st.button("Run research trial"):
        finding, chart = investigate(df, case.startswith("The Strategy"), cost)
        a, b = st.columns(2)
        a.metric("Reported Sharpe", f"{finding.original_sharpe:.2f}")
        b.metric("Corrected Sharpe", f"{finding.corrected_sharpe:.2f}")
        st.write(finding.validity)
        st.write(finding.explanation)
        st.line_chart(chart)
        with st.expander("Show Me Why"):
            st.json(json.loads(report_json(finding)))
        st.download_button("Download evidence", report_json(finding), "evidence.json", "application/json")
with t2:
    st.write("Nebius Nemotron selects safe investigation tools, reviews numerical results and explains limitations.")
    api_key = os.getenv("NEBIUS_API_KEY")
    try:
        api_key = api_key or st.secrets.get("NEBIUS_API_KEY")
    except Exception:
        pass
    if not api_key:
        st.warning("Set NEBIUS_API_KEY privately to run a live Nemotron investigation.")
    question = st.text_input("Research question", "Does this strategy show evidence of information timing bias?")
    if st.button("Investigate with NVIDIA", disabled=not bool(api_key)):
        with st.spinner("Investigating evidence"):
            try:
                result = investigate_with_agent(df, question, cost, api_key)
                st.success("Live Nemotron investigation completed")
                st.write(result["interpretation"])
                st.json(result["evidence"])
                st.download_button("Download AI investigation", json.dumps(result, indent=2), "agent_report.json", "application/json")
            except Exception as exc:
                st.error("Nebius investigation failed. Check credits, model and API access.")
                st.code(str(exc))
st.caption("Synthetic data for educational research. Not investment advice.")

with t3:
    st.subheader("Bond Risk Laboratory")
    st.caption("Educational fixed coupon bond scenario analysis. No live market data or forecasts.")
    left, right = st.columns(2)
    with left:
        face = st.number_input("Face value", min_value=1.0, value=1000.0, step=100.0)
        coupon = st.slider("Annual coupon (%)", 0.0, 15.0, 4.0, 0.25)
        years = st.slider("Years to maturity", 1, 40, 5)
    with right:
        yield_pct = st.slider("Annual yield (%)", 0.0, 15.0, 4.5, 0.25)
        shock = st.slider("Interest rate shock (basis points)", -300, 300, 100, 25)
    bond = Bond(face=face, coupon_rate=coupon/100, years=years, yield_rate=yield_pct/100)
    measures = risk_measures(bond)
    scenario = rate_shock(bond, shock)
    a,b,c = st.columns(3)
    a.metric("Model bond price", f"{measures['price']:,.2f}")
    b.metric("Modified duration", f"{measures['modified_duration']:.2f}")
    c.metric("Convexity", f"{measures['convexity']:.2f}")
    st.metric("Bond price after yield shock", f"{scenario['price_after']:,.2f}",
              f"{scenario['exact_change_pct']:+.2f}%")
    st.write("Why this matters: bond prices generally move inversely to yields for fixed cashflows. Duration estimates first order sensitivity; convexity captures curvature.")
    with st.expander("Show Me Why: Model assumptions"):
        st.json({"bond": {"face":face,"coupon_rate":coupon/100,"years":years,"yield_rate":yield_pct/100},
                 "risk":measures,"scenario":scenario})
        st.caption("Annual coupons and parallel yield shock; excludes credit risk, liquidity, taxes and execution costs.")
    st.download_button("Download bond scenario evidence",
                       json.dumps({"risk":measures,"scenario":scenario},indent=2),
                       file_name="bond_scenario.json", mime="application/json")
