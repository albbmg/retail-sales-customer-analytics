import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import psycopg
import pytest

from retail_analytics.analytics import build_analytics_model
from retail_analytics.config import PROJECT_ROOT
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

ANALYSIS_DIR = PROJECT_ROOT / "sql/analysis"


def make_clean_frame() -> pd.DataFrame:
    raw = pd.DataFrame(
        {
            "Invoice": [
                "1001",
                "1001",
                "1002",
                "C1003",
                "1004",
                "1005",
            ],
            "StockCode": ["A", "B", "A", "A", "B", "A"],
            "Description": [
                "PRODUCT A",
                "PRODUCT B",
                "PRODUCT A",
                "PRODUCT A",
                "PRODUCT B",
                "PRODUCT A",
            ],
            "Quantity": [2, 1, 3, -1, 4, 1],
            "InvoiceDate": [
                datetime(2010, 1, 1, 10, 0),
                datetime(2010, 1, 1, 10, 0),
                datetime(2010, 1, 15, 11, 0),
                datetime(2010, 1, 20, 12, 0),
                datetime(2010, 2, 1, 9, 0),
                datetime(2010, 2, 2, 9, 30),
            ],
            "Price": [10.0, 5.0, 10.0, 10.0, 5.0, 10.0],
            "Customer ID": [1, 1, 2, 2, 1, None],
            "Country": [
                "United Kingdom",
                "United Kingdom",
                "France",
                "France",
                "United Kingdom",
                "United Kingdom",
            ],
            "source_period": ["Year 2009-2010"] * 6,
            "source_row": [2, 3, 4, 5, 6, 7],
        }
    )
    return transform_transactions(raw)


def run_query(settings: DatabaseSettings, filename: str):
    query = (Path(ANALYSIS_DIR) / filename).read_text(encoding="utf-8")
    with psycopg.connect(**settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def test_core_analysis_queries_match_documented_definitions(tmp_path):
    settings = DatabaseSettings.from_environment()
    parquet_path = tmp_path / "transactions.parquet"

    make_clean_frame().to_parquet(parquet_path, index=False, engine="pyarrow")
    load_transactions(parquet_path, settings=settings)
    build_analytics_model(settings=settings)

    overview = run_query(settings, "01_kpi_overview.sql")
    assert overview == [
        (
            Decimal("75.00"),
            Decimal("85.00"),
            4,
            11,
            Decimal("21.25"),
            2,
            Decimal("32.50"),
            Decimal("0.2000"),
        )
    ]

    monthly = run_query(settings, "02_monthly_sales.sql")
    assert monthly == [
        (
            datetime(2010, 1, 1).date(),
            Decimal("45.00"),
            Decimal("55.00"),
            2,
            6,
            2,
            Decimal("27.50"),
            1,
            Decimal("0.3333"),
        ),
        (
            datetime(2010, 2, 1).date(),
            Decimal("30.00"),
            Decimal("30.00"),
            2,
            5,
            1,
            Decimal("15.00"),
            0,
            Decimal("0.0000"),
        ),
    ]

    customers = run_query(settings, "03_customer_performance.sql")
    assert customers[0][0] == 1
    assert customers[0][4] == Decimal("45.00")
    assert customers[1][0] == 2
    assert customers[1][4] == Decimal("20.00")

    products = run_query(settings, "04_product_performance.sql")
    assert products[0][0] == "A"
    assert products[0][2] == Decimal("50.00")
    assert products[0][4] == 6
    assert products[0][5] == Decimal("10.00")

    countries = run_query(settings, "05_country_performance.sql")
    assert countries[0][0] == "United Kingdom"
    assert countries[0][1] == Decimal("55.00")
    assert countries[1][0] == "France"
    assert countries[1][1] == Decimal("20.00")

    cancellations = run_query(settings, "06_cancellation_trend.sql")
    assert cancellations == [
        (
            datetime(2010, 1, 1).date(),
            1,
            1,
            Decimal("10.00"),
            1,
        )
    ]
