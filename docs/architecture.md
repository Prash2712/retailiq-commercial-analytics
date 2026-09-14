# Architecture

RetailIQ is organised so each layer has one responsibility and can be inspected independently.

```text
                         +----------------------+
                         | UCI Online Retail II |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Python ingestion     |
                         | download + checksum  |
                         +----------+-----------+
                                    |
                    +---------------+----------------+
                    |                                |
                    v                                v
          +-------------------+             +-------------------+
          | raw/              |             | provenance.json   |
          | immutable source  |             | source hashes     |
          +---------+---------+             +-------------------+
                    |
                    v
          +-------------------+
          | interim Parquet   |
          | typed + lineage   |
          +---------+---------+
                    |
                    v
          +-------------------+
          | quality profiling |
          | explicit issues   |
          +---------+---------+
                    |
                    v
          +-------------------+
          | PostgreSQL        |
          | staging + marts   |
          +---------+---------+
                    |
          +---------+---------+
          |                   |
          v                   v
 +------------------+   +------------------+
 | dimensional      |   | analytical SQL   |
 | model / facts    |   | cohorts / RFM    |
 +---------+--------+   +---------+--------+
           |                      |
           +----------+-----------+
                      |
                      v
             +------------------+
             | Power BI         |
             | semantic model   |
             +--------+---------+
                      |
                      v
             +------------------+
             | Executive views  |
             | + insight memo   |
             +------------------+
```

## Design decisions

### 1. Raw data is immutable
The source archive/workbook is never edited in place. This keeps the project auditable and makes transformation defects reversible.

### 2. Parquet is the hand-off from ingestion to modelling
Excel is useful as a source but inefficient and weakly typed for repeated analytics work. The normalised Parquet layer preserves source rows while making downstream processing faster and typed.

### 3. Data quality is a first-class output
Missing customers, cancellations, non-positive quantities/prices and duplicates are profiled before business rules are applied. This prevents a dashboard from hiding source-quality problems.

### 4. Business logic belongs in SQL / semantic measures
Python performs source ingestion and normalisation. Commercial definitions are implemented in reviewable warehouse SQL and, where appropriate, documented DAX. This mirrors a common analyst/BI delivery model and avoids burying KPI logic inside notebooks.

### 5. Dimensional model before dashboard
Power BI will consume a star-oriented model rather than a single denormalised spreadsheet. The intended model includes date, customer, product and geography dimensions plus transaction/sales facts.

### 6. Reproducibility over screenshots
A screenshot is supporting evidence, not the project. A reviewer should be able to reproduce data preparation and validation from the repository.

## Planned deployment boundary

The initial target is a local reproducible analytical stack using Python + PostgreSQL + Power BI. Cloud deployment is intentionally not part of the first milestone; it will only be added if it improves the analytical story rather than adding technology for its own sake.
