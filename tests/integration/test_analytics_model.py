import os
from datetime import datetime
from decimal import Decimal

import pandas as pd
import psycopg
import pytest

from retail_analytics.analytics import build_analytics_model
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


def make_clean_frame() -> pd.DataFrame:
    raw = pd.DataFrame(
        {
            "Invoice": ["489434", "489435", "C489436", "489437"],
            "StockCode": ["85048", "85048", "79323P", None],
            "Description": ["OLD LIGHTS", "NEW LIGHTS", "CANDLE", None],
            "Quantity": [12, 3, -1, 2],
            "InvoiceDate": [
                datetime(2009, 12, 1, 7, 45),
                datetime(2009, 12, 2, 8, 0),
                datetime(2009, 12, 3, 9, 0),
                datetime(2009, 12, 4, 10, 0),
            ],
            "Price": [6.95, 7.25, 5.0, 2.5],
            "Customer ID": [13085, 13085, None, 13086],
            "Country": [
                "United Kingdom",
                "United Kingdom",
                "France",
                None,
            ],
            "source_period": ["Year 2009-2010"] * 4,
            "source_row": [2, 3, 4, 5],
        }
    )
    return transform_transactions(raw)


def fetch_all(settings: DatabaseSettings, query: str):
    with psycopg.connect(**settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def test_star_schema_build_is_repeatable_and_preserves_relationships(tmp_path):
    settings = DatabaseSettings.from_environment()
    parquet_path = tmp_path / "transactions.parquet"
    make_clean_frame().to_parquet(parquet_path, index=False, engine="pyarrow")
    load_transactions(parquet_path, settings=settings)

    first = build_analytics_model(settings=settings)

    assert first.staging_rows == 4
    assert first.fact_rows == 4
    assert first.dates == 4
    assert first.customers == 3
    assert first.products == 3
    assert first.countries == 3

    unknown_customer_rows = fetch_all(
        settings,
        """
        SELECT COUNT(*)
        FROM analytics.fact_sales
        WHERE customer_key = 0
        """,
    )
    assert unknown_customer_rows[0][0] == 1

    canonical_product = fetch_all(
        settings,
        """
        SELECT product_description
        FROM analytics.dim_product
        WHERE stock_code = '85048'
        """,
    )
    assert canonical_product == [("NEW LIGHTS",)]

    cancellation = fetch_all(
        settings,
        """
        SELECT is_cancellation, line_amount
        FROM analytics.fact_sales
        WHERE invoice_no = 'C489436'
        """,
    )
    assert cancellation == [(True, Decimal("-5.0000"))]

    first_customer_keys = fetch_all(
        settings,
        """
        SELECT customer_key, customer_id
        FROM analytics.dim_customer
        ORDER BY customer_key
        """,
    )

    second = build_analytics_model(settings=settings)
    second_customer_keys = fetch_all(
        settings,
        """
        SELECT customer_key, customer_id
        FROM analytics.dim_customer
        ORDER BY customer_key
        """,
    )

    assert second.fact_rows == 4
    assert second_customer_keys == first_customer_keys

    orphan_counts = fetch_all(
        settings,
        """
        SELECT
            COUNT(*) FILTER (WHERE d.date_key IS NULL),
            COUNT(*) FILTER (WHERE c.customer_key IS NULL),
            COUNT(*) FILTER (WHERE p.product_key IS NULL),
            COUNT(*) FILTER (WHERE co.country_key IS NULL)
        FROM analytics.fact_sales AS f
        LEFT JOIN analytics.dim_date AS d USING (date_key)
        LEFT JOIN analytics.dim_customer AS c USING (customer_key)
        LEFT JOIN analytics.dim_product AS p USING (product_key)
        LEFT JOIN analytics.dim_country AS co USING (country_key)
        """,
    )
    assert orphan_counts == [(0, 0, 0, 0)]
