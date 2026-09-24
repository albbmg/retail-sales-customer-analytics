import argparse
from dataclasses import dataclass
from pathlib import Path

import psycopg

from .config import QUALITY_CHECKS_SQL_PATH
from .database import DatabaseConfigError, DatabaseSettings


class DataQualityError(RuntimeError):
    """Raised when one or more analytical data-quality checks fail."""


@dataclass(frozen=True)
class QualityCheckResult:
    check_name: str
    failed_rows: int

    @property
    def passed(self) -> bool:
        return self.failed_rows == 0


def run_quality_checks(
    *,
    settings: DatabaseSettings | None = None,
    sql_path: Path = QUALITY_CHECKS_SQL_PATH,
) -> tuple[QualityCheckResult, ...]:
    """Execute the versioned SQL quality checks against the analytical model."""
    sql_path = Path(sql_path)

    if not sql_path.is_file():
        raise DataQualityError(f"Quality-check SQL file not found: {sql_path}")

    query = sql_path.read_text(encoding="utf-8").strip()
    if not query:
        raise DataQualityError(f"Quality-check SQL file is empty: {sql_path}")

    database_settings = settings or DatabaseSettings.from_environment()

    with psycopg.connect(**database_settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    results = tuple(
        QualityCheckResult(check_name=name, failed_rows=int(failed_rows))
        for name, failed_rows in rows
    )

    if not results:
        raise DataQualityError("No data-quality checks were returned")

    return results


def assert_quality(results: tuple[QualityCheckResult, ...]) -> None:
    failures = [result for result in results if not result.passed]

    if failures:
        summary = ", ".join(
            f"{failure.check_name}={failure.failed_rows}" for failure in failures
        )
        raise DataQualityError(f"Analytical data-quality checks failed: {summary}")


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Run SQL data-quality checks against the analytical model."
    )


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)

    try:
        results = run_quality_checks()
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"{status} {result.check_name}: {result.failed_rows}")

        assert_quality(results)
    except (DataQualityError, DatabaseConfigError, OSError, psycopg.Error) as exc:
        print(f"Data quality error: {exc}")
        return 1

    print(f"All {len(results)} analytical data-quality checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
