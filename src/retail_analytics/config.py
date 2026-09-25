from pathlib import Path

DATASET_ARCHIVE_URL = (
    "https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip"
)

RAW_DATA_DIR = Path("data/raw")
RAW_WORKBOOK_PATH = RAW_DATA_DIR / "online_retail_II.xlsx"

PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_TRANSACTIONS_PATH = PROCESSED_DATA_DIR / "transactions.parquet"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGING_SCHEMA_SQL_PATH = PROJECT_ROOT / "sql/staging/01_create_transactions.sql"
ANALYTICS_MODEL_SQL_PATH = PROJECT_ROOT / "sql/analytics/01_build_star_schema.sql"
QUALITY_CHECKS_SQL_PATH = PROJECT_ROOT / "sql/quality/01_analytics_checks.sql"
PROFILE_SOURCE_SQL_PATH = PROJECT_ROOT / "sql/profile/01_source_profile.sql"

EXPECTED_SHEETS = (
    "Year 2009-2010",
    "Year 2010-2011",
)

EXPECTED_COLUMNS = (
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
)

CLEAN_TRANSACTION_COLUMNS = (
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "source_period",
    "source_row",
    "is_cancellation",
    "line_amount",
)
