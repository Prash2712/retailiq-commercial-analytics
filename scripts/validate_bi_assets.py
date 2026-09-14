from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

THEME = ROOT / "powerbi" / "theme" / "retailiq-theme.json"
TMDL = ROOT / "powerbi" / "tmdl" / "retailiq-model.tmdl"
REPORT_SPEC = ROOT / "powerbi" / "report" / "report-spec.md"
MEASURE_CATALOGUE = ROOT / "powerbi" / "dax" / "measure-catalogue.md"
MART_SQL = ROOT / "sql" / "marts" / "020_create_commercial_marts.sql"
VERIFIED_RESULTS = ROOT / "docs" / "verified_results.md"

REQUIRED_PAGES = {
    "Page 1 — Executive overview",
    "Page 2 — Customer & retention",
    "Page 3 — Product performance",
    "Page 4 — Geography",
    "Page 5 — Data quality & reconciliation",
}

REQUIRED_MEASURES = {
    "Gross Sales Value",
    "Cancellation Value",
    "Net Sales Value",
    "Sale Orders",
    "Average Order Value",
    "Known Customers",
    "Repeat Customer Rate",
    "Repeated Exact Rows",
    "Missing Customer ID Rows",
}

VERIFIED_MARKERS = {
    "1,067,371",
    "£19,445,179.5680",
    "40,077",
    "5,878",
    "72.39%",
    "34,335",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    theme = json.loads(THEME.read_text(encoding="utf-8"))
    require(theme.get("name") == "RetailIQ Executive", "Unexpected Power BI theme name")
    require(bool(theme.get("dataColors")), "Power BI theme must define dataColors")

    tmdl = TMDL.read_text(encoding="utf-8")
    report_spec = REPORT_SPEC.read_text(encoding="utf-8")
    catalogue = MEASURE_CATALOGUE.read_text(encoding="utf-8")
    mart_sql = MART_SQL.read_text(encoding="utf-8")
    verified = VERIFIED_RESULTS.read_text(encoding="utf-8")

    for parameter in ("PBI_Server", "PBI_Database"):
        require(parameter in tmdl, f"Missing TMDL parameter: {parameter}")

    for measure in REQUIRED_MEASURES:
        require(
            f"measure '{measure}'" in tmdl,
            f"Required TMDL measure missing: {measure}",
        )
        require(measure in catalogue, f"Measure catalogue missing: {measure}")

    for page in REQUIRED_PAGES:
        require(page in report_spec, f"Report specification missing: {page}")

    lowered_tmdl = tmdl.lower()
    require("password=" not in lowered_tmdl, "TMDL must not contain a password")
    require("postgresql://" not in lowered_tmdl, "TMDL must not embed a credential-bearing DSN")

    governed_aov_dax = "DIVIDE([Net Sales Value], [Sale Orders])"
    require(governed_aov_dax in tmdl, "TMDL AOV does not use governed net-sales definition")
    require(governed_aov_dax in catalogue, "Catalogue AOV does not match TMDL")

    governed_aov_sql = (
        "(gross_sales_value - cancellation_value) / NULLIF(orders, 0) "
        "AS average_order_value"
    )
    require(governed_aov_sql in mart_sql, "SQL AOV does not match governed metric contract")

    for marker in VERIFIED_MARKERS:
        require(marker in verified, f"Verified-results evidence missing marker: {marker}")

    print("BI asset contract checks passed")


if __name__ == "__main__":
    main()
