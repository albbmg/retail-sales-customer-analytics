from decimal import Decimal

from retail_analytics.profile import _markdown_table, _percentage


def test_markdown_table_formats_rows():
    table = _markdown_table(
        ("Name", "Value"),
        [("Example", Decimal("12.50"))],
    )

    assert "| Name | Value |" in table
    assert "| Example | 12.50 |" in table


def test_percentage_formats_decimal_ratio():
    assert _percentage(Decimal("0.1234")) == "12.34%"
