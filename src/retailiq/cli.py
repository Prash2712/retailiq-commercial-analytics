from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from retailiq.ingest import run_ingestion
from retailiq.quality import profile_quality, summary_as_dict
from retailiq.warehouse import build_warehouse, initialise_warehouse, reconciliation_summary

DEFAULT_PARQUET = Path("data/interim/online_retail_ii_normalised.parquet")


def add_database_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db-url",
        default=None,
        help="PostgreSQL URL. Defaults to RETAILIQ_DB_URL or the local compose database.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="retailiq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ingest", help="Download, normalise and persist the source dataset.")

    profile = subparsers.add_parser("profile", help="Profile a normalised parquet dataset.")
    profile.add_argument("--input", type=Path, default=DEFAULT_PARQUET)

    warehouse_init = subparsers.add_parser(
        "warehouse-init",
        help="Create PostgreSQL warehouse schemas and tables.",
    )
    add_database_argument(warehouse_init)

    warehouse_build = subparsers.add_parser(
        "warehouse-build",
        help="Load staging, build the star schema/marts and enforce reconciliation.",
    )
    warehouse_build.add_argument("--input", type=Path, default=DEFAULT_PARQUET)
    add_database_argument(warehouse_build)

    reconcile = subparsers.add_parser(
        "reconcile",
        help="Print warehouse row-count and line-value reconciliation.",
    )
    add_database_argument(reconcile)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "ingest":
        output = run_ingestion()
        print(f"Wrote normalised dataset to {output}")
        return

    if args.command == "profile":
        frame = pd.read_parquet(args.input)
        print(json.dumps(summary_as_dict(profile_quality(frame)), indent=2))
        return

    if args.command == "warehouse-init":
        initialise_warehouse(args.db_url)
        print("Warehouse schemas and tables are ready")
        return

    if args.command == "warehouse-build":
        summary = build_warehouse(args.input, args.db_url)
        print(json.dumps(summary, indent=2, default=str))
        return

    summary = reconciliation_summary(args.db_url)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
