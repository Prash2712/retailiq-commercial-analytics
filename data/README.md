# Data directory

Data files are generated locally and are not stored in Git.

```text
data/
├── raw/         # downloaded UCI archive, workbook and provenance metadata
├── interim/     # typed, row-preserving normalised Parquet
└── processed/   # later analytical outputs / extracts
```

## Obtain the data

After installing the package:

```bash
retailiq ingest
```

The command downloads the official UCI Online Retail II archive and records SHA-256 hashes in `data/raw/provenance.json`.

## Why the dataset is excluded from Git

The public repository should contain the **method**, tests, metadata and attribution—not duplicate a 40+ MB source file. Keeping raw data outside version control also prevents accidental edits from being mistaken for the original source.

Source: UCI Machine Learning Repository, Online Retail II (dataset 502), DOI `10.24432/C5CG6D`, CC BY 4.0.
