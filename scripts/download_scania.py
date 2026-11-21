"""Download ONLY original SCANIA Component X version-2 CSVs from SND.

Uses the exact user-supplied Researchdata record and an SND catalogue fallback.
If both official routes fail, STOP and use the source webpage's browser download.
No fake rows, replacement records, or automatic alternative datasets.
"""
from __future__ import annotations

import argparse
import csv
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.preprocessing.audit_scania import FILES, digest

DATASET_PAGE = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
API_BASE = "https://api.researchdata.se/dataset/2024-34/2/file/data"
SND_CATALOGUE_BASE = "https://snd.se/en/catalogue/download/dataset/2024-34/2"


def source_urls(name: str) -> list[str]:
    # Both URLs belong to the SAME user-supplied SCANIA dataset v2.
    return [
        API_BASE + "?" + urlencode({"filePath": name}),
        SND_CATALOGUE_BASE + "?" + urlencode({"filename": name}),
    ]


def validate_header(name: str, header: list[str]) -> None:
    actual = set(header)
    if name.endswith("_operational_readouts.csv"):
        required = {"vehicle_id", "time_step"}
    elif name.endswith("_specifications.csv"):
        required = {f"Spec_{i}" for i in range(8)}
    elif name == "train_tte.csv":
        required = {"length_of_study_time_step", "in_study_repair"}
    elif name.endswith("_labels.csv"):
        required = {"class_label"}
    else:
        raise ValueError(f"Unexpected SCANIA file name: {name}")
    if not required.issubset(actual):
        raise ValueError(f"Downloaded {name} is not the expected SCANIA table; columns={header}")


def download(output: Path, names: list[str]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name in names:
        if name not in FILES:
            raise ValueError(f"File not listed in the original SCANIA v2 source: {name}")
        dest = output / name
        if dest.exists():
            print(f"Existing file kept unchanged: {name}; SHA256={digest(dest)}")
            continue
        temp = dest.with_suffix(".csv.partial")
        errors = []
        for url in source_urls(name):
            temp.unlink(missing_ok=True)
            print(f"Trying official SND route for {name}: {url}", flush=True)
            request = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (academic research dataset download)",
                "Accept": "text/csv,application/octet-stream,*/*",
            })
            try:
                with urllib.request.urlopen(request, timeout=120) as src, temp.open("wb") as out:
                    print(f"Source response: HTTP {src.status}; final URL: {src.geturl()}", flush=True)
                    while chunk := src.read(1024 * 1024):
                        out.write(chunk)
                if temp.stat().st_size == 0:
                    raise ValueError("Empty response")
                with temp.open("r", encoding="utf-8-sig", newline="") as stream:
                    first_row = next(csv.reader(stream), [])
                validate_header(name, first_row)
                temp.rename(dest)
                print(f"Original source saved: {name}; SHA256={digest(dest)}")
                print("Hash computed locally for traceability; official hash verification pending.")
                break
            except (OSError, UnicodeError, ValueError, urllib.error.HTTPError,
                    urllib.error.URLError) as exc:
                errors.append(f"{url} -> {type(exc).__name__}: {exc}")
                print(f"Official download attempt failed: {errors[-1]}", flush=True)
                temp.unlink(missing_ok=True)
        else:
            raise RuntimeError(
                f"Could not retrieve original SCANIA file {name} from either SND route.\n"
                + "\n".join(errors)
                + f"\nDownload the exact original CSV through your browser from {DATASET_PAGE}, "
                  f"save it to {dest}, and run the existing audit script locally. "
                  "Do not invent or substitute any records."
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/scania"))
    parser.add_argument("--only", nargs="+", choices=sorted(FILES),
                        help="Try one or more original source CSVs first")
    args = parser.parse_args()
    download(args.output, args.only or list(FILES))


if __name__ == "__main__":
    main()
