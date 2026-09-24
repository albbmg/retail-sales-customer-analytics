import argparse
from dataclasses import dataclass
from pathlib import Path

import psycopg

from .config import ANALYTICS_MODEL_SQL_PATH
from .database import DatabaseConfigError, DatabaseSettings


class AnalyticsBuildError(RuntimeError):
    """Raised when the analytical model cannot be built safely."""


@dataclass(frozen=True)
class AnalyticsBuildResult:
    staging_rows: int
    fact_rows: int
    dates: int
    customers: int
    products: int
    countries: int


def _read_sql_script(path: Path) -> list[str]:
    path = Path(path)

    if not path.is_file():
        raise AnalyticsBuildError(f"Analytics SQL file not found: {path}")

    statements = [
        statement.strip()
        for statement in path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]

    if not statements:
        raise AnalyticsBuildError(f"Analytics SQL file is empty: {path}")

    return statements


def build_analytics_model(
    *,
    settings: DatabaseSettings | None = None,
    sql_path: Path = ANALYTICS_MODEL_SQL_PATH,
) -> AnalyticsBuildResult:
    """Rebuild the analytical star schema from PostgreSQL staging."""
    database_settings = settings or DatabaseSettings.from_environment()
    statements = _read_sql_script(sql_path)

    with psycopg.connect(**database_settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM staging.transactions")
            staging_rows = cursor.fetchone()[0]

            if staging_rows == 0:
                raise AnalyticsBuildError(
                    "staging.transactions is empty; load staging before analytics"
                )

            for statement in statements:
                cursor.execute(statement)

            cursor.execute("SELECT COUNT(*) FROM analytics.fact_sales")
            fact_rows = cursor.fetchone()[0]

            if fact_rows != staging_rows:
                raise AnalyticsBuildError(
                    "Analytical fact row-count mismatch: "
                    f"staging={staging_rows}, fact={fact_rows}"
                )

            counts = {}
            for table in (
                "dim_date",
                "dim_customer",
                "dim_product",
                "dim_country",
            ):
                cursor.execute(f"SELECT COUNT(*) FROM analytics.{table}")
                counts[table] = cursor.fetchone()[0]

    return AnalyticsBuildResult(
        staging_rows=staging_rows,
        fact_rows=fact_rows,
        dates=counts["dim_date"],
        customers=counts["dim_customer"],
        products=counts["dim_product"],
        countries=counts["dim_country"],
    )


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Rebuild the PostgreSQL analytical star schema."
    )


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)

    try:
        result = build_analytics_model()
    except (AnalyticsBuildError, DatabaseConfigError, OSError, psycopg.Error) as exc:
        print(f"Analytics build error: {exc}")
        return 1

    print("Analytical model rebuilt")
    print(f"- fact rows: {result.fact_rows:,}")
    print(f"- dates: {result.dates:,}")
    print(f"- customers: {result.customers:,}")
    print(f"- products: {result.products:,}")
    print(f"- countries: {result.countries:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
