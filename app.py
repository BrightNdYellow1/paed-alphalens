import streamlit as st
from alphalens.core import synthetic_case,investigate,report_json
st.set_page_config(page_title="PAED AlphaLens",page_icon="🔬",layout="wide")
st.title("🔬 PAED AlphaLens")
st.caption("Precision · Accuracy · Efficiency · Depth")
st.info("Synthetic research prototype; the NVIDIA/Nebius agent is not integrated yet.")
case=st.radio("Choose a research trial",["The Strategy That Knew Tomorrow","Clean timing control"])
cost=st.slider("Transaction cost (basis points per change)",0.0,20.0,1.0,0.5)
if st.button("Investigate",type="primary"):
    contaminated=case.startswith("The Strategy")
    data=synthetic_case(contaminated)
    finding,chart=investigate(data,contaminated,cost)
    x,y=st.columns(2)
    x.metric("Original Sharpe",f"{finding.original_sharpe:.2f}")
    y.metric("Corrected Sharpe",f"{finding.corrected_sharpe:.2f}")
    st.subheader(finding.validity)
    st.write(finding.explanation)
    st.line_chart(chart)
    with st.expander("Show me why",expanded=True):
        st.code(report_json(finding),language="json")
        st.caption("The synthetic case label is preassigned, not detected autonomously.")
    st.download_button("Download evidence report",report_json(finding),"alphalens_evidence.json","application/json")
    st.download_button("Download synthetic data",data.to_csv(index=False),"synthetic_case.csv","text/csv")
