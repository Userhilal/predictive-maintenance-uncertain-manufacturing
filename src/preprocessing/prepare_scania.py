"""Index ONLY real SCANIA v2 operational readouts, preserving all source CSVs.

Creates one metadata row per original observed readout (no extra observations).
Past-only fields: observation number, preceding observed time step, observed time
gap, and number of sensor values genuinely present/missing at this observation.
No imputation, synthetic examples, model training, or target derivation.

Preflight: python src/preprocessing/prepare_scania.py --audit data/processed/scania_audit.json --check-audit-only
Full run: python src/preprocessing/prepare_scania.py --audit data/processed/scania_audit.json --data-dir PATH_TO_ORIGINAL_DATA --output-dir data/processed/scania_observation_index
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

SPLITS = ("train", "validation", "test")
SOURCE_URL = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
EXPECTED_FILES = (
    "train_operational_readouts.csv", "train_specifications.csv", "train_tte.csv",
    "validation_operational_readouts.csv", "validation_specifications.csv",
    "validation_labels.csv", "test_operational_readouts.csv",
    "test_specifications.csv", "test_labels.csv",
)
INDEX_COLUMNS = (
    "vehicle_id", "time_step", "original_csv_row", "observation_index",
    "previous_observed_time_step", "gap_since_previous_time_step",
    "available_sensor_values", "missing_sensor_values",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_audit(path: Path) -> dict:
    """Accept only the original-data audit report, not fixture data."""
    audit = json.loads(path.read_text(encoding="utf-8-sig"))
    if audit.get("status") != "RAW_CSV_AUDIT_EXECUTED":
        raise ValueError("Original SCANIA CSV audit is not successfully completed")
    if audit.get("source_version") != "2024-34/2" or audit.get("source_url") != SOURCE_URL:
        raise ValueError("Only the user-supplied SCANIA Component X v2 is allowed")
    overall = audit.get("overall", {})
    if not overall.get("disjoint_vehicle_splits") or not overall.get("vehicle_target_linkage_verified"):
        raise ValueError("Original audit did not verify split disjointness and source target joins")
    if overall.get("vehicles") != 33641 or overall.get("readouts") != 1516819:
        raise ValueError("Unexpected counts: audit does not match provided original source")
    fingerprints = audit.get("checksums", {})
    if set(fingerprints) != set(EXPECTED_FILES):
        raise ValueError("Missing original-file fingerprints")
    for name in EXPECTED_FILES:
        digest = fingerprints[name].get("sha256", "")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid source fingerprint for {name}")
    splits = audit.get("splits", {})
    if set(splits) != set(SPLITS):
        raise ValueError("Incomplete original-data split audit")
    for split in SPLITS:
        data = splits[split]
        if data["operational_columns"] != 107 or data["readouts"] <= 0 or data["vehicles"] <= 0:
            raise ValueError(f"Unexpected original SCANIA layout in {split}")
        identifiers = data.get("small_tables_with_explicit_vehicle_id", {})
        if not identifiers.get("specifications") or not identifiers.get("target"):
            raise ValueError(f"Source vehicle-to-target identifiers not verified in {split}")
        if data.get("non_numeric_values", 1) != 0:
            raise ValueError(f"Invalid numeric source values reported in {split}")
        if data.get("backwards_order_vehicle_count", 1) or data.get("repeated_adjacent_time_steps", 1):
            raise ValueError(f"Unexpected original time sequence in {split}")
    return audit


def index_observed_rows(path: Path, output: Path, expected: dict,
                        prior_schema: list[str] | None) -> tuple[dict, list[str]]:
    """Write metadata mapped one-to-one to each original recorded observation."""
    previous: dict[str, tuple[Decimal, str, int]] = {}
    row_count = 0
    missing_cells = 0
    rows_with_missing = 0
    with path.open("r", encoding="utf-8-sig", newline="") as src, \
         output.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        fields = reader.fieldnames or []
        if len(fields) != 107 or len(set(fields)) != 107:
            raise ValueError(f"Invalid operational schema: {path.name}")
        if "vehicle_id" not in fields or "time_step" not in fields:
            raise ValueError(f"Missing source vehicle ID/time: {path.name}")
        sensors = [key for key in fields if key not in ("vehicle_id", "time_step")]
        if len(sensors) != 105 or (prior_schema is not None and sensors != prior_schema):
            raise ValueError(f"Feature columns differ across real source splits: {path.name}")
        writer = csv.DictWriter(dst, fieldnames=INDEX_COLUMNS)
        writer.writeheader()
        for csv_line, record in enumerate(reader, 2):
            if None in record:
                raise ValueError(f"Malformed source row in {path.name}:{csv_line}")
            vehicle, raw_time = record.get("vehicle_id"), record.get("time_step")
            if not vehicle or not raw_time:
                raise ValueError(f"Original vehicle/time missing at {path.name}:{csv_line}")
            try:
                current = Decimal(raw_time)
                if not current.is_finite() or current < 0:
                    raise ValueError()
            except (ValueError, InvalidOperation):
                raise ValueError(f"Invalid original time at {path.name}:{csv_line}") from None
            missing = sum(record[col] is None or not record[col].strip() for col in sensors)
            missing_cells += missing
            rows_with_missing += int(missing > 0)
            old = previous.get(vehicle)
            if old is None:
                previous_time, gap, index = "", "", 1
            else:
                prev_time, previous_time, prior_index = old
                if current <= prev_time:
                    raise ValueError(f"Non-increasing time for actual vehicle {vehicle}")
                gap, index = str(current - prev_time), prior_index + 1
            writer.writerow({
                "vehicle_id": vehicle, "time_step": raw_time,
                "original_csv_row": csv_line, "observation_index": index,
                "previous_observed_time_step": previous_time,
                "gap_since_previous_time_step": gap,
                "available_sensor_values": 105 - missing,
                "missing_sensor_values": missing,
            })
            previous[vehicle] = (current, raw_time, index)
            row_count += 1
    expected_missing = sum(expected["feature_missing_counts"].values())
    if (row_count != expected["readouts"] or len(previous) != expected["vehicles"]
            or missing_cells != expected_missing):
        raise ValueError(f"Derived index does not match real audit counts for {path.name}")
    return ({
        "source_readouts": row_count,
        "source_vehicles": len(previous),
        "source_missing_sensor_cells": missing_cells,
        "rows_with_at_least_one_missing_sensor": rows_with_missing,
        "first_observations_with_no_prior_gap": len(previous),
    }, sensors)


def prepare(data_dir: Path, audit_file: Path, output_dir: Path) -> dict:
    audit = validate_audit(audit_file)
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite output folder: {output_dir}")
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Original SCANIA source folder not found: {data_dir}")
    # Source integrity: compare every genuine CSV byte fingerprint to the
    # audit created from the owner's original download. Not a publisher SHA check.
    for name in EXPECTED_FILES:
        path = data_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing original SCANIA CSV: {path}")
        if sha256_file(path) != audit["checksums"][name]["sha256"]:
            raise ValueError(f"Original CSV differs from uploaded real-data audit: {name}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".scania-source-index-", dir=output_dir.parent))
    try:
        report = {
            "status": "REAL_SCANIA_V2_OBSERVATION_INDEX_CREATED",
            "source": SOURCE_URL,
            "local_source_hashes_match_audit": True,
            "publisher_hash_verification": all(
                audit["checksums"][name].get("provider_hash_verified") is True
                for name in EXPECTED_FILES
            ),
            "no_synthetic_observations": True,
            "no_new_sensor_measurements": True,
            "no_imputation_or_row_synthesis": True,
            "targets_not_copied_or_derived": True,
            "source_csvs_unchanged": True,
            "time_gap_uses_only_previous_observed_readout": True,
            "not_a_model_training_dataset": True,
            "splits": {},
        }
        schema = None
        for split in SPLITS:
            details, schema = index_observed_rows(
                data_dir / f"{split}_operational_readouts.csv",
                staging / f"{split}_observed_index.csv",
                audit["splits"][split], schema,
            )
            report["splits"][split] = details
        (staging / "preparation_report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(output_dir)
        return report
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True, help="Full JSON audit of nine real CSVs")
    parser.add_argument("--check-audit-only", action="store_true",
                        help="Check genuine source audit; do not make any observations")
    parser.add_argument("--data-dir", type=Path, help="Folder holding the nine unmodified SCANIA CSVs")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("data/processed/scania_observation_index"))
    args = parser.parse_args()
    audit = validate_audit(args.audit)
    if args.check_audit_only:
        print(json.dumps({
            "status": "ORIGINAL_AUDIT_REPORT_ACCEPTED",
            "vehicles": audit["overall"]["vehicles"],
            "readouts": audit["overall"]["readouts"],
            "prepared_source_rows": False,
        }, indent=2))
    else:
        if args.data_dir is None:
            parser.error("--data-dir is required unless --check-audit-only is set")
        print(json.dumps(prepare(args.data_dir, args.audit, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
