# RetailIQ — Commercial Analytics & Executive BI Platform

RetailIQ is an end-to-end analytics engineering and business-intelligence portfolio project built on **real UK retail transaction data**. The objective is to turn a messy transactional source into a governed analytical model and decision-ready commercial reporting layer.

> **Status:** Foundation in progress

## Business problem

Commercial leaders need a trusted view of:

- net revenue and order trends
- average order value and units per order
- customer acquisition and repeat purchasing
- cohort retention and customer lifecycle
- product concentration and top/bottom performers
- cancellations and return-value exposure
- geographic revenue mix
- data-quality exceptions that can distort reporting

RetailIQ is designed as if an analyst were responsible for taking this from raw source data through validation, modelling, SQL analytics and an executive Power BI semantic layer.

## Data source

The project uses **Online Retail II** from the UCI Machine Learning Repository (Daqing Chen). It contains transactions for a UK-based registered non-store retailer from **1 December 2009 to 9 December 2011**.

- ~1.07 million transaction lines
- invoice, product, quantity, timestamp, unit price, customer and country fields
- cancellation invoices identified by invoice numbers beginning with `C`
- missing values and real-world data-quality issues
- source license: **CC BY 4.0**
- DOI: `10.24432/C5CG6D`

Raw source files are **not committed** to this repository. The ingestion pipeline downloads them from UCI and records provenance.

## Target architecture

```text
UCI Online Retail II
        |
        v
Python ingestion + provenance
        |
        v
Raw / staging layer
        |
        v
Data-quality rules + cleaning
        |
        v
PostgreSQL analytical warehouse
        |
        +--> dimensional/star model
        |
        v
SQL commercial marts
        |
        v
Power BI semantic model + DAX
        |
        v
Executive dashboard + insight memo
```

The warehouse and semantic model follow dimensional modelling principles: dimensions support filtering/grouping and fact tables retain a consistent analytical grain.

## Planned analytical outputs

1. **Executive scorecard** — revenue, orders, AOV, units, customers, cancellations
2. **Customer analytics** — repeat rate, cohort retention, RFM/lifecycle segmentation
3. **Product analytics** — revenue concentration, quantity, cancellation exposure
4. **Geographic analytics** — country contribution and customer mix
5. **Data-quality dashboard** — missing IDs, cancellations, invalid prices/quantities, duplicates
6. **Commercial insight memo** — concise evidence-led recommendations for management

## Engineering standards

- reproducible ingestion; no raw data committed
- explicit source attribution and data provenance
- deterministic transformation rules
- tested data-quality logic
- SQL kept reviewable and version controlled
- CI on pull requests
- no fabricated business metrics or fake client claims
- documented assumptions and limitations

## Repository roadmap

- [ ] Foundation, source contract and CI
- [ ] Raw-to-clean Python pipeline
- [ ] PostgreSQL warehouse + star schema
- [ ] SQL commercial marts and validation checks
- [ ] Customer cohort / RFM analytics
- [ ] Power BI semantic model and DAX measure catalogue
- [ ] Executive dashboard screenshots
- [ ] Final commercial insight memo
- [ ] Reproducibility and portfolio close-out

## Why this project exists

The aim is not to demonstrate another notebook. RetailIQ is intended to show the full analyst workflow: **source understanding → data quality → SQL modelling → KPI definition → BI → commercial interpretation**.

## Attribution

Dataset: Chen, D. *Online Retail II*. UCI Machine Learning Repository. DOI: 10.24432/C5CG6D. Licensed under CC BY 4.0.
