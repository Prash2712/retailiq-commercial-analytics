from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from retailiq.ingest import run_ingestion
from retailiq.quality import profile_quality, summary_as_dict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="retailiq")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ingest", help="Download, normalise and persist the source dataset.")

    profile = subparsers.add_parser("profile", help="Profile a normalised parquet dataset.")
    profile.add_argument(
        "--input",
        type=Path,
        default=Path("data/interim/online_retail_ii_normalised.parquet"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "ingest":
        output = run_ingestion()
        print(f"Wrote normalised dataset to {output}")
        return

    frame = pd.read_parquet(args.input)
    print(json.dumps(summary_as_dict(profile_quality(frame)), indent=2))


if __name__ == "__main__":
    main()
