from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UCI_DATASET_ID = 502
UCI_DATASET_URL = "https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip"
EXPECTED_XLSX_NAME = "online_retail_II.xlsx"


@dataclass(frozen=True)
class ProjectPaths:
    root: Path = PROJECT_ROOT

    @property
    def raw(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def interim(self) -> Path:
        return self.root / "data" / "interim"

    @property
    def processed(self) -> Path:
        return self.root / "data" / "processed"

    @property
    def provenance(self) -> Path:
        return self.raw / "provenance.json"

    def ensure(self) -> None:
        for path in (self.raw, self.interim, self.processed):
            path.mkdir(parents=True, exist_ok=True)
