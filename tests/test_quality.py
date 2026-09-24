import pytest

from retail_analytics.quality import (
    DataQualityError,
    QualityCheckResult,
    assert_quality,
)


def test_quality_check_result_passes_only_with_zero_failures():
    assert QualityCheckResult("example", 0).passed
    assert not QualityCheckResult("example", 1).passed


def test_assert_quality_accepts_all_passing_checks():
    results = (
        QualityCheckResult("first", 0),
        QualityCheckResult("second", 0),
    )

    assert_quality(results)


def test_assert_quality_reports_all_failures():
    results = (
        QualityCheckResult("first", 2),
        QualityCheckResult("second", 0),
        QualityCheckResult("third", 1),
    )

    with pytest.raises(
        DataQualityError,
        match=r"first=2.*third=1",
    ):
        assert_quality(results)
