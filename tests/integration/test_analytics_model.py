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
            "Invoice": [
                "489434",
                "489435",
                "C489436",
                "489437",
                "489438",
                "489439",
            ],
            "StockCode": [
                "85048",
                "85048",
                "79323P",
                None,
                "DOT",
                "DCGS0076",
            ],
            "Description": [
                "OLD LIGHTS",
                "NEW LIGHTS",
                "CANDLE",
                None,
                "DOTCOM POSTAGE",
                "SUNJAR LED NIGHT LIGHT",
            ],
            "Quantity": [12, 3, -1, 2, 1, 1],
            "InvoiceDate": [
                datetime(2009, 12, 1, 7, 45),
                datetime(2009, 12, 2, 8, 0),
                datetime(2009, 12, 3, 9, 0),
                datetime(2009, 12, 4, 10, 0),
                datetime(2009, 12, 5, 10, 30),
                datetime(2009, 12, 6, 11, 0),
            ],
            "Price": [6.95, 7.25, 5.0, 2.5, 10.0, 8.0],
            "Customer ID": [13085, 13085, None, 13086, 13087, 13088],
            "Country": [
                "United Kingdom",
                "United Kingdom",
                "France",
                None,
                "United Kingdom",
                "United Kingdom",
            ],
            "source_period": ["Year 2009-2010"] * 6,
            "source_row": [2, 3, 4, 5, 6, 7],
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

    assert first.staging_rows == 6
    assert first.fact_rows == 6
    assert first.dates == 6
    assert first.customers == 5
    assert first.products == 5
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

    classifications = fetch_all(
        settings,
        """
        SELECT stock_code, product_type
        FROM analytics.dim_product
        WHERE stock_code IN ('DOT', 'DCGS0076')
        ORDER BY stock_code
        """,
    )
    assert classifications == [
        ("DCGS0076", "merchandise"),
        ("DOT", "shipping"),
    ]

    unknown_product = fetch_all(
        settings,
        """
        SELECT product_type
        FROM analytics.dim_product
        WHERE product_key = 0
        """,
    )
    assert unknown_product == [("unknown",)]

    cancellation = fetch_all(
        settings,
        """
        SELECT is_cancellation, line_amount
        FROM analytics.fact_sales
        WHERE invoice_no = 'C489436'
        """,
    )
    assert cancellation == [(True, Decimal("-5.0000"))]

    first_product_keys = fetch_all(
        settings,
        """
        SELECT product_key, stock_code, product_type
        FROM analytics.dim_product
        ORDER BY product_key
        """,
    )

    second = build_analytics_model(settings=settings)
    second_product_keys = fetch_all(
        settings,
        """
        SELECT product_key, stock_code, product_type
        FROM analytics.dim_product
        ORDER BY product_key
        """,
    )

    assert second.fact_rows == 6
    assert second_product_keys == first_product_keys

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
