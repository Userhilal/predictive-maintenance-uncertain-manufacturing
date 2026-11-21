"""Read-only SCANIA v2 endpoint diagnostic using only original source observations.

Preflight (actual uploaded source-audit report):
 python src/preprocessing/audit_scania_cutoffs.py --audit data/processed/scania_audit.json --check-audit-only

Original-file diagnostic:
 python src/preprocessing/audit_scania_cutoffs.py --audit data/processed/scania_audit.json --data-dir PATH_TO_NINE_CSVS --index-dir data/processed/scania_observation_index --output data/processed/scania_cutoff_audit.json

Produces only aggregated timing counts, not fabricated data, new repair labels,
chosen prediction times, or training samples.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from prepare_scania import sha256_file, validate_audit


def finite_nonnegative(value: str, *, location: str) -> Decimal:
    try:
        number = Decimal(value)
        if not number.is_finite() or number < 0:
            raise ValueError()
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid original numeric time at {location}") from None
    return number


def load_original_endpoints(file: Path, expected_vehicles: int) -> dict[str, tuple[Decimal, int]]:
    endpoints: dict[str, tuple[Decimal, int]] = {}
    with file.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        expected = {"vehicle_id", "length_of_study_time_step", "in_study_repair"}
        if set(reader.fieldnames or []) != expected:
            raise ValueError("train_tte.csv source schema differs from the original audit")
        for line, rec in enumerate(reader, 2):
            vehicle = rec["vehicle_id"]
            if not vehicle or vehicle in endpoints:
                raise ValueError(f"Missing/duplicate real vehicle ID in train_tte.csv line {line}")
            event = rec["in_study_repair"]
            if event not in ("0", "1"):
                raise ValueError(f"Invalid event/censoring flag at train_tte.csv line {line}")
            endpoint = finite_nonnegative(rec["length_of_study_time_step"], location=f"train_tte.csv line {line}")
            endpoints[vehicle] = (endpoint, int(event))
    if len(endpoints) != expected_vehicles:
        raise ValueError("Original endpoint table vehicle count differs from source audit")
    return endpoints


def audit_real_cutoffs(audit_path: Path, data_dir: Path, index_dir: Path) -> dict:
    audit = validate_audit(audit_path)
    if not data_dir.is_dir() or not index_dir.is_dir():
        raise FileNotFoundError("Original source folder or real observation-index folder is missing")

    # Local source-integrity matching, not a publisher-verified hash check.
    for filename in ("train_tte.csv", "train_operational_readouts.csv"):
        path = data_dir / filename
        if not path.is_file() or sha256_file(path) != audit["checksums"][filename]["sha256"]:
            raise ValueError(f"Missing/changed original SCANIA source file: {filename}")

    prep_file = index_dir / "preparation_report.json"
    if not prep_file.is_file():
        raise FileNotFoundError(f"Missing original-data preparation report: {prep_file}")
    prep = json.loads(prep_file.read_text(encoding="utf-8"))
    if prep.get("status") != "REAL_SCANIA_V2_OBSERVATION_INDEX_CREATED" or not prep.get("local_source_hashes_match_audit"):
        raise ValueError("Original SCANIA observation index not accepted against local original-file hashes")
    safeguards = (
        "no_synthetic_observations", "no_new_sensor_measurements",
        "no_imputation_or_row_synthesis", "targets_not_copied_or_derived",
        "source_csvs_unchanged", "time_gap_uses_only_previous_observed_readout",
    )
    for key in safeguards:
        if prep.get(key) is not True:
            raise ValueError(f"Original-data preparation report lacks safeguard: {key}")

    expected = audit["splits"]["train"]
    train_prep = prep["splits"]["train"]
    if (train_prep["source_vehicles"] != expected["vehicles"]
            or train_prep["source_readouts"] != expected["readouts"]
            or train_prep["source_missing_sensor_cells"] != sum(expected["feature_missing_counts"].values())):
        raise ValueError("Prepared observation totals differ from original train audit")

    endpoints = load_original_endpoints(data_dir / "train_tte.csv", expected["vehicles"])
    actual_event_counts = Counter(str(event) for _, event in endpoints.values())
    if dict(actual_event_counts) != expected["target_counts"]:
        raise ValueError("Original repair/censoring counts differ from audited target distribution")

    index_file = index_dir / "train_observed_index.csv"
    if not index_file.is_file():
        raise FileNotFoundError(f"Original-train observation index not found: {index_file}")
    time_status = {0: Counter(), 1: Counter()}
    seen_by_vehicle: dict[str, tuple[Decimal, int]] = {}
    before_by_vehicle = Counter()
    missing_cells = 0
    rows_with_missing = 0
    rows = 0
    with index_file.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"vehicle_id", "time_step", "original_csv_row", "observation_index", "missing_sensor_values"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("Original observation index has an unexpected schema")
        for line, rec in enumerate(reader, 2):
            vid = rec["vehicle_id"]
            if vid not in endpoints:
                raise ValueError(f"Index contains vehicle not in genuine SCANIA endpoints at line {line}")
            t = finite_nonnegative(rec["time_step"], location=f"index line {line}")
            if int(rec["original_csv_row"]) != line:
                raise ValueError(f"Missing/rearranged source row in observation index at line {line}")
            number = int(rec["observation_index"])
            old = seen_by_vehicle.get(vid)
            if old:
                old_t, old_number = old
                if t <= old_t or number != old_number + 1:
                    raise ValueError(f"Non-increasing time or sequence index for original vehicle {vid}")
            elif number != 1:
                raise ValueError(f"Non-initial index number for original vehicle {vid}")
            seen_by_vehicle[vid] = (t, number)
            missed = int(rec["missing_sensor_values"])
            if not 0 <= missed <= 105:
                raise ValueError(f"Invalid missing-cell count at source index line {line}")
            missing_cells += missed
            rows_with_missing += missed > 0
            endpoint, event = endpoints[vid]
            if t < endpoint:
                time_status[event]["before_study_endpoint"] += 1
                before_by_vehicle[vid] += 1
            elif t == endpoint:
                time_status[event]["at_study_endpoint"] += 1
            else:
                time_status[event]["after_study_endpoint"] += 1
            rows += 1

    if (rows != expected["readouts"] or len(seen_by_vehicle) != expected["vehicles"]
            or missing_cells != train_prep["source_missing_sensor_cells"]
            or rows_with_missing != train_prep["rows_with_at_least_one_missing_sensor"]
            or set(seen_by_vehicle) != set(endpoints)):
        raise ValueError("Prepared source rows or IDs do not match the original SCANIA audit")

    groups = {}
    for event, name in ((1, "recorded_repair"), (0, "right_censored")):
        ids = {vid for vid, (_, label) in endpoints.items() if label == event}
        groups[name] = {
            "source_vehicles": len(ids),
            "source_readouts_before_endpoint": time_status[event]["before_study_endpoint"],
            "source_readouts_at_endpoint": time_status[event]["at_study_endpoint"],
            "source_readouts_after_endpoint": time_status[event]["after_study_endpoint"],
            "vehicles_with_at_least_one_strictly_pre_endpoint_readout": sum(vid in before_by_vehicle for vid in ids),
            "vehicles_without_strictly_pre_endpoint_readout": sum(vid not in before_by_vehicle for vid in ids),
        }
    return {
        "status": "REAL_SCANIA_TRAIN_ENDPOINT_RELATION_AUDITED",
        "source": "https://researchdata.se/en/catalogue/dataset/2024-34/2",
        "source_hashes_match_original_local_audit": True,
        "source_train_index_matches_original_preparation": True,
        "new_rows_or_observations_created": False,
        "repair_or_failure_labels_generated": False,
        "prediction_cutoffs_selected": False,
        "model_trained": False,
        "raw_source_files_modified": False,
        "publisher_hash_verification": False,
        "train_vehicles": len(endpoints),
        "train_existing_readouts": rows,
        "groups": groups,
        "notes": [
            "QA-only relationship between existing readout times and source repair/censoring endpoints; do not choose as-of prediction time from a future endpoint.",
            "Right-censored vehicles are not negative forever; the source endpoint is the end of observed follow-up, not a confirmed failure time.",
            "Validation/test categorical labels do not reveal exact repair times.",
            "A model's train as-of selection rule must not depend on future repair timing or number of future observations.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--check-audit-only", action="store_true", help="Use only the uploaded genuine raw-data audit")
    parser.add_argument("--data-dir", type=Path, help="Folder with unchanged original SCANIA v2 CSVs")
    parser.add_argument("--index-dir", type=Path, default=Path("data/processed/scania_observation_index"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/scania_cutoff_audit.json"))
    args = parser.parse_args()
    audit = validate_audit(args.audit)
    if args.check_audit_only:
        print(json.dumps({
            "status": "ORIGINAL_SCANIA_AUDIT_VERIFIED_FOR_CUTOFF_DIAGNOSTIC",
            "source_vehicles": audit["overall"]["vehicles"],
            "source_readouts": audit["overall"]["readouts"],
            "no_source_rows_created": True,
        }, indent=2))
        return
    if args.data_dir is None:
        parser.error("--data-dir is required for the full original-file cutoff diagnostic")
    result = audit_real_cutoffs(args.audit, args.data_dir, args.index_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite existing original-data diagnostic: {args.output}")
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
