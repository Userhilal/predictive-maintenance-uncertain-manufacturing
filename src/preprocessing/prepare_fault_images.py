"""Non-destructive image audit and provisional splits (Pillow required).

python src/preprocessing/prepare_fault_images.py --input data/raw/industrial_fault_images.zip --output data/processed/fault_images --review-file docs/datasets/fault-image-manual-review.csv

No photos are redistributed. Split proposals are not approved datasets.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import random
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, UnidentifiedImageError

SOURCE_SHA256 = "d30ffdcdcda1258ac95d89dd90539fe7ffd7b398e693ada652b4f63c073c9b28"
CLASSES = ("Crack", "Misalignment", "Normal condition", "Surface defects", "Wear")
ACCEPTED_EXTENSIONS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
MANIFEST_FIELDS = (
    "path", "class", "sha256", "byte_size", "width", "height", "image_format",
    "extension_mismatch", "min_side_under_300", "min_side_under_200",
    "duplicate_group_size", "status", "split", "review_reason", "license_verified",
)

def read_review_queue(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["path", "reason", "review_status"]:
            raise ValueError("Review-file columns must be path,reason,review_status")
        reasons = {}
        for row in reader:
            if row["review_status"] not in ("pending", "approved", "rejected"):
                raise ValueError(f"Invalid review status for {row['path']}")
            if row["path"] in reasons:
                raise ValueError(f"Duplicate manual-review path: {row['path']}")
            if row["review_status"] != "approved":
                reasons[row["path"]] = row["reason"] or row["review_status"]
        return reasons

def read_images(archive: Path, expected_sha256: str | None) -> tuple[list[dict], str]:
    archive_bytes = archive.read_bytes()
    fingerprint = hashlib.sha256(archive_bytes).hexdigest()
    if expected_sha256 and fingerprint.lower() != expected_sha256.lower():
        raise ValueError(f"Unexpected ZIP SHA-256: {fingerprint}; expected {expected_sha256}")
    entries = []
    seen = set()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            path = info.filename
            parts = path.split("/")
            if len(parts) != 3 or parts[0] != "Dataset" or parts[1] not in CLASSES or not parts[2]:
                raise ValueError(f"Unexpected archive structure or unsafe path: {path}")
            if path in seen or "\\" in path or ".." in parts:
                raise ValueError(f"Duplicate or unsafe archive path: {path}")
            seen.add(path)
            ext = Path(path).suffix.lower()
            if ext not in ACCEPTED_EXTENSIONS:
                raise ValueError(f"Unsupported extension: {path}")
            data = z.read(info)
            try:
                with Image.open(io.BytesIO(data)) as im:
                    im.load()
                    fmt, (width, height) = im.format, im.size
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                raise ValueError(f"Unreadable image: {path}") from exc
            if width <= 0 or height <= 0:
                raise ValueError(f"Invalid dimensions: {path}")
            entries.append({
                "path": path, "class": parts[1],
                "sha256": hashlib.sha256(data).hexdigest(),
                "byte_size": len(data), "width": width, "height": height,
                "image_format": fmt, "extension_mismatch": fmt != ACCEPTED_EXTENSIONS[ext],
                "min_side_under_300": min(width, height) < 300,
                "min_side_under_200": min(width, height) < 200,
                "duplicate_group_size": 1, "status": "provisional_candidate", "split": "",
                "review_reason": "", "license_verified": False,
            })
    if not entries:
        raise ValueError("Empty archive")
    return sorted(entries, key=lambda r: r["path"]), fingerprint

def assign_review_status(rows: list[dict], manual_queue: dict[str, str]) -> None:
    path_index = {r["path"] for r in rows}
    if set(manual_queue) - path_index:
        raise ValueError(f"Review file references absent images: {sorted(set(manual_queue) - path_index)}")
    groups = defaultdict(list)
    for row in rows:
        groups[row["sha256"]].append(row)
    for group in groups.values():
        for row in group:
            row["duplicate_group_size"] = len(group)
        if len(group) < 2:
            continue
        if len({r["class"] for r in group}) > 1:
            for row in group:
                row["status"] = "quarantine_conflicting_labels"
                row["review_reason"] = "identical image assigned different classes"
        else:
            for row in sorted(group, key=lambda item: item["path"])[1:]:
                row["status"] = "exclude_same_class_duplicate"
                row["review_reason"] = "exactly same bytes as another image in class"
    for row in rows:
        if row["path"] in manual_queue:
            if row["status"] == "provisional_candidate":
                row["status"] = "quarantine_manual_review"
            row["review_reason"] = (row["review_reason"] + "; " if row["review_reason"] else "") + manual_queue[row["path"]]

def make_provisional_split(rows: list[dict], seed: int = 42) -> None:
    rng = random.Random(seed)
    for label in CLASSES:
        bucket = [r for r in rows if r["class"] == label and r["status"] == "provisional_candidate"]
        bucket.sort(key=lambda r: r["path"])
        rng.shuffle(bucket)
        n_train = (7 * len(bucket) + 5) // 10
        n_validation = (15 * len(bucket) + 50) // 100
        for i, row in enumerate(bucket):
            row["split"] = ("train" if i < n_train else
                            "validation" if i < n_train + n_validation else "test")
    splits_by_hash = defaultdict(set)
    for row in rows:
        if row["split"]:
            splits_by_hash[row["sha256"]].add(row["split"])
    if any(len(splits) > 1 for splits in splits_by_hash.values()):
        raise AssertionError("Exact duplicate leaked between splits")

def write_csv(path: Path, columns, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def prepare(archive: Path, output: Path, manual_file: Path | None,
            seed: int = 42, expected_sha256: str | None = SOURCE_SHA256) -> dict:
    rows, fingerprint = read_images(archive, expected_sha256)
    assign_review_status(rows, read_review_queue(manual_file))
    make_provisional_split(rows, seed)
    by_sha = defaultdict(list)
    for row in rows:
        by_sha[row["sha256"]].append(row)
    report = {
        "status": "PROVISIONAL_CURATED_IMAGES_REVIEW_AND_RIGHTS_OPEN",
        "source_filename": archive.name, "source_zip_sha256": fingerprint,
        "total_images": len(rows),
        "classes": dict(sorted(Counter(r["class"] for r in rows).items())),
        "unreadable_images": 0,
        "exact_duplicate_groups": sum(len(g) > 1 for g in by_sha.values()),
        "cross_class_duplicate_groups": sum(len({r["class"] for r in g}) > 1 for g in by_sha.values()),
        "status_counts": dict(sorted(Counter(r["status"] for r in rows).items())),
        "extension_mismatches": [r["path"] for r in rows if r["extension_mismatch"]],
        "min_side_under_300": sum(r["min_side_under_300"] for r in rows),
        "min_side_under_200": sum(r["min_side_under_200"] for r in rows),
        "split_seed": seed,
        "split_policy": "provisional stratified 70/15/15 by class, exact-hash leakage checked",
        "split_counts": dict(sorted(Counter(r["split"] for r in rows if r["split"]).items())),
        "split_by_class": {
            c: dict(sorted(Counter(r["split"] for r in rows if r["class"] == c and r["split"]).items()))
            for c in CLASSES
        },
        "limitations": [
            "No labels were rewritten or human-verified",
            "Image licensing/provenance is not established by this audit",
            "Small heterogeneous equipment dataset; classes may be visually ambiguous",
            "Low image resolution is flagged but not automatically excluded",
            "Perceptual near-duplicates and cross-source reuse still require independent assessment",
            "Provisional splits are NOT approved for scientific model evaluation until source rights and labels are reviewed",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "image_manifest.csv", MANIFEST_FIELDS, rows)
    write_csv(output / "provisional_splits.csv", ("path", "class", "split", "sha256"),
              [r for r in rows if r["split"]])
    write_csv(output / "review_and_exclusion_queue.csv",
              ("path", "class", "status", "review_reason", "sha256"),
              [r for r in rows if r["status"] != "provisional_candidate"])
    (output / "quality_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", default=Path("data/processed/fault_images"), type=Path)
    parser.add_argument("--review-file", default=Path("docs/datasets/fault-image-manual-review.csv"), type=Path)
    parser.add_argument("--seed", default=42, type=int)
    parser.add_argument("--no-hash-check", action="store_true", help="Only for a separately documented source version")
    args = parser.parse_args()
    report = prepare(args.input, args.output, args.review_file, args.seed,
                     expected_sha256=None if args.no_hash_check else SOURCE_SHA256)
    print(json.dumps({k: report[k] for k in (
        "status", "total_images", "status_counts", "split_counts", "extension_mismatches"
    )}, indent=2))

if __name__ == "__main__":
    main()
