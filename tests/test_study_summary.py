from decimal import Decimal

from retail_analytics.study_summary import _growth, _percentage


def test_growth_calculates_relative_change():
    result = _growth(Decimal("120"), Decimal("100"))

    assert result == Decimal("0.2")


def test_growth_handles_zero_denominator():
    assert _growth(Decimal("120"), Decimal("0")) is None


def test_percentage_formats_negative_ratio():
    assert _percentage(Decimal("-0.125")) == "-12.50%"
