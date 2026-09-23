import argparse
from pathlib import Path
from shutil import copyfileobj
from urllib.error import URLError
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

from .config import DATASET_ARCHIVE_URL, RAW_WORKBOOK_PATH
from .validation import DatasetValidationError, validate_workbook


class DatasetDownloadError(RuntimeError):
    """Raised when the source archive cannot be downloaded or extracted."""


def download_dataset(
    source_url: str = DATASET_ARCHIVE_URL,
    destination: Path = RAW_WORKBOOK_PATH,
    *,
    force: bool = False,
) -> Path:
    """Download the official UCI archive and extract the source workbook."""
    destination = Path(destination)

    if destination.exists() and not force:
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)

    archive_path = destination.parent / f".{destination.name}.download.zip"
    temporary_workbook = destination.parent / f".{destination.name}.tmp"
    request = Request(
        source_url,
        headers={"User-Agent": "retail-sales-customer-analytics/0.1"},
    )

    try:
        with (
            urlopen(request, timeout=120) as response,
            archive_path.open("wb") as archive_file,
        ):
            copyfileobj(response, archive_file)

        with ZipFile(archive_path) as archive:
            matching_members = [
                member
                for member in archive.namelist()
                if Path(member).name == destination.name
            ]

            if len(matching_members) != 1:
                raise DatasetDownloadError(
                    "The UCI archive does not contain exactly one "
                    f"{destination.name!r} workbook"
                )

            with (
                archive.open(matching_members[0]) as source,
                temporary_workbook.open("wb") as target,
            ):
                copyfileobj(source, target)

        temporary_workbook.replace(destination)
        return destination
    except (BadZipFile, OSError, URLError) as exc:
        raise DatasetDownloadError(
            f"Could not download or extract dataset from {source_url}"
        ) from exc
    finally:
        archive_path.unlink(missing_ok=True)
        temporary_workbook.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and validate the UCI Online Retail II dataset."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download the workbook again even when it already exists.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        workbook_path = download_dataset(force=args.force)
        summary = validate_workbook(workbook_path)
    except (DatasetDownloadError, DatasetValidationError) as exc:
        print(f"Dataset error: {exc}")
        return 1

    print(f"Dataset ready: {summary.path}")
    for sheet in summary.sheets:
        print(f"- {sheet.name}: {sheet.data_rows:,} rows")
    print(f"Total rows: {summary.total_rows:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
