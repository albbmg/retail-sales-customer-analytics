from pathlib import Path

import pytest

from retail_analytics.analytics import AnalyticsBuildError, _read_sql_script


def test_read_sql_script_splits_statements(tmp_path):
    sql_path = tmp_path / "model.sql"
    sql_path.write_text("SELECT 1;\nSELECT 2;\n", encoding="utf-8")

    assert _read_sql_script(sql_path) == ["SELECT 1", "SELECT 2"]


def test_read_sql_script_rejects_missing_file(tmp_path):
    with pytest.raises(AnalyticsBuildError, match="not found"):
        _read_sql_script(tmp_path / "missing.sql")


def test_read_sql_script_rejects_empty_file(tmp_path):
    sql_path = Path(tmp_path / "empty.sql")
    sql_path.write_text("\n", encoding="utf-8")

    with pytest.raises(AnalyticsBuildError, match="empty"):
        _read_sql_script(sql_path)
