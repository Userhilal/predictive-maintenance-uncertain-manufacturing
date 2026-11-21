"""Profile only genuine SCANIA v2 sensor values; no synthetic observations.

Fitting population: EXISTING original readouts of train_fit vehicles with
original-source-known binary 48-step outcomes. Uses the user's already-created
genuine grouped manifest. Unknown outcomes and holdout rows NEVER fit feature
statistics. This is a source-feature QA profile, NOT transformed model input,
imputed data, or model training.

Example (run from repository root):
 py -3.11 src/preprocessing/profile_scania_trainfit_sensors.py \
  --audit data/processed/scania_audit.json \
  --data-dir ORIGINAL_SCANIA_V2_CSV_FOLDER \
  --manifest-dir data/processed/scania_training_manifest \
  --output data/processed/scania_trainfit_sensor_profile.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from decimal import Decimal
from itertools import zip_longest
from pathlib import Path

from audit_scania_cutoffs import finite_nonnegative, load_original_endpoints
from build_scania_training_manifest import FIELDS, STATUSES, vehicle_partition
from prepare_scania import sha256_file, validate_audit

SOURCE_URL = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
HORIZON = Decimal("48")


class RunningStats:
    """Online moments of observed actual values; never imputes missing cells."""
    def __init__(self) -> None:
        self.n = 0
        self.missing = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.minimum = None
        self.maximum = None

    def observe(self, raw: str, location: str) -> None:
        if not raw.strip():
            self.missing += 1
            return
        try:
            value = float(raw)
        except (ValueError, OverflowError):
            raise ValueError(f"Malformed original sensor value at {location}") from None
        if not math.isfinite(value):
            raise ValueError(f"Nonfinite original sensor value at {location}")
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (value - self.mean)
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)
        if not all(math.isfinite(x) for x in (self.mean, self.m2)):
            raise ValueError(f"Feature numerical overflow at {location}")

    def result(self) -> dict:
        return {
            "observed_actual_values": self.n,
            "original_missing_values": self.missing,
            "mean_of_observed_train_fit_values": self.mean if self.n else None,
            "population_std_of_observed_train_fit_values":
                math.sqrt(max(0.0, self.m2 / self.n)) if self.n else None,
            "minimum_original_observed_value": self.minimum,
            "maximum_original_observed_value": self.maximum,
            "all_missing_in_fit": self.n == 0,
            "constant_in_fit": self.n > 0 and self.minimum == self.maximum,
        }


def profile(audit_file: Path, data_dir: Path, manifest_dir: Path) -> dict:
    audit = validate_audit(audit_file)
    train = audit["splits"]["train"]
    raw_path = data_dir / "train_operational_readouts.csv"
    tte_path = data_dir / "train_tte.csv"
    manifest_path = manifest_dir / "train_original_observation_manifest.csv"
    manifest_report_path = manifest_dir / "manifest_report.json"

    if not all(x.is_file() for x in (raw_path, tte_path, manifest_path, manifest_report_path)):
        raise FileNotFoundError("Missing genuine SCANIA training source or original manifest")
    for original in (raw_path, tte_path):
        if sha256_file(original) != audit["checksums"][original.name]["sha256"]:
            raise ValueError(f"Source CSV bytes differ from the owner's original local audit: {original.name}")

    mr = json.loads(manifest_report_path.read_text(encoding="utf-8-sig"))
    if (mr.get("status") != "ORIGINAL_SCANIA_V2_TRAINING_MANIFEST_CREATED"
            or mr.get("source") != SOURCE_URL
            or mr.get("original_training_readouts_referenced") != train["readouts"]
            or mr.get("original_training_vehicles") != train["vehicles"]
            or mr.get("prediction_horizon_original_steps") != 48
            or mr.get("original_csv_sha256_matches_owner_audit") is not True
            or mr.get("original_horizon_audit_counts_match") is not True
            or mr.get("source_csvs_modified") is not False
            or mr.get("new_sensor_observations_generated") is not False
            or mr.get("new_source_repair_events_generated") is not False
            or mr.get("unknown_short_censored_has_blank_binary_target") is not True):
        raise ValueError("Manifest report does not match the genuine original SCANIA audit")
    endpoints = load_original_endpoints(tte_path, train["vehicles"])
    readouts = 0
    source_missing = 0
    source_rows_with_missing = 0
    status_count = Counter()
    partition_count = Counter()
    fit_known = 0
    fit_unknown = 0
    seen_partition: dict[str, str] = {}

    with raw_path.open("r", encoding="utf-8-sig", newline="") as sf, \
         manifest_path.open("r", encoding="utf-8-sig", newline="") as mf:
        original = csv.reader(sf)
        manifest = csv.DictReader(mf)
        header = next(original)
        if len(header) != 107 or len(set(header)) != 107:
            raise ValueError("Expected 107 unique original SCANIA operational CSV columns")
        if "vehicle_id" not in header or "time_step" not in header:
            raise ValueError("Original vehicle/time source fields absent")
        if manifest.fieldnames != FIELDS:
            raise ValueError("Unexpected source-derived manifest schema")
        feature_indices = [i for i, name in enumerate(header)
                           if name not in ("vehicle_id", "time_step")]
        if len(feature_indices) != 105:
            raise ValueError("Expected exactly 105 real source sensor columns")
        sensor_names = [header[i] for i in feature_indices]
        sensors = [RunningStats() for _ in sensor_names]
        vehicle_col, time_col = header.index("vehicle_id"), header.index("time_step")

        for line, (raw, meta) in enumerate(zip_longest(original, manifest), 2):
            if raw is None or meta is None:
                raise ValueError("Original SCANIA sensor CSV differs from manifest row count")
            if len(raw) != 107:
                raise ValueError(f"Malformed actual SCANIA operational CSV row {line}")
            vehicle, time = raw[vehicle_col], raw[time_col]
            if (vehicle != meta["vehicle_id"] or time != meta["time_step"]
                    or int(meta["original_csv_row"]) != line):
                raise ValueError(f"Manifest mismatched original vehicle/time or source line {line}")
            if vehicle not in endpoints:
                raise ValueError(f"Unknown source vehicle in original training row {line}")
            part = vehicle_partition(vehicle)
            if meta["internal_vehicle_partition"] != part:
                raise ValueError(f"Vehicle grouping differs from original ID-only rule at row {line}")
            earlier = seen_partition.setdefault(vehicle, part)
            if earlier != part:
                raise ValueError(f"Original vehicle appears in both internal partitions: {vehicle}")

            # Check target integrity against original SCANIA endpoint data.
            # These future values are used for QA only, never as sensor inputs.
            t = finite_nonnegative(time, location=f"original train row {line}")
            endpoint, event = endpoints[vehicle]
            d = endpoint - t
            if d <= 0:
                raise ValueError(f"Actual readout at/after original study endpoint: {vehicle}")
            if event == 1 and d <= HORIZON:
                expected_status, expected_target = STATUSES[0], "1"
            elif d >= HORIZON:
                expected_status, expected_target = STATUSES[1], "0"
            elif event == 0:
                expected_status, expected_target = STATUSES[2], ""
            else:
                raise ValueError(f"Unrecognized genuine source endpoint at row {line}")
            if (meta["horizon48_outcome_status"] != expected_status
                    or meta["source_derived_binary_target"] != expected_target):
                raise ValueError(f"Source label in manifest disagrees with genuine endpoint at row {line}")

            status_count[(part, expected_status)] += 1
            partition_count[part] += 1
            readouts += 1

            # Scan all *actual original* readings for source missingness integrity.
            values = [raw[i] for i in feature_indices]
            missing = sum(not value.strip() for value in values)
            source_missing += missing
            source_rows_with_missing += bool(missing)
            if part == "train_fit" and expected_target in ("0", "1"):
                fit_known += 1
                for name, value, stat in zip(sensor_names, values, sensors):
                    stat.observe(value, f"train_fit known source row {line}, {name}")
            elif part == "train_fit":
                fit_unknown += 1

    if readouts != train["readouts"] or len(seen_partition) != train["vehicles"]:
        raise ValueError("Original vehicle/readout totals do not match real SCANIA source")
    if (source_missing != mr["source_missing_sensor_cells_confirmed"]
            or source_rows_with_missing != mr["readouts_with_missing_sensor_confirmed"]):
        raise ValueError("Actual sensor missingness does not match original owner-run manifest")
    actual_vehicles = Counter(seen_partition.values())
    if dict(actual_vehicles) != mr["unique_source_vehicle_counts_by_partition"]:
        raise ValueError("Internal vehicle split differs from original owner-run report")
    for part, breakdown in mr["readout_outcome_by_partition"].items():
        for status, count in breakdown.items():
            if status_count[(part, status)] != count:
                raise ValueError(f"Original source outcome count mismatch for {part}/{status}")
    if fit_known != (mr["readout_outcome_by_partition"]["train_fit"][STATUSES[0]]
                     + mr["readout_outcome_by_partition"]["train_fit"][STATUSES[1]]):
        raise ValueError("Known train-fit outcome count differs from real manifest")
    if fit_unknown != mr["readout_outcome_by_partition"]["train_fit"][STATUSES[2]]:
        raise ValueError("Unknown train-fit rows incorrectly counted")
    if any(stat.n + stat.missing != fit_known for stat in sensors):
        raise ValueError("Feature-level fit counts inconsistent with original data")

    return {
        "status": "ORIGINAL_SCANIA_TRAIN_FIT_SENSOR_PROFILE_CREATED",
        "source": SOURCE_URL,
        "original_sensor_feature_columns": len(sensor_names),
        "original_training_readouts_verified": readouts,
        "original_training_vehicles_verified": len(seen_partition),
        "only_group_for_fitted_stats": "train_fit",
        "only_target_status_for_fitted_stats": "source-known binary 48-step outcome",
        "actual_original_readouts_used_to_fit_stats": fit_known,
        "actual_train_fit_readouts_with_unknown_outcome_excluded": fit_unknown,
        "unique_original_vehicles_by_partition": dict(sorted(actual_vehicles.items())),
        "original_train_missing_sensor_cells_verified": source_missing,
        "original_train_readouts_with_missing_verified": source_rows_with_missing,
        "feature_profile": {name: stat.result() for name, stat in zip(sensor_names, sensors)},
        "source_csv_sha256_matches_owners_raw_audit": True,
        "publisher_sha256_independently_verified": False,
        "prediction_endpoint_fields_in_features": False,
        "vehicle_id_or_time_step_in_features": False,
        "unknown_outcomes_used_to_fit_stats": False,
        "internal_holdout_values_used_to_fit_stats": False,
        "original_source_rows_added_or_modified": False,
        "missing_cells_imputed": False,
        "sensor_matrix_created": False,
        "model_trained": False,
        "warning": "Statistics are from known-outcome training-fit source readouts, not independent vehicles. This profile neither imputes nor normalizes real observations. Missing-data decisions, selection bias and vehicle-aware evaluation remain model-stage requirements.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--manifest-dir", type=Path,
                        default=Path("data/processed/scania_training_manifest"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/processed/scania_trainfit_sensor_profile.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite actual source feature profile: {args.output}")
    report = profile(args.audit, args.data_dir, args.manifest_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "original_sensor_feature_columns": report["original_sensor_feature_columns"],
        "original_training_readouts_verified": report["original_training_readouts_verified"],
        "actual_original_readouts_used_to_fit_stats": report["actual_original_readouts_used_to_fit_stats"],
        "actual_train_fit_readouts_with_unknown_outcome_excluded":
            report["actual_train_fit_readouts_with_unknown_outcome_excluded"],
        "original_train_missing_sensor_cells_verified":
            report["original_train_missing_sensor_cells_verified"],
        "source_csv_sha256_matches_owners_raw_audit": True,
        "missing_cells_imputed": False,
        "sensor_matrix_created": False,
        "model_trained": False,
        "full_feature_profile_path": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
