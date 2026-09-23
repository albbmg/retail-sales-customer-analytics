from datetime import datetime

import pytest
from openpyxl import Workbook

from retail_analytics.config import EXPECTED_COLUMNS, EXPECTED_SHEETS
from retail_analytics.validation import DatasetValidationError, validate_workbook


def create_workbook(path, *, sheets=EXPECTED_SHEETS, columns=EXPECTED_COLUMNS):
    workbook = Workbook()
    workbook.remove(workbook.active)

    for sheet_name in sheets:
        worksheet = workbook.create_sheet(sheet_name)
        worksheet.append(columns)
        worksheet.append(
            (
                "489434",
                "85048",
                "15CM CHRISTMAS GLASS BALL 20 LIGHTS",
                12,
                datetime(2009, 12, 1, 7, 45),
                6.95,
                13085,
                "United Kingdom",
            )
        )

    workbook.save(path)


def test_validate_workbook_accepts_expected_structure(tmp_path):
    workbook_path = tmp_path / "online_retail_II.xlsx"
    create_workbook(workbook_path)

    summary = validate_workbook(workbook_path)

    assert [sheet.name for sheet in summary.sheets] == list(EXPECTED_SHEETS)
    assert summary.total_rows == 2


def test_validate_workbook_rejects_missing_sheet(tmp_path):
    workbook_path = tmp_path / "online_retail_II.xlsx"
    create_workbook(workbook_path, sheets=EXPECTED_SHEETS[:1])

    with pytest.raises(DatasetValidationError, match="Missing required sheet"):
        validate_workbook(workbook_path)


def test_validate_workbook_rejects_unexpected_columns(tmp_path):
    workbook_path = tmp_path / "online_retail_II.xlsx"
    wrong_columns = (*EXPECTED_COLUMNS[:-1], "Region")
    create_workbook(workbook_path, columns=wrong_columns)

    with pytest.raises(DatasetValidationError, match="Unexpected columns"):
        validate_workbook(workbook_path)


def test_validate_workbook_rejects_missing_file(tmp_path):
    workbook_path = tmp_path / "missing.xlsx"

    with pytest.raises(DatasetValidationError, match="not found"):
        validate_workbook(workbook_path)
