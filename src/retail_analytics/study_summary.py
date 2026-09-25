import argparse
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

from .config import PROJECT_ROOT
from .database import DatabaseConfigError, DatabaseSettings

ANALYSIS_DIR = PROJECT_ROOT / "sql/analysis"


class StudySummaryError(RuntimeError):
    """Raised when the validated study summary cannot be generated."""


def _read_query(filename: str) -> str:
    path = ANALYSIS_DIR / filename

    if not path.is_file():
        raise StudySummaryError(f"Analysis SQL file not found: {path}")

    query = path.read_text(encoding="utf-8").strip()
    if not query:
        raise StudySummaryError(f"Analysis SQL file is empty: {path}")

    return query


def _fetch_all(cursor: psycopg.Cursor, filename: str) -> list[tuple[Any, ...]]:
    cursor.execute(_read_query(filename))
    return cursor.fetchall()


def _single_row(rows: list[tuple[Any, ...]], label: str) -> tuple[Any, ...]:
    if len(rows) != 1:
        raise StudySummaryError(f"{label} must return exactly one row")
    return rows[0]


def _currency(value: Any) -> str:
    if value is None:
        return "—"
    return f"£{Decimal(value):,.2f}"


def _percentage(value: Any) -> str:
    if value is None:
        return "—"
    return f"{Decimal(value) * 100:.2f}%"


def _integer(value: Any) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}"


def _growth(current: Any, previous: Any) -> Decimal | None:
    if current is None or previous in (None, 0):
        return None

    current_decimal = Decimal(current)
    previous_decimal = Decimal(previous)
    return (current_decimal - previous_decimal) / previous_decimal


def _markdown_table(
    headers: tuple[str, ...],
    rows: list[tuple[str, ...]],
) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def build_study_summary(
    *,
    settings: DatabaseSettings | None = None,
    top_n: int = 10,
) -> str:
    if top_n < 1:
        raise StudySummaryError("top_n must be at least 1")

    database_settings = settings or DatabaseSettings.from_environment()

    with psycopg.connect(**database_settings.connect_kwargs()) as connection:
        with connection.cursor() as cursor:
            overview = _single_row(
                _fetch_all(cursor, "01_kpi_overview.sql"),
                "KPI overview",
            )
            monthly = _fetch_all(cursor, "02_monthly_sales.sql")
            products = _fetch_all(
                cursor,
                "04_product_performance.sql",
            )[:top_n]
            operational = _fetch_all(
                cursor,
                "07_operational_stock_codes.sql",
            )[:top_n]
            comparable = _fetch_all(cursor, "08_comparable_periods.sql")
            concentration = _single_row(
                _fetch_all(cursor, "09_customer_concentration.sql"),
                "Customer concentration",
            )
            geography = _single_row(
                _fetch_all(cursor, "10_geographic_concentration.sql"),
                "Geographic concentration",
            )
            unknown_customer = _single_row(
                _fetch_all(cursor, "11_unknown_customer_impact.sql"),
                "Unknown-customer impact",
            )
            product_types = _fetch_all(cursor, "12_product_type_impact.sql")

    if len(comparable) != 2:
        raise StudySummaryError(
            "Comparable-period query must return exactly two rows"
        )

    period_by_label = {row[0]: row for row in comparable}
    period_2010 = period_by_label.get("2010 Jan-Nov")
    period_2011 = period_by_label.get("2011 Jan-Nov")
    if period_2010 is None or period_2011 is None:
        raise StudySummaryError("Comparable-period labels are missing")

    (
        net_revenue,
        non_cancellation_revenue,
        sales_orders,
        units_sold,
        average_order_value,
        active_customers,
        net_revenue_per_customer,
        cancellation_invoice_rate,
    ) = overview

    complete_months = [
        row for row in monthly if row[0] < date(2011, 12, 1)
    ]
    top_months = sorted(
        complete_months,
        key=lambda row: (row[1], row[0]),
        reverse=True,
    )[:5]

    net_revenue_growth = _growth(period_2011[1], period_2010[1])
    order_growth = _growth(period_2011[3], period_2010[3])
    customer_growth = _growth(period_2011[5], period_2010[5])
    aov_growth = _growth(period_2011[6], period_2010[6])

    (
        active_customer_net_revenue,
        top_1_net_revenue,
        top_10_net_revenue,
        top_100_net_revenue,
        top_1_share,
        top_10_share,
        top_100_share,
    ) = concentration

    (
        total_geographic_revenue,
        uk_net_revenue,
        uk_share,
        top_5_country_share,
    ) = geography

    (
        unknown_customer_lines,
        unknown_line_share,
        unknown_net_revenue,
        unknown_revenue_share,
        unknown_sales_orders,
    ) = unknown_customer

    comparable_rows = [
        (
            str(row[0]),
            _currency(row[1]),
            _integer(row[3]),
            _integer(row[4]),
            _integer(row[5]),
            _currency(row[6]),
            _percentage(row[7]),
        )
        for row in comparable
    ]

    top_month_rows = [
        (
            row[0].isoformat(),
            _currency(row[1]),
            _integer(row[3]),
            _integer(row[5]),
            _currency(row[6]),
        )
        for row in top_months
    ]

    product_rows = [
        (
            str(row[0]),
            str(row[1]).strip(),
            _currency(row[2]),
            _integer(row[3]),
            _integer(row[4]),
            _currency(row[5]),
        )
        for row in products
    ]

    operational_rows = [
        (
            str(row[0]),
            str(row[1]),
            str(row[2]).strip(),
            _integer(row[3]),
            _currency(row[5]),
            _currency(row[6]),
        )
        for row in operational
    ]

    product_type_rows = [
        (
            str(row[0]),
            _integer(row[1]),
            _integer(row[2]),
            _currency(row[3]),
            _currency(row[4]),
            _currency(row[5]),
        )
        for row in product_types
    ]

    sections = [
        "# Validated study summary",
        "",
        "This file is generated from the analytical PostgreSQL model after "
        "the full Online Retail II pipeline has completed and passed the "
        "versioned data-quality checks.",
        "",
        "## Overall scale",
        "",
        f"- Net revenue: **{_currency(net_revenue)}**",
        f"- Non-cancellation revenue: **{_currency(non_cancellation_revenue)}**",
        f"- Sales orders: **{_integer(sales_orders)}**",
        f"- Units sold: **{_integer(units_sold)}**",
        f"- Average order value: **{_currency(average_order_value)}**",
        f"- Active customers: **{_integer(active_customers)}**",
        "- Net revenue per active customer: "
        f"**{_currency(net_revenue_per_customer)}**",
        "- Cancellation invoice rate: "
        f"**{_percentage(cancellation_invoice_rate)}**",
        "- Signed revenue difference associated with cancellation invoices: "
        f"**{_currency(non_cancellation_revenue - net_revenue)}**",
        "",
        "## Comparable trading periods",
        "",
        "The dataset ends on 9 December 2011, so year-on-year comparison "
        "uses January-November for both years.",
        "",
        _markdown_table(
            (
                "Period",
                "Net revenue",
                "Sales orders",
                "Units sold",
                "Active customers",
                "Average order value",
                "Cancellation invoice rate",
            ),
            comparable_rows,
        ),
        "",
        "2011 Jan-Nov change versus 2010 Jan-Nov:",
        "",
        f"- Net revenue: **{_percentage(net_revenue_growth)}**",
        f"- Sales orders: **{_percentage(order_growth)}**",
        f"- Active customers: **{_percentage(customer_growth)}**",
        f"- Average order value: **{_percentage(aov_growth)}**",
        "",
        "## Highest-revenue complete months",
        "",
        "December 2011 is excluded because the source ends on 9 December.",
        "",
        _markdown_table(
            (
                "Month",
                "Net revenue",
                "Sales orders",
                "Active customers",
                "Average order value",
            ),
            top_month_rows,
        ),
        "",
        "## Customer concentration",
        "",
        "- Net revenue attributable to the active identified-customer "
        f"population: **{_currency(active_customer_net_revenue)}**",
        f"- Top customer: **{_currency(top_1_net_revenue)}** "
        f"({_percentage(top_1_share)})",
        f"- Top 10 customers: **{_currency(top_10_net_revenue)}** "
        f"({_percentage(top_10_share)})",
        f"- Top 100 customers: **{_currency(top_100_net_revenue)}** "
        f"({_percentage(top_100_share)})",
        "",
        "## Geographic concentration",
        "",
        f"- Total net revenue: **{_currency(total_geographic_revenue)}**",
        f"- United Kingdom net revenue: **{_currency(uk_net_revenue)}** "
        f"({_percentage(uk_share)})",
        f"- Top five countries' share: **{_percentage(top_5_country_share)}**",
        "",
        "## Missing customer identifiers",
        "",
        f"- Transaction lines mapped to Unknown customer: "
        f"**{_integer(unknown_customer_lines)}** "
        f"({_percentage(unknown_line_share)})",
        f"- Net revenue mapped to Unknown customer: "
        f"**{_currency(unknown_net_revenue)}** "
        f"({_percentage(unknown_revenue_share)})",
        f"- Non-cancellation invoices with Unknown customer: "
        f"**{_integer(unknown_sales_orders)}**",
        "",
        "## Revenue by product type",
        "",
        _markdown_table(
            (
                "Product type",
                "Lines",
                "Invoices",
                "Net revenue",
                "Non-cancellation revenue",
                "Cancellation value",
            ),
            product_type_rows,
        ),
        "",
        f"## Top {top_n} merchandise products by net revenue",
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
            product_rows,
        ),
        "",
        f"## Top {top_n} operational entries by absolute impact",
        "",
        _markdown_table(
            (
                "Type",
                "Stock code",
                "Description",
                "Lines",
                "Net revenue",
                "Cancellation value",
            ),
            operational_rows,
        ),
        "",
        "## Interpretation boundaries",
        "",
        "- These are descriptive transaction-level observations, not causal "
        "estimates.",
        "- The source does not contain product cost, so revenue must not be "
        "read as profit.",
        "- Cancellation invoices are separate records; their rate is not a "
        "matched-order cancellation probability.",
        "- Customer-level conclusions exclude the explicit Unknown customer "
        "from customer counts, while its revenue remains in overall totals.",
        "- Merchandise rankings exclude operational stock codes by the "
        "documented product classification.",
        "",
    ]

    return "\n".join(sections)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the validated analytical study summary."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("validation/study_summary.md"),
        help="Markdown output path.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of merchandise and operational rows to include.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        summary = build_study_summary(top_n=args.top)
    except (
        DatabaseConfigError,
        OSError,
        psycopg.Error,
        StudySummaryError,
    ) as exc:
        print(f"Study summary error: {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summary, encoding="utf-8")
    print(f"Study summary written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
