"""Aggregate feasibility audit for a 48-step SCANIA v2 repair prediction horizon.

Only original training readouts and the original source repair/censor records.
Does NOT generate training rows, synthetic data, new source observations, or labels.
Every existing readout is inspected as an as-of *candidate*; no prediction times
are selected using future repair events or total future readings.

Usage:
  py -3.11 src/preprocessing/audit_scania_horizon48.py \
    --audit data/processed/scania_audit.json \
    --data-dir ORIGINAL_SCANIA_V2_DATA \
    --index-dir data/processed/scania_observation_index \
    --output data/processed/scania_horizon48_audit.json
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from decimal import Decimal
from itertools import zip_longest
from pathlib import Path

from audit_scania_cutoffs import finite_nonnegative, load_original_endpoints
from prepare_scania import sha256_file, validate_audit

HORIZON = Decimal("48")
SOURCE_URL = "https://researchdata.se/en/catalogue/dataset/2024-34/2"


def inspect(audit_path: Path, data_dir: Path, index_dir: Path) -> dict:
    audit = validate_audit(audit_path)
    expected = audit["splits"]["train"]

    # Compare actual source bytes against real, owner-generated local audit.
    # This is not independent publisher hash verification.
    for name in ("train_tte.csv", "train_operational_readouts.csv"):
        file = data_dir / name
        if not file.is_file() or sha256_file(file) != audit["checksums"][name]["sha256"]:
            raise ValueError(f"Original SCANIA source file missing/changed: {file}")

    prep_file = index_dir / "preparation_report.json"
    prep = json.loads(prep_file.read_text(encoding="utf-8"))
    if prep.get("status") != "REAL_SCANIA_V2_OBSERVATION_INDEX_CREATED":
        raise ValueError("Expected the completed original-source observation index")
    for flag in (
        "local_source_hashes_match_audit", "no_synthetic_observations",
        "no_new_sensor_measurements", "no_imputation_or_row_synthesis",
        "targets_not_copied_or_derived", "source_csvs_unchanged",
        "time_gap_uses_only_previous_observed_readout",
    ):
        if prep.get(flag) is not True:
            raise ValueError(f"Original observation-index safeguard missing: {flag}")
    source_train = prep["splits"]["train"]
    if (source_train["source_readouts"] != expected["readouts"]
            or source_train["source_vehicles"] != expected["vehicles"]):
        raise ValueError("Training index differs from audited original train data")

    endpoints = load_original_endpoints(
        data_dir / "train_tte.csv", expected["vehicles"]
    )
    actual_counts = Counter(str(event) for _, event in endpoints.values())
    if dict(actual_counts) != expected["target_counts"]:
        raise ValueError("Original observed repair/censor counts changed")

    result_counts = Counter()
    readouts_by_event = Counter()
    vehicle_state = {}
    index_path = index_dir / "train_observed_index.csv"
    original_path = data_dir / "train_operational_readouts.csv"
    source_rows = 0

    # Stream the original operational CSV and the already-created source-only
    # index together. Strict one-to-one matching prevents a shifted time index.
    with index_path.open("r", encoding="utf-8-sig", newline="") as index_in, \
         original_path.open("r", encoding="utf-8-sig", newline="") as original_in:
        indexed = csv.DictReader(index_in)
        original = csv.DictReader(original_in)
        required_index = {"vehicle_id", "time_step", "observation_index", "original_csv_row"}
        required_original = {"vehicle_id", "time_step"}
        if not required_index.issubset(set(indexed.fieldnames or [])):
            raise ValueError("Original observation index schema differs")
        if not required_original.issubset(set(original.fieldnames or [])):
            raise ValueError("Original operational source schema differs")

        for line, (row, raw) in enumerate(zip_longest(indexed, original), 2):
            if row is None or raw is None:
                raise ValueError("Indexed observations do not match original row count")
            vehicle = raw["vehicle_id"]
            original_time = raw["time_step"]
            if (vehicle != row["vehicle_id"]
                    or original_time != row["time_step"]
                    or int(row["original_csv_row"]) != line):
                raise ValueError(f"Original observation mismatch at row {line}")
            if vehicle not in endpoints:
                raise ValueError(f"Unrecognized original vehicle at row {line}")
            t = finite_nonnegative(original_time, location=f"source row {line}")
            prior = vehicle_state.get(vehicle)
            sequence = int(row["observation_index"])
            if prior is None:
                if sequence != 1:
                    raise ValueError(f"Incorrect first observed index: {vehicle}")
            else:
                prior_time, prior_sequence = prior
                if t <= prior_time or sequence != prior_sequence + 1:
                    raise ValueError(f"Non-increasing original time/index: {vehicle}")
            vehicle_state[vehicle] = (t, sequence)

            endpoint, event = endpoints[vehicle]
            residual = endpoint - t
            if residual <= 0:
                raise ValueError(f"Original readout not before study endpoint: {vehicle}")
            readouts_by_event[str(event)] += 1

            # All candidates are *original* recorded observations. Source
            # outcome is consulted ONLY to count label observability, not to
            # select prediction timestamps or build predictor features.
            if event == 1 and residual <= HORIZON:
                key = "known_observed_repair_within_48"
            elif residual >= HORIZON:
                key = "known_no_recorded_repair_within_48"
            else:
                # Only possible for right-censored original vehicles. Follow-up
                # ends before 48 steps, so this is NOT a negative observation.
                if event != 0:
                    raise AssertionError("Unexpected observed-event timing")
                key = "unknown_right_censored_before_48"
            result_counts[key] += 1
            source_rows += 1

    if (source_rows != expected["readouts"]
            or len(vehicle_state) != expected["vehicles"]
            or set(vehicle_state) != set(endpoints)):
        raise ValueError("Original training vehicle or observation count mismatch")
    if readouts_by_event["1"] + readouts_by_event["0"] != source_rows:
        raise ValueError("Original repair/censor grouping does not cover all readouts")

    return {
        "status": "ORIGINAL_SCANIA_48STEP_ELIGIBILITY_AUDITED",
        "source": SOURCE_URL,
        "prediction_horizon_original_time_steps": 48,
        "original_training_vehicles": len(vehicle_state),
        "existing_training_readouts_examined": source_rows,
        "source_readouts_with_repair_event_vehicle": readouts_by_event["1"],
        "source_readouts_with_right_censored_vehicle": readouts_by_event["0"],
        "observed_repair_within_horizon": result_counts["known_observed_repair_within_48"],
        "known_no_repair_through_horizon": result_counts["known_no_recorded_repair_within_48"],
        "unknown_due_to_short_censored_followup": result_counts["unknown_right_censored_before_48"],
        "original_file_hashes_match_local_audit": True,
        "publisher_hashes_verified": False,
        "original_readouts_unchanged": True,
        "generated_source_rows_or_events": False,
        "created_training_examples_or_new_labels": False,
        "trained_model": False,
        "asof_rule": "Every originally recorded training readout is only a candidate, not a sampled training instance.",
        "censoring_rule": "Censored with less than 48 observed follow-up steps is unknown, never a known negative.",
        "warning": "These are aggregate source-derived eligibility counts, NOT training labels. Multiple rows per original vehicle are dependent. Validation/test use only their final available original readout for scoring.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--index-dir", type=Path,
                        default=Path("data/processed/scania_observation_index"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/processed/scania_horizon48_audit.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite earlier source QA: {args.output}")
    report = inspect(args.audit, args.data_dir, args.index_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
