from datetime import datetime

import pandas as pd
import pytest

from retail_analytics.config import CLEAN_TRANSACTION_COLUMNS
from retail_analytics.load import LoadError, read_clean_dataset, validate_clean_dataset


def make_clean_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "invoice_no": pd.Series(["489434", "C489435"], dtype="string"),
            "stock_code": pd.Series(["85048", "79323P"], dtype="string"),
            "description": pd.Series(["LIGHTS", "CANDLE"], dtype="string"),
            "quantity": pd.Series([12, -1], dtype="Int64"),
            "invoice_date": pd.to_datetime(
                [
                    datetime(2009, 12, 1, 7, 45),
                    datetime(2009, 12, 1, 8, 10),
                ]
            ),
            "unit_price": pd.Series([6.95, 5.0], dtype="Float64"),
            "customer_id": pd.Series([13085, pd.NA], dtype="Int64"),
            "country": pd.Series(
                ["United Kingdom", "United Kingdom"],
                dtype="string",
            ),
            "source_period": pd.Series(
                ["Year 2009-2010", "Year 2009-2010"],
                dtype="string",
            ),
            "source_row": pd.Series([2, 3], dtype="Int64"),
            "is_cancellation": pd.Series([False, True], dtype="boolean"),
            "line_amount": pd.Series([83.4, -5.0], dtype="Float64"),
        }
    ).loc[:, CLEAN_TRANSACTION_COLUMNS]


def test_validate_clean_dataset_accepts_expected_contract():
    validate_clean_dataset(make_clean_frame())


def test_validate_clean_dataset_rejects_wrong_column_order():
    frame = make_clean_frame()
    frame = frame.loc[:, list(reversed(frame.columns))]

    with pytest.raises(LoadError, match="Unexpected clean dataset columns"):
        validate_clean_dataset(frame)


def test_validate_clean_dataset_rejects_null_lineage():
    frame = make_clean_frame()
    frame.loc[0, "source_row"] = pd.NA

    with pytest.raises(LoadError, match="lineage contains null"):
        validate_clean_dataset(frame)


def test_validate_clean_dataset_rejects_duplicate_lineage():
    frame = make_clean_frame()
    frame.loc[1, ["source_period", "source_row"]] = [
        frame.loc[0, "source_period"],
        frame.loc[0, "source_row"],
    ]

    with pytest.raises(LoadError, match="lineage contains duplicate"):
        validate_clean_dataset(frame)


def test_read_clean_dataset_round_trips_parquet(tmp_path):
    frame = make_clean_frame()
    path = tmp_path / "transactions.parquet"
    frame.to_parquet(path, index=False, engine="pyarrow")

    restored = read_clean_dataset(path)

    assert tuple(restored.columns) == CLEAN_TRANSACTION_COLUMNS
    assert len(restored) == 2
