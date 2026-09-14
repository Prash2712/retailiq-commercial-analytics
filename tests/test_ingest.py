import pandas as pd

from retailiq.ingest import normalise_sheet


def test_normalise_sheet_maps_legacy_online_retail_columns() -> None:
    source = pd.DataFrame(
        {
            "Invoice": ["C489434", "489435"],
            "StockCode": ["85048", "79323P"],
            "Description": ["15CM CHRISTMAS GLASS BALL 20 LIGHTS", "PINK CHERRY LIGHTS"],
            "Quantity": [-12, 12],
            "InvoiceDate": ["2009-12-01 07:45:00", "2009-12-01 07:46:00"],
            "Price": [6.95, 6.75],
            "Customer ID": [13085.0, None],
            "Country": ["United Kingdom", "United Kingdom"],
        }
    )

    result = normalise_sheet(source, "Year 2009-2010")

    assert result.loc[0, "invoice_no"] == "C489434"
    assert result.loc[0, "customer_id"] == "13085"
    assert pd.isna(result.loc[1, "customer_id"])
    assert bool(result.loc[0, "is_cancellation"]) is True
    assert bool(result.loc[1, "is_cancellation"]) is False
    assert result.loc[0, "line_value"] == -83.4
    assert set(result["source_sheet"]) == {"Year 2009-2010"}
    assert result["source_row_number"].tolist() == [2, 3]


def test_normalise_sheet_fails_loudly_on_schema_drift() -> None:
    source = pd.DataFrame({"Invoice": ["1"]})

    try:
        normalise_sheet(source, "sheet")
    except ValueError as exc:
        assert "missing columns" in str(exc)
    else:
        raise AssertionError("Expected a schema validation error")
