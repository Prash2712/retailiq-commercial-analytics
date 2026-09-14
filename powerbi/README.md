# Power BI implementation

This directory defines the RetailIQ BI layer as source-controlled text assets. The objective is to make the semantic model and report design reviewable in Git rather than treating a binary `.pbix` as the only artefact.

Power BI Desktop project (PBIP), TMDL and PBIR formats are Microsoft-supported developer workflows for source-controlled model/report metadata. RetailIQ uses a TMDL model script plus a governed report specification so the analytical logic remains inspectable before any binary report is published.

## BI architecture

```text
PostgreSQL core star schema
        |
        +--> Date
        +--> Customer
        +--> Product
        +--> Geography
        +--> Fact Transactions
        |
        +--> Customer Summary / RFM / Cohort helper marts
        +--> Data Quality / Reconciliation helper marts
        |
        v
Power BI Import semantic model
        |
        v
Governed DAX measures
        |
        v
Executive / Customer / Product / Geography / Data Quality pages
```

## Files

- `tmdl/retailiq-model.tmdl` — source-controlled TMDL script for the semantic model
- `dax/measure-catalogue.md` — measure definitions, intent and validation rules
- `report/report-spec.md` — page-by-page visual and interaction specification
- `theme/retailiq-theme.json` — restrained report theme

## Prerequisites

1. Build the local warehouse:

```bash
docker compose up -d postgres
retailiq ingest
retailiq warehouse-build
```

2. Confirm reconciliation:

```bash
retailiq warehouse-reconcile
```

Expected full-source reconciliation is documented in `../docs/verified_results.md`.

3. Install Power BI Desktop on Windows and ensure the PostgreSQL connector prerequisites are available.

## Create the semantic model

1. Open Power BI Desktop and create a blank model/report.
2. Open **TMDL view**.
3. Open `tmdl/retailiq-model.tmdl` from this repository.
4. Apply the script.
5. When Power BI requests PostgreSQL credentials, use the credentials for your local `compose.yaml` instance.
6. Refresh the model.
7. Check that the model row counts and headline measures match `../docs/verified_results.md` before designing visuals.

The script exposes `PBI_Server` and `PBI_Database` parameters. They default to `localhost` and `retailiq`, so the model can be repointed without editing every table query.

## Report build

Build the report pages exactly from `report/report-spec.md`. The page design intentionally uses native Power BI visuals only; there is no dependency on marketplace/custom visuals.

The final report should be saved as a **Power BI Project (PBIP)** using TMDL/PBIR where available so the generated model/report metadata can be reviewed in Git. Local caches and credentials must remain excluded from version control.

## Validation contract

A Power BI build is accepted only when all of the following are true:

- fact row count = `1,067,371`
- net sales = `£19,445,179.5680`
- sale orders = `40,077`
- known customers = `5,878`
- repeat customers = `4,255`
- repeat-customer rate = `72.39%`
- repeated exact business rows = `34,335`
- source-to-fact row difference = `0`
- source-to-fact line-value difference = `£0.0000`

If a visual produces a different result, investigate filter context or metric definition; do not edit the reference values to make the dashboard agree.

## Security and portability

- Database passwords are never committed to TMDL or Git.
- The TMDL model references server/database parameters only.
- `compose.yaml` provides local development credentials; production credentials would be supplied through the Power BI/Fabric connection layer.
- The source workbook and generated data remain gitignored.

## Current boundary

The repository contains the semantic-model source and complete report specification. Power BI Desktop itself is a Windows application and is not executed by this repository's Linux GitHub Actions runner. A rendered PBIP/PBIX should therefore be committed only after it has been opened, refreshed and visually reviewed in Power BI Desktop.
