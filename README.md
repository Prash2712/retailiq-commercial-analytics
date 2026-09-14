# RetailIQ — Commercial Analytics & Executive BI Platform

[![CI](https://github.com/Prash2712/retailiq-commercial-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Prash2712/retailiq-commercial-analytics/actions/workflows/ci.yml)
[![Full data audit](https://github.com/Prash2712/retailiq-commercial-analytics/actions/workflows/full-data-audit.yml/badge.svg)](https://github.com/Prash2712/retailiq-commercial-analytics/actions/workflows/full-data-audit.yml)

RetailIQ is an end-to-end commercial analytics and BI engineering project built on **1,067,371 real UK retail transaction lines** from the UCI Online Retail II dataset. It demonstrates the complete path from a messy operational source to reconciled PostgreSQL analytics, governed business metrics and a source-controlled Power BI semantic/report design layer.

> **Current status:** data ingestion, quality controls, PostgreSQL star schema, commercial marts, automated full-source reconciliation and Power BI semantic-model source are implemented. The remaining desktop-only step is to render, refresh and visually validate the PBIP/PBIX report in Power BI Desktop before publishing screenshots.

## 60-second review

| Area | Evidence in this repository |
|---|---|
| Python | Official-source ingestion, SHA-256 provenance, schema validation, type normalisation, Parquet hand-off and quality profiling |
| SQL | PostgreSQL staging, dimensional model, row-preserving fact table, cohort/RFM/product/country marts and reconciliation gates |
| Power BI | Source-controlled TMDL semantic model, governed DAX catalogue, five-page report specification and report theme |
| Data quality | 34,335 repeated business rows flagged; missing identities/descriptions and non-positive values surfaced rather than silently removed |
| Testing / CI | Ruff, Pytest, PostgreSQL integration tests, BI contract checks and a complete 1.07m-row audit workflow |
| Business analysis | Verified commercial results, KPI contract, executive insight memo and explicit analytical limitations |

## Verified full-source results

These values come from the automated Full data audit workflow, not from manually typed dashboard totals.

| Metric | Verified value |
|---|---:|
| Transaction lines | **1,067,371** |
| Gross sales value | **£20,972,594.5680** |
| Cancellation value | **£1,527,415.0000** |
| Net sales value | **£19,445,179.5680** |
| Sale orders | **40,077** |
| Net sales per sale order | **£485.20** |
| Known purchasing customers | **5,878** |
| Repeat customers | **4,255** |
| Repeat-customer rate | **72.39%** |
| Products | **5,304** |
| Countries | **43** |
| Repeated exact business rows | **34,335** |
| Missing customer-ID rows | **243,007** |

### Reconciliation result

```text
staging rows:       1,067,371
fact rows:          1,067,371
row difference:             0

staging line value: £19,287,250.5680
fact line value:    £19,287,250.5680
value difference:          £0.0000
```

The warehouse build fails if row-count or line-value reconciliation is non-zero.

Full evidence and interpretation guardrails are in [`docs/verified_results.md`](docs/verified_results.md).

## Business question

A commercial team needs a trusted answer to five recurring questions:

1. How are net sales, order volume and average order value changing over time?
2. Which identifiable customers return, and how does retention differ by cohort?
3. Which products and countries drive commercial concentration?
4. Where is cancellation exposure material?
5. Which source-quality conditions could change the interpretation of management reporting?

RetailIQ builds the analytical system required to answer those questions rather than beginning with a dashboard and working backwards.

## Architecture

```text
UCI Online Retail II
        |
        v
Python ingestion
(download + SHA-256 provenance)
        |
        +------------------> immutable raw source (gitignored)
        |
        v
Typed normalised Parquet
(row-preserving + source lineage)
        |
        v
Data-quality profiling
        |
        v
PostgreSQL staging
        |
        v
Date / Customer / Product / Geography dimensions
        |
        v
Transaction-line fact (1,067,371 rows)
        |
        +--> commercial marts
        |     - daily performance
        |     - customer summary / RFM
        |     - cohort retention
        |     - product / country performance
        |     - data quality / reconciliation
        |
        v
Power BI TMDL semantic model
        |
        v
Governed DAX + five-page executive report design
```

See [`docs/architecture.md`](docs/architecture.md) and [`docs/warehouse_model.md`](docs/warehouse_model.md) for the modelling rationale.

## Data source and boundaries

**Online Retail II**, donated by Daqing Chen to the UCI Machine Learning Repository.

- Period: 1 December 2009 to 9 December 2011
- Business: UK-based registered non-store retailer
- Fields: invoice, product, quantity, date/time, unit price, customer and country
- DOI: `10.24432/C5CG6D`
- Licence: CC BY 4.0

The source contains selling prices but **no product cost data**. RetailIQ therefore does not invent profit, gross-margin, CAC, marketing ROI or CLV assumptions that the source cannot support.

## Important quality findings

The automated profile found:

- **34,335** repeated business rows (3.22% of source rows)
- **243,007** rows with no customer ID (22.77%)
- **4,382** missing descriptions
- **22,950** non-positive quantity rows
- **6,207** non-positive unit-price rows
- **19,494** cancellation rows

Repeated business rows are flagged but preserved. The dataset does not contain enough evidence to assume that every repeated line is an erroneous duplicate. Customer-level analytics explicitly use the identifiable-customer population rather than pretending anonymous transactions belong to known customer journeys.

## Commercial interpretation

The verified full-source profile shows:

- cancellation value is **7.28% of gross sales value** under the documented classification rules;
- net sales retain **92.72% of gross sales value** after cancellation treatment;
- **72.39%** of identifiable purchasing customers place at least two valid sale orders;
- customer analysis has a material identity-coverage limitation because 22.77% of source rows have no customer ID.

The evidence-led management interpretation is maintained in [`docs/executive_insight_memo.md`](docs/executive_insight_memo.md).

## Quick start

### Requirements

- Python 3.11+
- Docker / Docker Compose
- Git
- Power BI Desktop on Windows only for the final report-rendering step

### Install

```bash
git clone https://github.com/Prash2712/retailiq-commercial-analytics.git
cd retailiq-commercial-analytics
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Run code and BI contract checks

```bash
make lint
make test
make bi-validate
```

### Build the data platform

```bash
make ingest
make profile
make db-up
make warehouse-build
make reconcile
```

The raw source and generated data are gitignored.

### Build the Power BI model

Follow [`powerbi/README.md`](powerbi/README.md). The repo provides the TMDL semantic model, governed DAX catalogue, theme and detailed five-page report specification.

## Repository structure

```text
.
├── .github/workflows/
│   ├── ci.yml                         # lint, BI contract and integration tests
│   └── full-data-audit.yml            # complete UCI -> warehouse audit
├── data/                               # generated data; raw/interim/processed gitignored
├── docs/
│   ├── architecture.md
│   ├── data_contract.md
│   ├── warehouse_model.md
│   ├── kpi_dictionary.md
│   ├── verified_results.md
│   └── executive_insight_memo.md
├── powerbi/
│   ├── tmdl/retailiq-model.tmdl       # semantic-model source
│   ├── dax/measure-catalogue.md        # governed measures
│   ├── report/report-spec.md           # page/visual/interaction contract
│   ├── theme/retailiq-theme.json
│   └── README.md
├── scripts/
│   ├── print_verified_metrics.py
│   └── validate_bi_assets.py
├── sql/
│   ├── ddl/
│   ├── models/
│   └── marts/
├── src/retailiq/
├── tests/
├── compose.yaml
├── Makefile
└── pyproject.toml
```

## Metric governance

Business definitions are version controlled. Headline measures include:

- gross sales value
- cancellation value
- net sales value
- sale orders
- **average order value = net sales / sale orders**
- units sold
- known customers
- repeat-customer rate
- cohort retention
- RFM measures
- product concentration
- cancellation exposure

The same AOV rule is enforced in the SQL mart, TMDL/DAX model, documentation and integration test.

See [`docs/kpi_dictionary.md`](docs/kpi_dictionary.md) and [`powerbi/dax/measure-catalogue.md`](powerbi/dax/measure-catalogue.md).

## Testing strategy

### Unit tests

Validate schema mapping, cancellation flags, customer-ID handling and quality profiling.

### PostgreSQL integration test

A synthetic dataset is loaded through the same Parquet -> PostgreSQL path used by the project. CI then builds dimensions, fact and marts and verifies:

- source/fact row reconciliation;
- source/fact line-value reconciliation;
- gross/cancellation/net sales outputs;
- repeated-row handling;
- customer-mart population;
- governed net-sales AOV.

### BI contract test

`python scripts/validate_bi_assets.py` checks:

- report-theme JSON validity;
- required report pages;
- required governed measures;
- SQL/DAX AOV agreement;
- verified-result evidence markers;
- absence of embedded database passwords/DSNs in TMDL.

### Full-data audit

The separate full-data workflow downloads the official UCI dataset and executes the complete 1.07m-row pipeline. Portfolio claims are promoted only after this workflow succeeds.

## Power BI delivery boundary

The repository deliberately does **not** claim that a rendered `.pbix` has been validated by CI. Power BI Desktop is a Windows application and the GitHub Actions runner used here is Linux. Instead, the model and report logic are stored as reviewable text assets following the current PBIP/TMDL developer workflow. A final rendered PBIP/PBIX and genuine dashboard screenshots should be committed only after Power BI Desktop opens, refreshes and visually validates the report.

## Delivery roadmap

- [x] Project charter and source selection
- [x] Reproducible official-source ingestion
- [x] Source provenance and data contract
- [x] Data-quality profiling and tests
- [x] PostgreSQL staging layer
- [x] Dimensional/star schema
- [x] Reconciliation gates and commercial marts
- [x] Cohort retention and RFM marts
- [x] Full 1.07m-row automated audit
- [x] Verified-results evidence pack
- [x] Power BI TMDL semantic-model source
- [x] Governed DAX measure catalogue
- [x] Five-page executive report specification
- [x] BI source-asset CI contract
- [ ] Open/refresh the model in Power BI Desktop
- [ ] Build and visually QA the five report pages
- [ ] Commit genuine PBIP/PBIR output and report screenshots
- [ ] Tag portfolio release `v1.0.0`

## Project standards

1. **No fabricated impact.** Results and CV claims must be reproducible from committed code and documented evidence.
2. **No hidden cleaning.** Exclusion logic must be named, reviewable and reconciled.
3. **No metric theatre.** Metrics unsupported by the source are not invented.
4. **No notebook-only delivery.** Core workflow is runnable, tested and documented outside exploratory notebooks.
5. **No fake screenshots.** Portfolio images must come from the genuinely refreshed report.

## Attribution

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. DOI: `10.24432/C5CG6D`. Licensed under CC BY 4.0.

## Licence

Project code and documentation are released under the MIT Licence. Dataset usage remains subject to the source dataset's CC BY 4.0 terms.
