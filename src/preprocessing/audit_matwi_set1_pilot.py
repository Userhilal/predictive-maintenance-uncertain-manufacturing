"""Read-only MATWI Set1 pilot: audit publisher metadata and archive membership."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
import zipfile

EXPECTED = {
    "labels.csv": "314fa8c1ff769a3e3c745945e31e1bc8",
    "Set1.zip": "a2146e24541dfad50a1bb5e04c27189e",
}
REQUIRED = {"Set", "ImageName", "SensorName", "ImageFile", "SensorFile",
            "ImageID", "SensorID", "wear", "type", "ImageDateTime", "SensorDateTime"}

def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def clean(value):
    s = (value or "").strip()
    return "" if s.lower() in {"nan", "none", "null", "na"} else s

def set_one(value):
    return clean(value).lower().replace(" ", "").replace("_", "") in {"1", "1.0", "set1", "set01", "01"}

def basename(value):
    return PurePosixPath(clean(value).replace(chr(92), "/")).name

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    if a.output_dir.exists():
        raise FileExistsError(a.output_dir)
    hashes = {}
    for name, expected in EXPECTED.items():
        path = a.source_dir / name
        actual = digest(path, "md5")
        if actual != expected:
            raise ValueError(f"Publisher MD5 mismatch: {name}: {actual}")
        hashes[name] = {"md5": actual, "sha256": digest(path, "sha256")}
    with (a.source_dir / "labels.csv").open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not REQUIRED <= set(reader.fieldnames or []):
            raise ValueError(f"Unexpected publisher schema: {reader.fieldnames}")
        all_rows = list(reader)
    rows = [(i, row) for i, row in enumerate(all_rows, 2) if set_one(row["Set"])]
    if not rows:
        raise ValueError("Set1 not identified; inspect original Set values: " +
                         repr(sorted({r["Set"] for r in all_rows})))
    counts = Counter()
    result = []
    with zipfile.ZipFile(a.source_dir / "Set1.zip") as z:
        members = defaultdict(list)
        for info in z.infolist():
            if not info.is_dir() and info.file_size > 0:
                members[basename(info.filename)].append(info.filename)
        def resolve(row, path_field, name_field):
            path, name = clean(row[path_field]), clean(row[name_field])
            if not path and not name:
                return "", "MISSING_REFERENCE"
            if path and name and basename(path) != basename(name):
                return "", "NAME_PATH_CONFLICT"
            matches = members[basename(path or name)]
            if len(matches) != 1:
                return "", "ABSENT_OR_AMBIGUOUS_MEMBER"
            return matches[0], "UNIQUE_MEMBER_MATCH"
        for line, row in rows:
            image, image_status = resolve(row, "ImageFile", "ImageName")
            sensor, sensor_status = resolve(row, "SensorFile", "SensorName")
            try:
                wear = float(clean(row["wear"]))
                wear_valid = math.isfinite(wear) and wear >= 0
            except ValueError:
                wear_valid = False
            linked = bool(image and sensor and image != sensor)
            counts["publisher_link_rows_resolved"] += linked
            counts["missing_or_unresolved_link_rows"] += not linked
            counts["rows_with_nonnegative_finite_wear"] += wear_valid
            result.append({
                "source_csv_line": line, **row,
                "image_zip_member": image, "sensor_zip_member": sensor,
                "image_status": image_status, "sensor_status": sensor_status,
                "wear_numeric_valid": wear_valid,
                "link_status": "PUBLISHER_LINK_MEMBER_MATCH" if linked else "UNRESOLVED",
                "related_failure_family": "TWF",
                "failure_type": "UNKNOWN",
                "failure_label_status": "NO_FAILURE_ENDPOINT_ADJUDICATION",
                "same_event_synchronization_verified": False,
                "training_approved": False,
            })
    image_counts = Counter(r["image_zip_member"] for r in result if r["image_zip_member"])
    sensor_counts = Counter(r["sensor_zip_member"] for r in result if r["sensor_zip_member"])
    report = {
        "status": "MATWI_SET1_PUBLISHER_LINK_PILOT_NOT_FAILURE_LABEL_VALIDATION",
        "publisher_doi": "10.48804/GK6LHH", "license": "CC-BY-SA-4.0",
        "source_hashes": hashes, "publisher_label_rows_total": len(all_rows),
        "set1_rows": len(rows), **dict(counts),
        "repeated_image_member_count": sum(v > 1 for v in image_counts.values()),
        "repeated_sensor_member_count": sum(v > 1 for v in sensor_counts.values()),
        "verified_five_mode_failure_labels": 0,
        "verified_cross_source_pairs": 0,
        "full_multimodal_ready": False,
        "limitations": ["Archive membership only; no pixel or waveform inspection",
                        "No timestamp synchronization validation",
                        "Wear measurements do not establish failure endpoints",
                        "No AI4I or SCANIA physical event links"]
    }
    a.output_dir.mkdir(parents=True, exist_ok=False)
    with (a.output_dir / "matwi_set1_review.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    (a.output_dir / "matwi_set1_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
