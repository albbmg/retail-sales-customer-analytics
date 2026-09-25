import argparse
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from .config import PROFILE_SOURCE_SQL_PATH, PROJECT_ROOT
from .database import DatabaseConfigError, DatabaseSettings

ANALYSIS_DIR = PROJECT_ROOT / "sql/analysis"
PROFILE_DIR = PROJECT_ROOT / "sql/profile"

ANALYSIS_FILES = {
    "overview": "01_kpi_overview.sql",
    "customers": "03_customer_performance.sql",
    "products": "04_product_performance.sql",
    "countries": "05_country_performance.sql",
}


class ProfileError(RuntimeError):
    """Raised when the reproducible real-data profile cannot be generated."""


def _read_query(path: Path) -> str:
    path = Path(path)

    if not path.is_file():
        raise ProfileError(f"SQL profile query not found: {path}")

    query = path.read_text(encoding="utf-8").strip()
    if not query:
        raise ProfileError(f"SQL profile query is empty: {path}")

    return query


def _fetch_all(cursor: psycopg.Cursor, path: Path) -> list[tuple[Any, ...]]:
    cursor.execute(_read_query(path))
    return cursor.fetchall()


def _format_value(value: Any) -> str:
    if value is None:
        return "—"

    if isinstance(value, Decimal):
        return f"{value:,}"

    return str(value)


def _markdown_table(headers: tuple[str, ...], rows: list[tuple[Any, ...]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join(_format_value(value) for value in row) + " |" for row in rows
    ]
    return "\n".join([header, separator, *body])


def _currency(value: Decimal | int | float | None) -> str:
    if value is None:
        return "—"
    return f"£{Decimal(value):,.2f}"


def _percentage(value: Decimal | int | float | None) -> str:
    if value is None:
        return "—"
    return f"{Decimal(value) * 100:.2f}%"


def build_profile(
    *,
    settings: DatabaseSettings | None = None,
    top_n: int = 10,
) -> str:
    database_settings = settings or DatabaseSettings.from_environment()

    if top_n < 1:
        raise ProfileError("top_n must be at least 1")

    with psycopg.connect(**database_settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            source_rows = _fetch_all(cursor, PROFILE_SOURCE_SQL_PATH)
            if len(source_rows) != 1:
                raise ProfileError("Source profile query must return exactly one row")

            overview_rows = _fetch_all(
                cursor,
                ANALYSIS_DIR / ANALYSIS_FILES["overview"],
            )
            if len(overview_rows) != 1:
                raise ProfileError("KPI overview query must return exactly one row")

            customers = _fetch_all(
                cursor,
                ANALYSIS_DIR / ANALYSIS_FILES["customers"],
            )[:top_n]
            products = _fetch_all(
                cursor,
                ANALYSIS_DIR / ANALYSIS_FILES["products"],
            )[:top_n]
            countries = _fetch_all(
                cursor,
                ANALYSIS_DIR / ANALYSIS_FILES["countries"],
            )[:top_n]
            non_numeric_stock_codes = _fetch_all(
                cursor,
                PROFILE_DIR / "02_non_numeric_stock_codes.sql",
            )

    (
        staging_rows,
        distinct_invoices,
        first_invoice,
        last_invoice,
        missing_customer_lines,
        missing_customer_rate,
        missing_description_lines,
        missing_country_lines,
        missing_stock_code_lines,
        zero_price_lines,
        negative_price_lines,
        negative_quantity_non_cancel,
        cancellation_lines,
        cancellation_invoices,
        identified_customers,
        distinct_stock_codes,
        distinct_countries,
    ) = source_rows[0]

    (
        net_revenue,
        non_cancellation_revenue,
        sales_orders,
        units_sold,
        average_order_value,
        active_customers,
        net_revenue_per_active_customer,
        cancellation_invoice_rate,
    ) = overview_rows[0]

    sections = [
        "# Full dataset validation snapshot",
        "",
        "Generated from the complete UCI Online Retail II dataset after the "
        "raw → clean → staging → analytics pipeline completed successfully.",
        "",
        "## Dataset coverage",
        "",
        f"- Transaction lines: **{staging_rows:,}**",
        f"- Distinct invoice numbers: **{distinct_invoices:,}**",
        f"- First transaction: **{first_invoice}**",
        f"- Last transaction: **{last_invoice}**",
        f"- Identified customers: **{identified_customers:,}**",
        f"- Distinct stock codes: **{distinct_stock_codes:,}**",
        f"- Distinct countries: **{distinct_countries:,}**",
        "",
        "## Source characteristics relevant to interpretation",
        "",
        f"- Lines without customer ID: **{missing_customer_lines:,}** "
        f"({_percentage(missing_customer_rate)})",
        f"- Lines without description: **{missing_description_lines:,}**",
        f"- Lines without country: **{missing_country_lines:,}**",
        f"- Lines without stock code: **{missing_stock_code_lines:,}**",
        f"- Zero-price lines: **{zero_price_lines:,}**",
        f"- Negative-price lines: **{negative_price_lines:,}**",
        "- Negative-quantity lines not flagged as cancellation invoices: "
        f"**{negative_quantity_non_cancel:,}**",
        f"- Cancellation lines: **{cancellation_lines:,}**",
        f"- Distinct cancellation invoices: **{cancellation_invoices:,}**",
        "",
        "## Core KPIs",
        "",
        f"- Net revenue: **{_currency(net_revenue)}**",
        f"- Non-cancellation revenue: **{_currency(non_cancellation_revenue)}**",
        f"- Sales orders: **{sales_orders:,}**",
        f"- Units sold: **{units_sold:,}**",
        f"- Average order value: **{_currency(average_order_value)}**",
        f"- Active customers: **{active_customers:,}**",
        "- Net revenue per active customer: "
        f"**{_currency(net_revenue_per_active_customer)}**",
        f"- Cancellation invoice rate: **{_percentage(cancellation_invoice_rate)}**",
        "",
        f"## Top {top_n} identified customers by net revenue",
        "",
        _markdown_table(
            (
                "Customer ID",
                "Label",
                "First purchase",
                "Last purchase",
                "Net revenue",
                "Sales orders",
                "Units sold",
                "Average order value",
                "Cancellation invoices",
            ),
            customers,
        ),
        "",
        f"## Top {top_n} products by net revenue",
        "",
        _markdown_table(
            (
                "Stock code",
                "Description",
                "Net revenue",
                "Sales orders",
                "Units sold",
                "Cancellation value",
            ),
            products,
        ),
        "",
        "## Non-numeric-leading stock codes",
        "",
        "These codes are profiled separately because operational charges and "
        "adjustments can otherwise appear in product rankings.",
        "",
        _markdown_table(
            (
                "Stock code",
                "Canonical description",
                "Transaction lines",
                "Invoices",
                "Net revenue",
            ),
            non_numeric_stock_codes,
        ),
        "",
        f"## Top {top_n} countries by net revenue",
        "",
        _markdown_table(
            (
                "Country",
                "Net revenue",
                "Non-cancellation revenue",
                "Sales orders",
                "Active customers",
                "Cancellation invoices",
            ),
            countries,
        ),
        "",
    ]

    return "\n".join(sections)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown snapshot of the full analytical dataset."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("validation/real_data_profile.md"),
        help="Markdown output path.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of rows to include in ranked sections.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        profile = build_profile(top_n=args.top)
    except (DatabaseConfigError, ProfileError, OSError, psycopg.Error) as exc:
        print(f"Profile error: {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(profile, encoding="utf-8")
    print(f"Profile written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
