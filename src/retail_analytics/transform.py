import argparse
from pathlib import Path

import pandas as pd

from .config import (
    CLEAN_TRANSACTION_COLUMNS,
    EXPECTED_COLUMNS,
    EXPECTED_SHEETS,
    PROCESSED_TRANSACTIONS_PATH,
    RAW_WORKBOOK_PATH,
)
from .validation import DatasetValidationError, validate_workbook

RAW_TO_CLEAN_COLUMNS = {
    "Invoice": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country",
}


class TransformationError(ValueError):
    """Raised when raw values cannot be converted to the clean data contract."""


def load_raw_transactions(path: Path = RAW_WORKBOOK_PATH) -> pd.DataFrame:
    """Load both validated source sheets and add row-level lineage."""
    path = Path(path)
    validate_workbook(path)

    frames: list[pd.DataFrame] = []

    try:
        for sheet_name in EXPECTED_SHEETS:
            frame = pd.read_excel(
                path,
                sheet_name=sheet_name,
                engine="openpyxl",
            )
            frame["source_period"] = sheet_name
            frame["source_row"] = pd.Series(
                range(2, len(frame) + 2),
                index=frame.index,
                dtype="Int64",
            )
            frames.append(frame)
    except (OSError, ValueError) as exc:
        raise TransformationError(f"Could not read source workbook: {path}") from exc

    return pd.concat(frames, ignore_index=True)


def _to_nullable_integer(series: pd.Series, column_name: str) -> pd.Series:
    try:
        numeric = pd.to_numeric(series, errors="raise")
    except (TypeError, ValueError) as exc:
        raise TransformationError(f"{column_name} contains non-numeric values") from exc

    non_null = numeric.dropna()
    if ((non_null % 1) != 0).any():
        raise TransformationError(f"{column_name} contains non-integer values")

    return numeric.astype("Int64")


def transform_transactions(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize the raw source into a typed, loss-conscious clean dataset."""
    required_columns = (*EXPECTED_COLUMNS, "source_period", "source_row")
    missing_columns = [
        column for column in required_columns if column not in raw.columns
    ]

    if missing_columns:
        missing = ", ".join(missing_columns)
        raise TransformationError(f"Missing required column(s): {missing}")

    clean = raw.loc[:, required_columns].rename(columns=RAW_TO_CLEAN_COLUMNS).copy()

    for column in (
        "invoice_no",
        "stock_code",
        "description",
        "country",
        "source_period",
    ):
        clean[column] = clean[column].astype("string")

    clean["quantity"] = _to_nullable_integer(clean["quantity"], "quantity")
    clean["customer_id"] = _to_nullable_integer(
        clean["customer_id"],
        "customer_id",
    )
    clean["source_row"] = _to_nullable_integer(
        clean["source_row"],
        "source_row",
    )

    try:
        clean["invoice_date"] = pd.to_datetime(
            clean["invoice_date"],
            errors="raise",
        )
    except (TypeError, ValueError) as exc:
        raise TransformationError("invoice_date contains invalid date values") from exc

    try:
        clean["unit_price"] = pd.to_numeric(
            clean["unit_price"],
            errors="raise",
        ).astype("Float64")
    except (TypeError, ValueError) as exc:
        raise TransformationError("unit_price contains non-numeric values") from exc

    clean["is_cancellation"] = (
        clean["invoice_no"].str.startswith("C", na=False).astype("boolean")
    )
    clean["line_amount"] = (
        clean["quantity"].astype("Float64") * clean["unit_price"]
    ).astype("Float64")

    return clean.loc[:, CLEAN_TRANSACTION_COLUMNS]


def write_processed_dataset(
    transactions: pd.DataFrame,
    path: Path = PROCESSED_TRANSACTIONS_PATH,
) -> Path:
    """Write the clean layer atomically as Parquet."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_name(f".{path.stem}.tmp{path.suffix}")

    try:
        transactions.to_parquet(
            temporary_path,
            index=False,
            engine="pyarrow",
        )
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return path


def build_clean_dataset(
    input_path: Path = RAW_WORKBOOK_PATH,
    output_path: Path = PROCESSED_TRANSACTIONS_PATH,
) -> pd.DataFrame:
    """Run the raw-to-clean transformation and persist the result."""
    raw = load_raw_transactions(input_path)
    clean = transform_transactions(raw)
    write_processed_dataset(clean, output_path)
    return clean


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transform the validated retail workbook into clean Parquet."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=RAW_WORKBOOK_PATH,
        help="Path to the validated raw workbook.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROCESSED_TRANSACTIONS_PATH,
        help="Path for the clean Parquet dataset.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        clean = build_clean_dataset(args.input, args.output)
    except (DatasetValidationError, TransformationError, OSError) as exc:
        print(f"Transformation error: {exc}")
        return 1

    cancellations = int(clean["is_cancellation"].sum())
    missing_customers = int(clean["customer_id"].isna().sum())

    print(f"Clean dataset ready: {args.output}")
    print(f"- rows: {len(clean):,}")
    print(f"- cancellations: {cancellations:,}")
    print(f"- rows without customer ID: {missing_customers:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
