from pathlib import Path

DATASET_ARCHIVE_URL = (
    "https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip"
)
RAW_DATA_DIR = Path("data/raw")
RAW_WORKBOOK_PATH = RAW_DATA_DIR / "online_retail_II.xlsx"

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
