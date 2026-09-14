# RetailIQ — Commercial Analytics & Executive BI Platform

[![CI](https://github.com/Prash2712/retailiq-commercial-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/Prash2712/retailiq-commercial-analytics/actions/workflows/ci.yml)

RetailIQ is an end-to-end commercial analytics project built on **1,067,371 real UK retail transaction lines** from the UCI Online Retail II dataset. It is designed to show the work behind a trustworthy management dashboard: source ingestion, data-quality controls, dimensional modelling, SQL business logic, customer analytics and Power BI reporting.

> **Project status:** Milestone 1 — reproducible data foundation. Warehouse, marts and BI layers are the next milestones.

## 60-second review

| Area | Evidence in this repository |
|---|---|
| Python | Reproducible source ingestion, schema validation, type normalisation and quality profiling |
| SQL / data modelling | PostgreSQL staging, star schema and commercial marts — next milestone |
| Power BI | Executive semantic model, DAX catalogue and dashboard — later milestone |
| Data quality | Explicit exception counts for missing fields, duplicates, cancellations and non-positive values |
| Reproducibility | UCI download path, SHA-256 source fingerprints, deterministic transforms, tests and CI |
| Business analysis | Version-controlled KPI definitions; no unsupported profit/margin assumptions |

## Business question

A commercial team needs a reliable answer to five recurring questions:

1. How are sales, orders and average order value changing over time?
2. Which customers return, and how does retention differ by acquisition cohort?
3. Which products and countries drive sales concentration?
4. What is the scale and pattern of cancellations/returns?
5. Which data-quality issues could materially distort management reporting?

RetailIQ builds the analytical system required to answer those questions rather than beginning with a dashboard and working backwards.

## Data source

**Online Retail II**, donated by Daqing Chen to the UCI Machine Learning Repository.

- **Rows:** 1,067,371 transaction lines
- **Period:** 1 December 2009 to 9 December 2011
- **Business:** UK-based registered non-store retailer
- **Fields:** invoice, product, quantity, date/time, unit price, customer and country
- **Known issues:** missing values, cancellations, negative quantities and duplicate-looking records
- **DOI:** `10.24432/C5CG6D`
- **Licence:** CC BY 4.0

The source contains **sales prices, not product costs**. RetailIQ therefore does not manufacture profit, margin, CAC or ROI metrics that cannot be supported by the data.

## Architecture

```text
UCI Online Retail II
        |
        v
Python ingestion
(download + SHA-256 provenance)
        |
        +------------------> raw source (immutable, gitignored)
        |
        v
Typed normalised Parquet
(row-preserving + source-sheet lineage)
        |
        v
Data-quality profiling
        |
        v
PostgreSQL
staging -> dimensions/facts -> commercial marts
        |
        v
Power BI semantic model
        |
        v
Executive dashboard + commercial insight memo
```

A fuller rationale is in [`docs/architecture.md`](docs/architecture.md).

## What is implemented now

The first milestone establishes the part of the system on which every later metric depends:

- downloads the official UCI source archive
- preserves the raw source outside Git
- calculates SHA-256 fingerprints for the archive and workbook
- records provenance metadata locally
- reads every workbook sheet
- validates the expected source schema
- normalises legacy column names and data types
- preserves workbook-sheet lineage
- derives an explicit cancellation flag
- writes a typed Parquet hand-off layer
- profiles missing values, duplicates, non-positive values and cancellation rows
- tests schema drift and important transformation behaviour
- runs linting and tests in GitHub Actions

## Quick start

### Requirements

- Python 3.11+
- Git

PostgreSQL and Power BI are **not required for Milestone 1**; they are introduced in the warehouse/BI milestones.

### Setup

```bash
git clone https://github.com/Prash2712/retailiq-commercial-analytics.git
cd retailiq-commercial-analytics
python -m venv .venv
```

Activate the environment, then install:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Run quality checks

```bash
make lint
make test
```

### Download and normalise the source data

```bash
make ingest
```

This creates local, gitignored artifacts under `data/raw/` and `data/interim/` and records source hashes in `data/raw/provenance.json`.

### Profile the normalised data

```bash
make profile
```

No raw dataset is committed to the repository.

## Repository structure

```text
.
├── .github/workflows/      # CI
├── data/                    # local generated data; raw/interim/processed are gitignored
├── docs/
│   ├── architecture.md      # design decisions and system boundary
│   ├── data_contract.md     # grain, fields, risks and quality contract
│   └── kpi_dictionary.md    # commercial metric definitions and guardrails
├── src/retailiq/
│   ├── cli.py               # command-line entry point
│   ├── config.py            # source and project paths
│   ├── ingest.py            # download, provenance and normalisation
│   └── quality.py           # quality profiling
├── tests/                   # transformation and quality tests
├── Makefile
└── pyproject.toml
```

## KPI design

Commercial definitions are treated as code-adjacent assets rather than labels added inside a dashboard. The current KPI contract includes:

- gross sales value
- cancellation value
- net sales value
- orders
- average order value
- units sold
- active customers
- repeat-customer rate
- cohort retention
- RFM measures
- product sales concentration
- geographic contribution

The definitions and limitations are maintained in [`docs/kpi_dictionary.md`](docs/kpi_dictionary.md).

## Data-quality policy

RetailIQ separates **observed source issues** from **business-rule exclusions**. For example, a negative quantity is not silently deleted simply because it complicates a sales measure.

The profiling layer records:

- exact duplicates
- missing invoice numbers
- missing product codes/descriptions
- missing customer IDs
- missing invoice timestamps
- non-positive quantities
- non-positive unit prices
- cancellation rows

See [`docs/data_contract.md`](docs/data_contract.md) for the current contract and interpretation risks.

## Delivery roadmap

- [x] Project charter and data-source selection
- [x] Reproducible ingestion foundation
- [x] Source provenance and schema contract
- [x] Baseline data-quality profiling and tests
- [x] Pull-request CI
- [ ] PostgreSQL staging layer
- [ ] Dimensional/star schema
- [ ] Reconciliation checks and commercial SQL marts
- [ ] Cohort retention and RFM analysis
- [ ] Power BI semantic model and DAX catalogue
- [ ] Executive dashboard
- [ ] Evidence-led commercial insight memo
- [ ] Final reproducibility audit and release

## Project standards

This repository follows four constraints throughout development:

1. **No fabricated impact.** Results and CV claims must be reproducible from committed code and documented data.
2. **No hidden cleaning.** Exclusion logic must be named, reviewable and reconciled.
3. **No metric theatre.** Metrics unsupported by the source are not invented.
4. **No notebook-only delivery.** The final analytical workflow must be runnable, tested and documented outside exploratory notebooks.

## Attribution

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. DOI: `10.24432/C5CG6D`. Licensed under CC BY 4.0.

## Licence

Project code and documentation are released under the MIT Licence. Dataset usage remains subject to the source dataset's CC BY 4.0 terms.
