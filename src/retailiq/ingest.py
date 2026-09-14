from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import requests

from retailiq.config import EXPECTED_XLSX_NAME, UCI_DATASET_URL, ProjectPaths

COLUMN_MAP = {
    "Invoice": "invoice_no",
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "UnitPrice": "unit_price",
    "Customer ID": "customer_id",
    "CustomerID": "customer_id",
    "Country": "country",
}

EXPECTED_COLUMNS = {
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_source(destination: Path, url: str = UCI_DATASET_URL) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination

    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return destination


def extract_workbook(zip_path: Path, raw_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path) as archive:
        candidates = [name for name in archive.namelist() if name.lower().endswith(".xlsx")]
        if len(candidates) != 1:
            raise ValueError(
                "Expected exactly one .xlsx file in source archive; "
                f"found {candidates}"
            )
        member = candidates[0]
        archive.extract(member, raw_dir)

    extracted = raw_dir / member
    target = raw_dir / EXPECTED_XLSX_NAME
    if extracted != target:
        extracted.replace(target)
    return target


def normalise_sheet(frame: pd.DataFrame, source_sheet: str) -> pd.DataFrame:
    renamed = frame.rename(columns=COLUMN_MAP).copy()
    missing = EXPECTED_COLUMNS.difference(renamed.columns)
    if missing:
        raise ValueError(f"Source schema changed; missing columns: {sorted(missing)}")

    output = renamed[list(sorted(EXPECTED_COLUMNS))].copy()
    output["invoice_no"] = output["invoice_no"].astype("string").str.strip()
    output["stock_code"] = output["stock_code"].astype("string").str.strip()
    output["description"] = output["description"].astype("string").str.strip()
    output["country"] = output["country"].astype("string").str.strip()
    output["customer_id"] = (
        output["customer_id"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .replace({"<NA>": pd.NA, "nan": pd.NA})
    )
    output["quantity"] = pd.to_numeric(output["quantity"], errors="coerce")
    output["unit_price"] = pd.to_numeric(output["unit_price"], errors="coerce")
    output["invoice_date"] = pd.to_datetime(output["invoice_date"], errors="coerce")
    output["source_sheet"] = source_sheet
    output["source_row_number"] = range(2, len(output) + 2)
    output["is_cancellation"] = output["invoice_no"].str.upper().str.startswith("C", na=False)
    output["line_value"] = output["quantity"] * output["unit_price"]
    return output


def workbook_to_parquet(workbook: Path, destination: Path) -> pd.DataFrame:
    sheets = pd.read_excel(workbook, sheet_name=None)
    if not sheets:
        raise ValueError("Workbook contains no sheets")

    combined = pd.concat(
        [normalise_sheet(frame, str(sheet_name)) for sheet_name, frame in sheets.items()],
        ignore_index=True,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(destination, index=False)
    return combined


def write_provenance(zip_path: Path, workbook: Path, row_count: int, destination: Path) -> None:
    payload = {
        "dataset": "UCI Online Retail II",
        "dataset_id": 502,
        "source_url": UCI_DATASET_URL,
        "downloaded_at_utc": datetime.now(UTC).isoformat(),
        "archive_sha256": sha256_file(zip_path),
        "workbook_sha256": sha256_file(workbook),
        "row_count": row_count,
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_ingestion(paths: ProjectPaths | None = None) -> Path:
    paths = paths or ProjectPaths()
    paths.ensure()
    zip_path = download_source(paths.raw / "online_retail_ii.zip")
    workbook = extract_workbook(zip_path, paths.raw)
    destination = paths.interim / "online_retail_ii_normalised.parquet"
    frame = workbook_to_parquet(workbook, destination)
    write_provenance(zip_path, workbook, len(frame), paths.provenance)
    return destination
