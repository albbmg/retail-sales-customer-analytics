from pathlib import Path

DATASET_ARCHIVE_URL = (
    "https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip"
)

RAW_DATA_DIR = Path("data/raw")
RAW_WORKBOOK_PATH = RAW_DATA_DIR / "online_retail_II.xlsx"

PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_TRANSACTIONS_PATH = PROCESSED_DATA_DIR / "transactions.parquet"

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
