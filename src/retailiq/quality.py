from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

BUSINESS_DUPLICATE_COLUMNS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
]


@dataclass(frozen=True)
class QualitySummary:
    row_count: int
    exact_duplicate_rows: int
    missing_invoice_no: int
    missing_stock_code: int
    missing_description: int
    missing_customer_id: int
    missing_invoice_date: int
    non_positive_quantity_rows: int
    non_positive_unit_price_rows: int
    cancellation_rows: int


def profile_quality(frame: pd.DataFrame) -> QualitySummary:
    required = {
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
        "is_cancellation",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Cannot profile data; missing columns: {sorted(missing)}")

    return QualitySummary(
        row_count=len(frame),
        exact_duplicate_rows=int(
            frame.duplicated(subset=BUSINESS_DUPLICATE_COLUMNS, keep="first").sum()
        ),
        missing_invoice_no=int(frame["invoice_no"].isna().sum()),
        missing_stock_code=int(frame["stock_code"].isna().sum()),
        missing_description=int(frame["description"].isna().sum()),
        missing_customer_id=int(frame["customer_id"].isna().sum()),
        missing_invoice_date=int(frame["invoice_date"].isna().sum()),
        non_positive_quantity_rows=int(frame["quantity"].le(0).fillna(False).sum()),
        non_positive_unit_price_rows=int(frame["unit_price"].le(0).fillna(False).sum()),
        cancellation_rows=int(frame["is_cancellation"].fillna(False).sum()),
    )


def summary_as_dict(summary: QualitySummary) -> dict[str, int]:
    return asdict(summary)
