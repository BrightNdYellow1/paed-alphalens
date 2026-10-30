"""PAED AlphaLens research workspace: transparent deterministic tools and optional AI."""
import json
import os
import streamlit as st
from alphalens.core import synthetic_case, investigate, report_json
from alphalens.agent import investigate_with_agent
from alphalens.fixed_income import Bond, risk_measures, rate_shock
from alphalens.portfolio import Holding, portfolio_scenario
from alphalens.benchmark import evaluate_timing_benchmark
from alphalens.theme import CSS
from alphalens.macro import macro_scenarios
from alphalens.paper_audit import audit_text

st.set_page_config(page_title="PAED AlphaLens | Research Evidence", page_icon="🔎", layout="wide")
st.markdown("<style>"+CSS+"</style>", unsafe_allow_html=True)
st.markdown("""<section class="al-hero">
<div class="al-eyebrow">Quantitative Research Intelligence</div>
<div class="al-hero-title">PAED AlphaLens</div>
<div class="al-hero-sub">Don't Just Trust the Signal. Test the Evidence.</div>
<span class="al-pill">Precision</span><span class="al-pill">Accuracy</span>
<span class="al-pill">Efficiency</span><span class="al-pill">Depth</span>
</section>""",unsafe_allow_html=True)
st.markdown('<div class="al-intro">A research validation workspace for investigating trading hypotheses, measuring risk and tracing conclusions to reproducible calculations.</div>',unsafe_allow_html=True)
view=st.radio("Explanation detail",["Explore | Plain language","Research | Mathematical detail"],
              horizontal=True, help="Change how results are explained. Both modes use the same deterministic calculations.")
research_mode=view.startswith("Research")
st.markdown('<div class="al-kicker">INVESTIGATE / TEST / EXPLAIN / REPRODUCE</div>',unsafe_allow_html=True)
with st.expander("How the evidence engine works", expanded=False):
    st.markdown("**1. Research claim** → **2. Approved numerical checks** → **3. Counterfactual** → **4. Evidence verdict** → **5. Export and reproduce**")
    st.caption("Mathematical tests execute in Python. When configured, NVIDIA Nemotron plans and explains selected checks. Language model output is not treated as independent proof.")
tabs=st.tabs(["01  Research Trial","02  Nemotron Investigator","03  Bond Risk","04  Portfolio Stress","05  Evidence Benchmark","06  Macro Scenarios","07  Claim Audit"])
with tabs[0]:
    st.markdown('<div class="al-kicker">01 / Strategy investigation</div>',unsafe_allow_html=True)
    st.header("The Strategy That Knew Tomorrow")
    st.write("Can a backtest look convincing because the strategy has access to information it could not have used in a real trade?")
    case=st.radio("Choose a controlled trial",["The Strategy That Knew Tomorrow","Clean timing control"],horizontal=True)
    cost=st.slider("Transaction cost per change in basis points",0.0,20.0,1.0,0.5)
    flawed=case.startswith("The Strategy")
    df=synthetic_case(flawed)
    if st.button("Run research trial",type="primary"):
        st.session_state["trial_result"] = None
        finding,chart=investigate(df,flawed,cost)
        st.session_state["trial_result"] = {"finding":finding,"chart":chart,"case":case,"cost":cost}
        a,b=st.columns(2)
        a.metric("Reported Sharpe",f"{finding.original_sharpe:.2f}")
        b.metric("Timing adjusted Sharpe",f"{finding.corrected_sharpe:.2f}")
        st.subheader("Research verdict")
        st.write(finding.validity)
        st.write(finding.explanation)
        st.line_chart(chart.rename(columns={"original":"Reported equity","corrected":"Adjusted equity"}))
        with st.expander("Inspect the information timeline"):
            timeline=df[["period","market_return","position"]].head(35).copy()
            timeline.columns=["Period","Market return","Strategy position"]
            st.dataframe(timeline,hide_index=True,width="stretch")
            st.caption("The future-aware case takes the sign of the current return as its current-period position. A realistic trade cannot rely on an outcome unknown at execution.")
        if research_mode:
            st.markdown('<div class="al-note"><b>Method</b><br>Sharpe estimates annualised return divided by observed return volatility with an assumed zero risk free rate. The counterfactual shifts the known flawed signal by one period.</div>',unsafe_allow_html=True)
        else:
            st.info("A strategy that knows a return before trading can appear exceptionally successful. The corrected comparison shows what changes when the timing assumption is enforced.")
        with st.expander("Show Me Why | Source fingerprint and evidence"):
            st.json(json.loads(report_json(finding)))
        st.download_button("Export reproducible evidence",report_json(finding),"research_trial.json","application/json")
    st.caption("This case is labelled in advance. The trial itself is not autonomous flaw discovery.")

with tabs[1]:
    st.markdown('<div class="al-kicker">02 / Bounded AI investigation</div>',unsafe_allow_html=True)
    st.header("Nemotron Investigator")
    st.write("NVIDIA Nemotron proposes approved numerical checks. Python executes the calculations and the model interprets the returned evidence.")
    st.markdown('<div class="al-warning"><b>Live inference is not yet independently verified.</b><br>Requires private Nebius API credentials and available usage balance. Never share or commit an API key.</div>',unsafe_allow_html=True)
    key=os.getenv("NEBIUS_API_KEY")
    try:
        key=key or st.secrets.get("NEBIUS_API_KEY")
    except Exception:
        pass
    question=st.text_input("Research question","Does this strategy show evidence of information timing bias?")
    ai_case=st.selectbox("Input case",["Known flawed synthetic case","Clean synthetic control"])
    ai_df=synthetic_case(ai_case.startswith("Known flawed"))
    st.caption("The model is not given the case label. The dataset remains deliberately synthetic.")
    if not key:
        st.info("Nemotron is not connected in this environment. The mathematical trials and benchmark remain available without an API key.")
    if st.button("Investigate with NVIDIA",type="primary",disabled=not bool(key)):
        with st.spinner("Selecting and executing research tests"):
            try:
                result=investigate_with_agent(ai_df,question,key=key)
                st.success("Nebius model request completed in this session")
                st.write(result["interpretation"])
                with st.expander("Approved tests and exact numerical evidence",expanded=True):
                    st.json(result["evidence"])
                st.download_button("Export AI investigation",json.dumps(result,indent=2),
                                   "nemotron_evidence.json","application/json")
            except Exception as e:
                st.error("Model investigation unsuccessful. Inspect model availability, credits and API configuration.")
                st.caption("For security, detailed API errors are not displayed publicly. Verify the model ID, API endpoint, available balance and private secret configuration.")

with tabs[2]:
    st.markdown('<div class="al-kicker">03 / Fixed income analytics</div>',unsafe_allow_html=True)
    st.header("Bond Risk Laboratory")
    st.write("What happens to the present value of a fixed coupon bond when market yields change?")
    a,b=st.columns(2)
    with a:
        face=st.number_input("Face value",min_value=1.0,value=1000.0,step=100.0)
        coupon=st.slider("Annual coupon (%)",0.0,15.0,4.0,0.25)
        years=st.slider("Years until maturity",1,40,5)
    with b:
        y=st.slider("Annual yield (%)",0.0,15.0,4.5,0.25)
        shock=st.slider("Yield shock (basis points)",-300,300,100,25)
    bond=Bond(face=face,coupon_rate=coupon/100,years=years,yield_rate=y/100)
    risk=risk_measures(bond)
    scenario=rate_shock(bond,shock)
    c1,c2,c3=st.columns(3)
    c1.metric("Model price",f"{risk['price']:,.2f}")
    c2.metric("Modified duration",f"{risk['modified_duration']:.2f}")
    c3.metric("Convexity",f"{risk['convexity']:.2f}")
    st.metric("After shock",f"{scenario['price_after']:,.2f}",f"{scenario['exact_change_pct']:+.2f}%")
    if research_mode:
        st.write("Duration estimates the first derivative of price sensitivity to yield. Convexity captures second order curvature.")
        st.write("Duration and convexity approximation (%)",round(scenario["duration_convexity_approx_pct"],3))
    else:
        st.info("Bond prices generally decrease as yields increase. Longer maturities usually mean greater exposure to interest rate changes.")
    with st.expander("Show Me Why | Pricing assumptions"):
        st.json({"risk":risk,"scenario":scenario})
    st.download_button("Export bond evidence",json.dumps({"risk":risk,"scenario":scenario},indent=2),"bond_evidence.json","application/json")
    st.caption("Illustrative fixed annual cashflows. No credit risk or live market data.")

with tabs[3]:
    st.markdown('<div class="al-kicker">04 / Portfolio sensitivity</div>',unsafe_allow_html=True)
    st.header("Portfolio Stress Test")
    st.write("Compare two bonds with different maturity exposures under the same hypothetical interest rate shock.")
    a,b=st.columns(2)
    with a:
        y1=st.slider("Bond A maturity",1,30,3)
        n1=st.number_input("Bond A units",1,1000,10)
    with b:
        y2=st.slider("Bond B maturity",1,30,10)
        n2=st.number_input("Bond B units",1,1000,5)
    base=st.slider("Starting portfolio yield (%)",0.0,15.0,4.5,0.25)
    dy=st.slider("Portfolio rate shock (basis points)",-300,300,100,25)
    result=portfolio_scenario([Holding(Bond(years=y1,yield_rate=base/100),n1),
                               Holding(Bond(years=y2,yield_rate=base/100),n2)],dy)
    a,b,c=st.columns(3)
    a.metric("Starting value",f"{result['value_before']:,.2f}")
    b.metric("Change",f"{result['change_pct']:+.2f}%")
    c.metric("Weighted duration",f"{result['weighted_modified_duration']:.2f}")
    st.dataframe(result["positions"],hide_index=True,width="stretch")
    if not research_mode:
        st.info("The longer duration bond usually has greater price sensitivity. Compare each holding's contribution to the portfolio result.")
    with st.expander("Show Me Why | Portfolio evidence"):
        st.json(result)
    st.download_button("Export portfolio evidence",json.dumps(result,indent=2),"portfolio_evidence.json","application/json")
    st.caption("Parallel hypothetical yield shock, without default, liquidity or execution cost modelling.")

with tabs[4]:
    st.markdown('<div class="al-kicker">05 / Reproducibility and evaluation</div>',unsafe_allow_html=True)
    st.header("Evidence Benchmark")
    st.write("Test the timing signature against intentionally flawed and clean synthetic constructions.")
    n=st.slider("Synthetic seeds",5,50,20,5)
    if st.button("Run evidence benchmark",type="primary"):
        st.session_state["benchmark_result"]=evaluate_timing_benchmark(range(n))
    if "benchmark_result" in st.session_state:
        results=st.session_state["benchmark_result"]
        a,b,c=st.columns(3)
        a.metric("Synthetic accuracy",f"{results['accuracy']:.1%}")
        b.metric("Precision",f"{results['precision']:.1%}" if results['precision'] is not None else "Undefined")
        c.metric("Recall",f"{results['recall']:.1%}" if results['recall'] is not None else "Undefined")
        st.markdown('<div class="al-warning"><b>Scope of measurement</b><br>This is not a truth percentage or a Nemotron benchmark, and it is not proof of performance on real historical markets. The synthetic cases share controlled patterns with the test rule.</div>',unsafe_allow_html=True)
        st.dataframe(results["rows"],hide_index=True,width="stretch")
        with st.expander("Confusion matrix | Exact counts"):
            st.json({k:results[k] for k in ["cases","true_positive","true_negative","false_positive","false_negative","false_positive_rate"]})
        st.download_button("Export benchmark evidence",json.dumps(results,indent=2),"synthetic_benchmark.json","application/json")
with tabs[5]:
    st.markdown('<div class="al-kicker">06 / Macroeconomic scenario engine</div>',unsafe_allow_html=True)
    st.header("Macro Scenario Laboratory")
    st.write("Explore transparent hypothetical shocks to inflation, policy rates and economic growth. These are scenarios, not forecasts.")
    m1,m2,m3=st.columns(3)
    with m1:
        inflation=st.number_input("Baseline inflation (%)",value=2.5,min_value=-10.0,max_value=30.0,step=0.25)
    with m2:
        policy=st.number_input("Baseline policy rate (%)",value=4.0,min_value=-10.0,max_value=30.0,step=0.25)
    with m3:
        growth=st.number_input("Baseline GDP growth (%)",value=1.5,min_value=-10.0,max_value=30.0,step=0.25)
    scenarios=macro_scenarios(inflation,policy,growth)
    st.dataframe(scenarios["scenarios"],hide_index=True,width="stretch")
    st.markdown('<div class="al-warning"><b>What this proves</b><br>Only the outputs of explicitly assumed shocks. The changes are not estimated with historical data and are not probabilistic forecasts.</div>',unsafe_allow_html=True)
    st.download_button("Export macro assumptions and scenarios",json.dumps(scenarios,indent=2),"macro_scenarios.json","application/json")
with tabs[6]:
    st.markdown('<div class="al-kicker">07 / Research claim extraction</div>',unsafe_allow_html=True)
    st.header("Research Claim Audit")
    st.write("Paste a passage from research you have rights to use. AlphaLens marks candidate financial claims for human verification; it does not certify their truth.")
    passage=st.text_area("Research passage",height=180,placeholder="Example: Our strategy achieved a Sharpe ratio of 2.1, with annual returns of 12%.")
    if st.button("Extract claims",type="primary"):
        try:
            st.session_state["claim_audit_result"]=audit_text(passage)
        except ValueError as e:
            st.session_state.pop("claim_audit_result",None)
            st.error(str(e))
    if "claim_audit_result" in st.session_state:
        try:
            audit=st.session_state["claim_audit_result"]
            st.metric("Candidate claims",len(audit["candidate_claims"]))
            if audit["candidate_claims"]:
                st.dataframe(audit["candidate_claims"],hide_index=True,width="stretch")
            else:
                st.info("No candidate financial claims detected by the keyword heuristic.")
            st.warning("All extracted claims remain UNVERIFIED. Source publication dates, datasets, code and statistical assumptions require separate checking.")
            with st.expander("Evidence fingerprint and limitations"):
                st.json({"source_sha256":audit["source_sha256"],"limitations":audit["limitations"]})
            st.download_button("Export claim audit",json.dumps(audit,indent=2),"claim_audit.json","application/json")
        except ValueError as e:
            st.error(str(e))
st.divider()
st.caption("PAED AlphaLens | Reproducible research prototype. Synthetic examples, not investment advice. Live AI investigation requires Nebius access.")
