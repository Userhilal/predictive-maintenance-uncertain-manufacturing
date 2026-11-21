"""Build a source-derived 48-step training MANIFEST, never synthetic data.

Reads only actual SCANIA v2 training CSVs, their existing one-to-one
observation index, and the owner's previous original-data audits. Emits one
REFERENCE per existing readout; does not add sensor observations or alter CSVs.

Outcome values are derived from the genuine repair/censor record, AFTER the
as-of observation is chosen independently from original source observations.
Right-censored short-follow-up outcomes are UNKNOWN (blank binary target).

No training, no imputation, no fake source labels or mixed-vehicle partitions.

Usage:
 py -3.11 src/preprocessing/build_scania_training_manifest.py \
  --audit data/processed/scania_audit.json \
  --horizon-audit data/processed/scania_horizon48_audit.json \
  --data-dir ORIGINAL_SCANIA_V2_CSV_FOLDER \
  --index-dir data/processed/scania_observation_index \
  --output-dir data/processed/scania_training_manifest
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from decimal import Decimal
from itertools import zip_longest
from pathlib import Path

from audit_scania_cutoffs import finite_nonnegative, load_original_endpoints
from prepare_scania import sha256_file, validate_audit

SOURCE = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
HORIZON = Decimal("48")
SPLIT_SALT = "scania-v2-vehicle-internal-split-v1"
FIELDS = [
    "vehicle_id",
    "time_step",
    "original_csv_row",
    "observation_index",
    "internal_vehicle_partition",
    "horizon48_outcome_status",
    "source_derived_binary_target",
]
STATUSES = (
    "recorded_repair_within_48",
    "no_recorded_repair_within_48",
    "unknown_short_censored_followup",
)


def vehicle_partition(vehicle_id: str) -> str:
    """Deterministic 80/20 split based on real ID alone, independent of outcomes."""
    raw = hashlib.sha256((SPLIT_SALT + "|" + vehicle_id).encode("utf-8")).digest()
    return "internal_holdout" if int.from_bytes(raw[:8], "big") % 5 == 0 else "train_fit"


def validate_original_horizon_report(path: Path, audit: dict) -> dict:
    report = json.loads(path.read_text(encoding="utf-8-sig"))
    if (report.get("status") != "ORIGINAL_SCANIA_48STEP_ELIGIBILITY_AUDITED"
            or report.get("source") != SOURCE
            or report.get("prediction_horizon_original_time_steps") != 48):
        raise ValueError("Incorrect or incomplete real SCANIA horizon audit")
    if not (report.get("original_file_hashes_match_local_audit") is True
            and report.get("original_readouts_unchanged") is True
            and report.get("generated_source_rows_or_events") is False
            and report.get("created_training_examples_or_new_labels") is False
            and report.get("trained_model") is False):
        raise ValueError("Source-only integrity flags absent from original horizon audit")
    if (report.get("original_training_vehicles") != audit["splits"]["train"]["vehicles"]
            or report.get("existing_training_readouts_examined") != audit["splits"]["train"]["readouts"]):
        raise ValueError("Horizon audit counts disagree with original train CSV audit")
    keys = (
        "observed_repair_within_horizon",
        "known_no_repair_through_horizon",
        "unknown_due_to_short_censored_followup",
    )
    if any(type(report.get(k)) is not int or report[k] < 0 for k in keys):
        raise ValueError("Expected nonnegative original-source horizon counters")
    if sum(report[k] for k in keys) != audit["splits"]["train"]["readouts"]:
        raise ValueError("Horizon report doesn't cover every genuine source readout")
    return report


def build(audit_file: Path, horizon_file: Path, data_dir: Path,
          index_dir: Path, output_dir: Path) -> dict:
    audit = validate_audit(audit_file)
    horizon_report = validate_original_horizon_report(horizon_file, audit)
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite derived manifest: {output_dir}")
    train = audit["splits"]["train"]
    paths = {
        "tte": data_dir / "train_tte.csv",
        "source": data_dir / "train_operational_readouts.csv",
        "index": index_dir / "train_observed_index.csv",
        "preparation": index_dir / "preparation_report.json",
    }
    for name in ("tte", "source", "index", "preparation"):
        if not paths[name].is_file():
            raise FileNotFoundError(f"Missing original input: {paths[name]}")
    for filename in ("train_tte.csv", "train_operational_readouts.csv"):
        if sha256_file(data_dir / filename) != audit["checksums"][filename]["sha256"]:
            raise ValueError(f"Original SCANIA CSV differs from owner's audited source: {filename}")
    prep = json.loads(paths["preparation"].read_text(encoding="utf-8"))
    needed_flags = (
        "local_source_hashes_match_audit", "no_synthetic_observations",
        "no_new_sensor_measurements", "no_imputation_or_row_synthesis",
        "targets_not_copied_or_derived", "source_csvs_unchanged",
        "time_gap_uses_only_previous_observed_readout",
    )
    if (prep.get("status") != "REAL_SCANIA_V2_OBSERVATION_INDEX_CREATED"
            or any(prep.get(k) is not True for k in needed_flags)):
        raise ValueError("Existing real-source observation-index provenance checks failed")
    if (prep["splits"]["train"]["source_readouts"] != train["readouts"]
            or prep["splits"]["train"]["source_vehicles"] != train["vehicles"]):
        raise ValueError("Original train observation-index counts differ from real source audit")

    endpoints = load_original_endpoints(paths["tte"], train["vehicles"])
    event_counts = Counter(str(event) for _, event in endpoints.values())
    if dict(event_counts) != train["target_counts"]:
        raise ValueError("Source repair/censor vehicle counts disagree with raw audit")

    partition_by_vehicle = {}
    last_seen = {}
    status_counts = Counter()
    status_by_partition = {"train_fit": Counter(), "internal_holdout": Counter()}
    partition_vehicles = Counter()
    source_event_readouts = Counter()
    missing_sensor_cells = 0
    rows_with_missing = 0
    rows_seen = 0
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".scania-real-manifest-", dir=output_dir.parent))
    try:
        with paths["source"].open("r", encoding="utf-8-sig", newline="") as sf, \
             paths["index"].open("r", encoding="utf-8-sig", newline="") as ix, \
             (staging / "train_original_observation_manifest.csv").open("w", encoding="utf-8", newline="") as out:
            originals, indexed = csv.DictReader(sf), csv.DictReader(ix)
            if len(originals.fieldnames or []) != 107 or not {"vehicle_id", "time_step"}.issubset(originals.fieldnames or []):
                raise ValueError("Unexpected original operational CSV schema")
            if not set(("vehicle_id", "time_step", "observation_index",
                        "original_csv_row", "missing_sensor_values")).issubset(indexed.fieldnames or []):
                raise ValueError("Unexpected original observation index schema")
            writer = csv.DictWriter(out, fieldnames=FIELDS)
            writer.writeheader()
            for line, (raw, idx) in enumerate(zip_longest(originals, indexed), 2):
                if raw is None or idx is None:
                    raise ValueError("Existing source records and observation index have different row counts")
                vid, time = raw["vehicle_id"], raw["time_step"]
                if (vid != idx["vehicle_id"] or time != idx["time_step"]
                        or int(idx["original_csv_row"]) != line):
                    raise ValueError(f"Real source and index mismatch at CSV line {line}")
                if vid not in endpoints:
                    raise ValueError(f"Unrecognized original vehicle at source line {line}")
                t = finite_nonnegative(time, location=f"real source row {line}")
                sequence = int(idx["observation_index"])
                prev = last_seen.get(vid)
                if prev is None:
                    if sequence != 1:
                        raise ValueError(f"Invalid real first observation ordinal for {vid}")
                elif t <= prev[0] or sequence != prev[1] + 1:
                    raise ValueError(f"Non-increasing original observation/time for vehicle {vid}")
                last_seen[vid] = (t, sequence)
                missed = int(idx["missing_sensor_values"])
                if not 0 <= missed <= 105:
                    raise ValueError(f"Invalid real missingness count at line {line}")
                sensor_keys = [name for name in originals.fieldnames
                               if name not in ("vehicle_id", "time_step")]
                source_missing = sum(not (raw.get(name) or "").strip() for name in sensor_keys)
                if missed != source_missing:
                    raise ValueError(f"Original sensor missingness disagrees with index: {line}")
                missing_sensor_cells += missed
                rows_with_missing += int(missed > 0)

                # As-of choice is EVERY ORIGINAL observation, regardless of
                # future repair/censor event or how many later readings exist.
                partition = partition_by_vehicle.get(vid)
                if partition is None:
                    partition = vehicle_partition(vid)
                    partition_by_vehicle[vid] = partition
                    partition_vehicles[partition] += 1

                # Target/outcome derivation happens AFTER the as-of time is
                # independently chosen, and is stored in a separate manifest;
                # none of these fields become model predictor features.
                endpoint, event = endpoints[vid]
                remaining = endpoint - t
                if remaining <= 0:
                    raise ValueError(f"Real source observation occurs at/after study endpoint: {vid}")
                source_event_readouts[str(event)] += 1
                if event == 1 and remaining <= HORIZON:
                    status, binary_target = STATUSES[0], "1"
                elif remaining >= HORIZON:
                    status, binary_target = STATUSES[1], "0"
                elif event == 0:
                    status, binary_target = STATUSES[2], ""
                else:
                    raise AssertionError("Unexpected original source event status")

                status_counts[status] += 1
                status_by_partition[partition][status] += 1
                writer.writerow({
                    "vehicle_id": vid, "time_step": time,
                    "original_csv_row": line, "observation_index": sequence,
                    "internal_vehicle_partition": partition,
                    "horizon48_outcome_status": status,
                    "source_derived_binary_target": binary_target,
                })
                rows_seen += 1

        if (rows_seen != train["readouts"] or len(last_seen) != train["vehicles"]
                or set(last_seen) != set(endpoints)):
            raise ValueError("Final manifest count or genuine source vehicle set mismatch")
        if (source_event_readouts["1"] != horizon_report["source_readouts_with_repair_event_vehicle"]
                or source_event_readouts["0"] != horizon_report["source_readouts_with_right_censored_vehicle"]):
            raise ValueError("Manifest source event-readout counts disagree with genuine horizon audit")
        expected = {
            STATUSES[0]: horizon_report["observed_repair_within_horizon"],
            STATUSES[1]: horizon_report["known_no_repair_through_horizon"],
            STATUSES[2]: horizon_report["unknown_due_to_short_censored_followup"],
        }
        if any(status_counts[k] != amount for k, amount in expected.items()):
            raise ValueError("Manifest outcomes disagree with genuine 48-step source audit")
        if (missing_sensor_cells != prep["splits"]["train"]["source_missing_sensor_cells"]
                or rows_with_missing != prep["splits"]["train"]["rows_with_at_least_one_missing_sensor"]):
            raise ValueError("Source missingness no longer matches original real-data preparation")
        if not all(partition_vehicles[part] for part in ("train_fit", "internal_holdout")):
            raise ValueError("Internal split unexpectedly empty")
        report = {
            "status": "ORIGINAL_SCANIA_V2_TRAINING_MANIFEST_CREATED",
            "source": SOURCE,
            "original_training_vehicles": len(last_seen),
            "original_training_readouts_referenced": rows_seen,
            "prediction_horizon_original_steps": 48,
            "asof_rule": "Every original readout retained, regardless of future source outcomes",
            "internal_partition_rule": "SHA256 original vehicle ID only; stable ~80/20 vehicle-grouped split",
            "partition_salt": SPLIT_SALT,
            "unique_source_vehicle_counts_by_partition": dict(sorted(partition_vehicles.items())),
            "original_readout_outcome_status": dict(sorted(status_counts.items())),
            "readout_outcome_by_partition": {
                k: dict(sorted(v.items())) for k, v in status_by_partition.items()
            },
            "source_missing_sensor_cells_confirmed": missing_sensor_cells,
            "readouts_with_missing_sensor_confirmed": rows_with_missing,
            "original_csv_sha256_matches_owner_audit": True,
            "original_horizon_audit_counts_match": True,
            "publisher_file_hashes_verified": False,
            "source_csvs_modified": False,
            "new_sensor_observations_generated": False,
            "new_source_repair_events_generated": False,
            "binary_target_only_derived_from_original_followup": True,
            "unknown_short_censored_has_blank_binary_target": True,
            "source_sensor_values_not_copied": True,
            "model_trained": False,
            "not_a_feature_matrix": True,
            "warning": "Rows reference correlated actual readouts, not independent vehicles. Unknown short-censored outcomes must be masked from binary loss; dropping them can bias training. No holdout targets should be predictor features.",
        }
        (staging / "manifest_report.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(output_dir)
        return report
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--horizon-audit", required=True, type=Path)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--index-dir", type=Path, default=Path("data/processed/scania_observation_index"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/scania_training_manifest"))
    args = parser.parse_args()
    print(json.dumps(build(args.audit, args.horizon_audit, args.data_dir, args.index_dir, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
