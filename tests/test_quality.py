import pandas as pd

from retailiq.quality import profile_quality


def test_profile_quality_counts_expected_exceptions() -> None:
    frame = pd.DataFrame(
        {
            "invoice_no": ["1", "C2", "C2"],
            "stock_code": ["A", "B", "B"],
            "description": ["Item A", None, None],
            "quantity": [2, -1, -1],
            "invoice_date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-02"]),
            "unit_price": [10.0, 0.0, 0.0],
            "customer_id": ["100", None, None],
            "is_cancellation": [False, True, True],
        }
    )

    result = profile_quality(frame)

    assert result.row_count == 3
    assert result.exact_duplicate_rows == 1
    assert result.missing_description == 2
    assert result.missing_customer_id == 2
    assert result.non_positive_quantity_rows == 2
    assert result.non_positive_unit_price_rows == 2
    assert result.cancellation_rows == 2
