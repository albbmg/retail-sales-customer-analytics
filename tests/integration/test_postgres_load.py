import os
from datetime import datetime

import pandas as pd
import psycopg
import pytest

from retail_analytics.database import DatabaseSettings
from retail_analytics.load import load_transactions
from retail_analytics.transform import transform_transactions

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_POSTGRES_INTEGRATION") != "1",
        reason="PostgreSQL integration environment is not enabled",
    ),
]


def make_clean_frame(rows: int) -> pd.DataFrame:
    raw = pd.DataFrame(
        {
            "Invoice": ["489434", "C489435"][:rows],
            "StockCode": ["85048", "79323P"][:rows],
            "Description": ["LIGHTS", "CANDLE"][:rows],
            "Quantity": [12, -1][:rows],
            "InvoiceDate": [
                datetime(2009, 12, 1, 7, 45),
                datetime(2009, 12, 1, 8, 10),
            ][:rows],
            "Price": [6.95, 5.0][:rows],
            "Customer ID": [13085, None][:rows],
            "Country": ["United Kingdom", "United Kingdom"][:rows],
            "source_period": ["Year 2009-2010", "Year 2009-2010"][:rows],
            "source_row": [2, 3][:rows],
        }
    )
    return transform_transactions(raw)


def database_count(settings: DatabaseSettings) -> int:
    with psycopg.connect(**settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM staging.transactions")
            return cursor.fetchone()[0]


def test_full_refresh_load_is_repeatable(tmp_path):
    settings = DatabaseSettings.from_environment()
    parquet_path = tmp_path / "transactions.parquet"

    make_clean_frame(2).to_parquet(parquet_path, index=False, engine="pyarrow")
    first = load_transactions(parquet_path, settings=settings)

    assert first.source_rows == 2
    assert first.loaded_rows == 2
    assert database_count(settings) == 2

    make_clean_frame(1).to_parquet(parquet_path, index=False, engine="pyarrow")
    second = load_transactions(parquet_path, settings=settings)

    assert second.source_rows == 1
    assert second.loaded_rows == 1
    assert database_count(settings) == 1
