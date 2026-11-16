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

## Batch evidence pipeline

The batch runner lands the original CSV, validates the schema and values, and
reuses the Research Trial calculation to produce curated period-level data and
a JSON evidence report. Each batch is keyed by schema version, case label and
source SHA-256. A retry targets the same paths. The manifest lists row count
and output checksums and is written after the curated outputs. A failed
validation leaves the raw input available for inspection.

Run a local batch:

```bash
python -m alphalens.pipeline --synthetic --case future-aware --output /tmp/alphalens-evidence
```

Run against an existing Azure Storage account and private container:

```bash
pip install -r requirements-azure.txt
az login
python -m alphalens.pipeline --synthetic --case future-aware \
  --azure-account-url https://YOUR_ACCOUNT.blob.core.windows.net --container alphalens
```

Grant the executing identity Storage Blob Data Contributor on the target
container. In an Azure-hosted job, configure a managed identity and assign it
the same container-scoped role. Use a serial runner per batch key. To replace
the synthetic generator, pass `--input file.csv` with columns
`period,market_return,position`; the case label describes the known construction
and is supplied by the operator. Use synthetic or appropriately licensed research
data for the portfolio demonstration.

Azure deployment and cloud scheduling require an Azure environment. The batch
runner does not provision infrastructure or schedule itself.

### Failure and recovery verification

A local filesystem run verified a 420-row synthetic batch and checked each
published artifact against its manifest checksum. A separate three-row input
with duplicate period IDs was rejected with `Invalid data order or missing entries`.
Only the original raw CSV was retained for that batch. Correcting the duplicate
period ID and reprocessing created a new batch with a different source hash,
three validated rows and matching output checksums. This was a deliberate
failure drill, not a production incident.

To repeat the drill against an existing Azure Blob Storage container, run this
from the repository root with an Azure CLI session that has Storage Blob Data
Contributor access scoped to the container:

```bash
python -m pip install -r requirements-azure.txt
python -m scripts.verify_blob_pipeline \
  --azure-account-url https://YOUR_ACCOUNT.blob.core.windows.net \
  --container alphalens | tee azure-verification.json
```

The verifier uploads synthetic inputs into a unique verification prefix,
downloads artifacts to compare their hashes, checks that the rejected batch
contains only the unchanged raw input, and verifies the corrected batch.
The commands require an existing account and container. Live Azure results
have yet to be recorded.

### Queryable research catalog

Add `--catalog catalog.db` to either pipeline command to record execution
attempts and load successful batches into SQLite. The catalog distinguishes
a **batch**, keyed by version, case and input SHA-256, from a **run**, which
records one execution attempt with its own start time, end time and status.
The observation primary key is `(batch_id, period)`. Batch and observation
inserts share a transaction. A repeat run records a new attempt without
duplicating the already loaded observations.

Run the synthetic drill from the repository root:

```bash
python -m scripts.catalog_drill
```

The drill deliberately runs the future-aware case twice, the clean case
once, and a CSV with a duplicate period once. It verifies three completed
attempts, one rejection, two unique batches, and 840 observations. It writes
the SQLite catalog and summary under `catalog-evidence/`. The GitHub Actions
workflow collects the same evidence and logs. Its Monday 08:23 UTC schedule
takes effect when the workflow is on the default branch. The scheduled drill
uses synthetic data and local job storage; the separate Azure verification
command is required to evidence a live Blob Storage run.

Example queries for an analyst:

```sql
-- Join period-level equity curves to the dataset that produced them.
SELECT b.case_label, o.period, o.original_equity, o.corrected_equity
FROM batches AS b JOIN observations AS o USING (batch_id)
WHERE o.period < 5 ORDER BY b.case_label, o.period;

-- Compare the labelled backtests and retain their input lineage.
SELECT case_label, source_sha256, row_count, original_sharpe,
       corrected_sharpe, original_sharpe - corrected_sharpe AS sharpe_gap
FROM batches ORDER BY case_label;

-- Triage attempts that did not complete.
SELECT run_id, batch_id, status, started_at, ended_at, error_type, error_message
FROM runs WHERE status <> 'completed' ORDER BY run_id DESC;
```

A `rejected` attempt failed input validation. Inspect the preserved raw CSV,
correct it upstream and resubmit. A `failed` attempt indicates an operational
error. For a storage permission failure, check the executing identity, account,
container and data role before retrying the same bytes. An abruptly interrupted
process can leave a `running` attempt. Check the runner before retrying. The
object-store manifest and the SQLite transaction are separate publication
steps; if catalog loading fails after publication, the retained manifest can
be checked and the original batch rerun to repair the catalog.

The public workflow uses synthetic data and uploads only its test artifacts.
Use an authenticated Azure identity with container-level access for Blob
Storage. If adapting this pattern for NHS data, keep identifiable records and
artifacts within the approved environment, restrict access by role, and agree
retention, audit logging and access controls with information governance.

## SQL Server warehouse lab

The [SQL Server lab](sql-server-lab/README.md) adds a T-SQL warehouse load,
data-quality drill, reporting view and backup/restore reconciliation using
the existing synthetic AlphaLens results. It includes separate Windows
exercises for SSIS, SSRS and SSAS.

## Synthetic health-data research example

The [vaccination evidence lab](sde-lab/README.md) demonstrates how source
definitions, review status and provenance affect interpretation of a linked
dataset. It is separate from the quantitative research workflows.
