import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg

from .config import (
    CLEAN_TRANSACTION_COLUMNS,
    PROCESSED_TRANSACTIONS_PATH,
    STAGING_SCHEMA_SQL_PATH,
)
from .database import DatabaseConfigError, DatabaseSettings

COPY_SQL = """
COPY staging.transactions (
    invoice_no,
    stock_code,
    description,
    quantity,
    invoice_date,
    unit_price,
    customer_id,
    country,
    source_period,
    source_row,
    is_cancellation,
    line_amount
)
FROM STDIN
"""


class LoadError(RuntimeError):
    """Raised when the clean dataset cannot be loaded safely."""


@dataclass(frozen=True)
class LoadResult:
    source_rows: int
    loaded_rows: int


def validate_clean_dataset(transactions: pd.DataFrame) -> None:
    """Validate the clean-layer contract before touching the database."""
    actual_columns = tuple(transactions.columns)
    if actual_columns != CLEAN_TRANSACTION_COLUMNS:
        raise LoadError(
            "Unexpected clean dataset columns. "
            f"Expected {CLEAN_TRANSACTION_COLUMNS!r}, found {actual_columns!r}"
        )

    if transactions.empty:
        raise LoadError("Clean dataset is empty")

    lineage_columns = ["source_period", "source_row"]
    if transactions[lineage_columns].isna().any().any():
        raise LoadError("Source lineage contains null values")

    if transactions.duplicated(lineage_columns).any():
        raise LoadError("Source lineage contains duplicate rows")

    if transactions["invoice_date"].isna().any():
        raise LoadError("invoice_date contains null values")


def read_clean_dataset(path: Path = PROCESSED_TRANSACTIONS_PATH) -> pd.DataFrame:
    path = Path(path)

    if not path.is_file():
        raise LoadError(f"Clean dataset not found: {path}")

    try:
        transactions = pd.read_parquet(path, engine="pyarrow")
    except (OSError, ValueError) as exc:
        raise LoadError(f"Could not read clean dataset: {path}") from exc

    validate_clean_dataset(transactions)
    return transactions


def _read_sql_script(path: Path) -> list[str]:
    path = Path(path)

    if not path.is_file():
        raise LoadError(f"SQL schema file not found: {path}")

    statements = [
        statement.strip()
        for statement in path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]

    if not statements:
        raise LoadError(f"SQL schema file is empty: {path}")

    return statements


def _normalize_value(value: Any) -> Any:
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if hasattr(value, "item"):
        return value.item()

    return value


def load_transactions(
    input_path: Path = PROCESSED_TRANSACTIONS_PATH,
    *,
    settings: DatabaseSettings | None = None,
    schema_path: Path = STAGING_SCHEMA_SQL_PATH,
) -> LoadResult:
    """Full-refresh the PostgreSQL staging table inside one transaction."""
    transactions = read_clean_dataset(input_path)
    source_rows = len(transactions)
    database_settings = settings or DatabaseSettings.from_environment()
    schema_statements = _read_sql_script(schema_path)

    with psycopg.connect(**database_settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            for statement in schema_statements:
                cursor.execute(statement)

            cursor.execute("TRUNCATE TABLE staging.transactions")

            with cursor.copy(COPY_SQL) as copy:
                for row in transactions.itertuples(index=False, name=None):
                    copy.write_row(tuple(_normalize_value(value) for value in row))

            cursor.execute("SELECT COUNT(*) FROM staging.transactions")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != source_rows:
                raise LoadError(
                    "Staging row-count mismatch: "
                    f"source={source_rows}, loaded={loaded_rows}"
                )

    return LoadResult(source_rows=source_rows, loaded_rows=loaded_rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load clean retail transactions into PostgreSQL staging."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROCESSED_TRANSACTIONS_PATH,
        help="Path to the clean Parquet dataset.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = load_transactions(args.input)
    except (DatabaseConfigError, LoadError, OSError, psycopg.Error) as exc:
        print(f"Load error: {exc}")
        return 1

    print("PostgreSQL staging load complete")
    print(f"- source rows: {result.source_rows:,}")
    print(f"- loaded rows: {result.loaded_rows:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
