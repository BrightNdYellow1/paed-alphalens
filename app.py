import json
import os
import streamlit as st
from alphalens.core import synthetic_case, investigate, report_json
from alphalens.agent import investigate_with_agent

st.set_page_config(page_title="PAED AlphaLens", page_icon="📈", layout="wide")
st.title("PAED AlphaLens")
st.caption("Precision · Accuracy · Efficiency · Depth")
st.subheader("Don't Just Trust the Signal. Test the Evidence.")
st.write("Investigate quantitative trading hypotheses with reproducible Python and NVIDIA Nemotron.")
case = st.radio("Select research trial", ["The Strategy That Knew Tomorrow", "Clean timing control"])
cost = st.slider("Trading cost in basis points", 0.0, 20.0, 1.0, 0.5)
df = synthetic_case(case.startswith("The Strategy"))
t1, t2 = st.tabs(["Research Trial", "Nemotron Investigator"])
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
