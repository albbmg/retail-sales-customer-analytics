from io import BytesIO
from zipfile import ZipFile

import pytest

from retail_analytics import extract
from retail_analytics.extract import DatasetDownloadError, download_dataset


def make_archive(member_name="online_retail_II.xlsx", payload=b"workbook"):
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr(member_name, payload)
    return buffer.getvalue()


def test_download_dataset_extracts_expected_workbook(tmp_path, monkeypatch):
    archive_bytes = make_archive()
    monkeypatch.setattr(
        extract,
        "urlopen",
        lambda *_args, **_kwargs: BytesIO(archive_bytes),
    )
    destination = tmp_path / "data" / "raw" / "online_retail_II.xlsx"

    result = download_dataset("https://example.test/data.zip", destination)

    assert result == destination
    assert destination.read_bytes() == b"workbook"


def test_download_dataset_keeps_existing_file_without_network(tmp_path, monkeypatch):
    destination = tmp_path / "online_retail_II.xlsx"
    destination.write_bytes(b"existing")

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("network should not be called")

    monkeypatch.setattr(extract, "urlopen", fail_if_called)

    result = download_dataset("https://example.test/data.zip", destination)

    assert result == destination
    assert destination.read_bytes() == b"existing"


def test_download_dataset_rejects_archive_without_workbook(tmp_path, monkeypatch):
    archive_bytes = make_archive(member_name="other.xlsx")
    monkeypatch.setattr(
        extract,
        "urlopen",
        lambda *_args, **_kwargs: BytesIO(archive_bytes),
    )
    destination = tmp_path / "online_retail_II.xlsx"

    with pytest.raises(DatasetDownloadError, match="does not contain"):
        download_dataset("https://example.test/data.zip", destination)
