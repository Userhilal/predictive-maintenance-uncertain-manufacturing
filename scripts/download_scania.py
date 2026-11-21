"""Download official SCANIA Component X v3 CSVs with integrity checks.

Run from the repository root:
    python scripts/download_scania.py --output data/raw/scania
Use --only train_tte.csv for a single-file trial. No originals are modified.
"""
from __future__ import annotations
import argparse
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.preprocessing.audit_scania import CHECKSUMS, digest

BASE = 'https://api.researchdata.se/dataset/2024-34/3/file/data/'

def download(output: Path, names: list[str]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for name in names:
        if name not in CHECKSUMS:
            raise ValueError(f'Unrecognized file: {name}')
        dest = output / name
        if dest.exists() and digest(dest) == CHECKSUMS[name]:
            print(f'OK existing: {name}')
            continue
        if dest.exists():
            raise ValueError(f'Existing file failed SHA-256; refusing to overwrite: {dest}')
        temp = dest.with_suffix(dest.suffix + '.partial')
        req = urllib.request.Request(BASE + name, headers={'User-Agent': 'AcademicPdMDataAudit/1.0'})
        print(f'Downloading {name} from the official archive...')
        try:
            with urllib.request.urlopen(req, timeout=90) as src, temp.open('wb') as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
            actual = digest(temp)
            if actual != CHECKSUMS[name]:
                raise ValueError(f'SHA-256 mismatch for {name}: {actual}. Check source version.')
            temp.rename(dest)
            print(f'Verified: {name}')
        except Exception:
            temp.unlink(missing_ok=True)
            raise

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=Path('data/raw/scania'))
    ap.add_argument('--only', nargs='+', choices=sorted(CHECKSUMS), help='Only download selected files')
    args = ap.parse_args()
    download(args.output, args.only or list(CHECKSUMS))

if __name__ == '__main__':
    main()
