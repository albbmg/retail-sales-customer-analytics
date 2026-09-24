import os
from datetime import datetime
from decimal import Decimal

import pandas as pd
import psycopg
import pytest

from retail_analytics.analytics import build_analytics_model
from retail_analytics.database import DatabaseSettings
from retail_analytics.load import load_transactions
from retail_analytics.quality import (
    DataQualityError,
    assert_quality,
    run_quality_checks,
)
from retail_analytics.transform import transform_transactions

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_INTEGRATION") != "1",
    reason="PostgreSQL integration environment is not enabled",
)


def make_clean_frame() -> pd.DataFrame:
    raw = pd.DataFrame(
        {
            "Invoice": ["489434", "C489435"],
            "StockCode": ["85048", "79323P"],
            "Description": ["LIGHTS", "CANDLE"],
            "Quantity": [12, -1],
            "InvoiceDate": [
                datetime(2009, 12, 1, 7, 45),
                datetime(2009, 12, 2, 8, 10),
            ],
            "Price": [6.95, 5.0],
            "Customer ID": [13085, None],
            "Country": ["United Kingdom", "France"],
            "source_period": ["Year 2009-2010", "Year 2009-2010"],
            "source_row": [2, 3],
        }
    )
    return transform_transactions(raw)


def test_quality_checks_pass_and_detect_corrupted_measure(tmp_path):
    settings = DatabaseSettings.from_environment()
    parquet_path = tmp_path / "transactions.parquet"

    make_clean_frame().to_parquet(parquet_path, index=False, engine="pyarrow")
    load_transactions(parquet_path, settings=settings)
    build_analytics_model(settings=settings)

    valid_results = run_quality_checks(settings=settings)
    assert all(result.passed for result in valid_results)
    assert_quality(valid_results)

    with psycopg.connect(**settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analytics.fact_sales
                SET line_amount = line_amount + %s
                WHERE source_period = %s AND source_row = %s
                """,
                (Decimal("1.0000"), "Year 2009-2010", 2),
            )

    corrupted_results = run_quality_checks(settings=settings)
    failures = {
        result.check_name: result.failed_rows
        for result in corrupted_results
        if not result.passed
    }

    assert failures == {"line_amount_consistency": 1}

    with pytest.raises(
        DataQualityError,
        match="line_amount_consistency=1",
    ):
        assert_quality(corrupted_results)
