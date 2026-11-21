"""Download unmodified SCANIA v2 files ONLY from the user-supplied Researchdata source.

The tool does not fabricate observations and does not claim checksum verification
against an unavailable official provider manifest. All output is source CSV bytes.
"""
from __future__ import annotations

import argparse
import csv
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.preprocessing.audit_scania import FILES, digest

BASE = "https://api.researchdata.se/dataset/2024-34/2/file/data/"


def download(output: Path, names: list[str]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name in names:
        if name not in FILES:
            raise ValueError(f"File not listed in SCANIA source: {name}")
        dest = output / name
        if dest.exists():
            print(f"Existing source file kept unchanged: {name}; SHA256={digest(dest)}")
            continue
        temp = dest.with_suffix(".csv.partial")
        request = urllib.request.Request(BASE + name, headers={"User-Agent": "ResearchData-Audit/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=120) as src, temp.open("wb") as out:
                while chunk := src.read(1024 * 1024):
                    out.write(chunk)
            if temp.stat().st_size == 0:
                raise ValueError(f"Empty downloaded source file: {name}")
            with temp.open("r", encoding="utf-8-sig", newline="") as stream:
                header = next(csv.reader(stream), [])
            if "vehicle_id" not in header:
                raise ValueError(f"Response is not expected SCANIA CSV: {name}")
            temp.rename(dest)
            print(f"Downloaded original source file: {name}; SHA256={digest(dest)}")
            print("SHA256 computed for traceability, not independently verified against official provider hash.")
        except Exception:
            temp.unlink(missing_ok=True)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/raw/scania"))
    parser.add_argument("--only", nargs="+", choices=sorted(FILES))
    args = parser.parse_args()
    download(args.output, args.only or list(FILES))


if __name__ == "__main__":
    main()
