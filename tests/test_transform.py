from datetime import datetime

import pandas as pd
import pytest
from openpyxl import Workbook

from retail_analytics.config import (
    CLEAN_TRANSACTION_COLUMNS,
    EXPECTED_COLUMNS,
    EXPECTED_SHEETS,
)
from retail_analytics.transform import (
    TransformationError,
    load_raw_transactions,
    transform_transactions,
    write_processed_dataset,
)


def make_raw_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Invoice": ["489434", "C489435", "489436"],
            "StockCode": ["85048", "79323P", "22041"],
            "Description": ["LIGHTS", "CANDLE", "DECORATION"],
            "Quantity": [12, -1, -2],
            "InvoiceDate": [
                datetime(2009, 12, 1, 7, 45),
                datetime(2009, 12, 1, 8, 10),
                datetime(2009, 12, 1, 8, 30),
            ],
            "Price": [6.95, 5.0, 1.5],
            "Customer ID": [13085, None, 13086],
            "Country": ["United Kingdom"] * 3,
            "source_period": ["Year 2009-2010"] * 3,
            "source_row": [2, 3, 4],
        }
    )


def test_transform_transactions_uses_documented_schema_and_types():
    clean = transform_transactions(make_raw_frame())

    assert tuple(clean.columns) == CLEAN_TRANSACTION_COLUMNS
    assert str(clean["invoice_no"].dtype) == "string"
    assert str(clean["quantity"].dtype) == "Int64"
    assert str(clean["invoice_date"].dtype) == "datetime64[ns]"
    assert str(clean["unit_price"].dtype) == "Float64"
    assert str(clean["customer_id"].dtype) == "Int64"
    assert str(clean["source_row"].dtype) == "Int64"
    assert str(clean["is_cancellation"].dtype) == "boolean"
    assert str(clean["line_amount"].dtype) == "Float64"


def test_transform_preserves_cancellations_and_negative_adjustments():
    clean = transform_transactions(make_raw_frame())

    cancellation = clean.loc[clean["invoice_no"] == "C489435"].iloc[0]
    adjustment = clean.loc[clean["invoice_no"] == "489436"].iloc[0]

    assert bool(cancellation["is_cancellation"])
    assert cancellation["line_amount"] == pytest.approx(-5.0)
    assert not bool(adjustment["is_cancellation"])
    assert adjustment["line_amount"] == pytest.approx(-3.0)


def test_transform_preserves_missing_customer_ids():
    clean = transform_transactions(make_raw_frame())

    assert pd.isna(clean.loc[1, "customer_id"])
    assert len(clean) == 3


def test_transform_does_not_drop_duplicate_rows():
    raw = make_raw_frame().iloc[[0]]
    duplicated = pd.concat([raw, raw], ignore_index=True)

    clean = transform_transactions(duplicated)

    assert len(clean) == 2
    assert clean.iloc[0]["invoice_no"] == clean.iloc[1]["invoice_no"]


def test_transform_rejects_fractional_customer_ids():
    raw = make_raw_frame()
    raw.loc[0, "Customer ID"] = 13085.5

    with pytest.raises(
        TransformationError,
        match="customer_id contains non-integer values",
    ):
        transform_transactions(raw)


def test_load_raw_transactions_combines_sheets_with_lineage(tmp_path):
    workbook_path = tmp_path / "online_retail_II.xlsx"
    workbook = Workbook()
    workbook.remove(workbook.active)

    for index, sheet_name in enumerate(EXPECTED_SHEETS):
        worksheet = workbook.create_sheet(sheet_name)
        worksheet.append(EXPECTED_COLUMNS)
        worksheet.append(
            (
                f"48943{index}",
                "85048",
                "LIGHTS",
                12,
                datetime(2009 + index, 12, 1, 7, 45),
                6.95,
                13085,
                "United Kingdom",
            )
        )

    workbook.save(workbook_path)

    raw = load_raw_transactions(workbook_path)

    assert len(raw) == 2
    assert raw["source_period"].tolist() == list(EXPECTED_SHEETS)
    assert raw["source_row"].tolist() == [2, 2]


def test_write_processed_dataset_round_trips_parquet(tmp_path):
    clean = transform_transactions(make_raw_frame())
    output_path = tmp_path / "processed" / "transactions.parquet"

    result_path = write_processed_dataset(clean, output_path)
    restored = pd.read_parquet(result_path)

    assert result_path == output_path
    assert tuple(restored.columns) == CLEAN_TRANSACTION_COLUMNS
    assert len(restored) == len(clean)
    assert restored["line_amount"].tolist() == pytest.approx(
        clean["line_amount"].tolist()
    )
