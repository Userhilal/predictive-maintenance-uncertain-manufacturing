"""Seal the original-only SCANIA v2 numeric model-input contract (NO model fitting).

Inputs are the owner's already-executed actual SCANIA source-derived manifest
report, 105-feature profile and quality-review JSON. They must have consistent
SHA-256 fingerprints and genuine counts. No source rows are modified or copied.
No new sensor observations, made-up repairs, imputation, clipping or scaling.
The contract can be consumed by a *later* NaN-native tree model.

From repo root:
 py -3.11 src/preprocessing/create_scania_model_input_contract.py \
  --manifest-report data/processed/scania_training_manifest/manifest_report.json \
  --profile data/processed/scania_trainfit_sensor_profile.json \
  --review data/processed/scania_sensor_quality_review.json \
  --output data/processed/scania_model_input_contract.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
N_SENSORS = 105
KNOWN_FIT = 737995
KNOWN_HOLDOUT = 182063
UNKNOWN_FIT = 162292
UNKNOWN_HOLDOUT = 40102
ALL_TRAIN = 1122452
TRAIN_VEHICLES = 23550
TRAIN_SOURCE_MISSING = 354634
FIT_KNOWN_MISSING = 226017

FORBIDDEN = frozenset({
    "vehicle_id", "time_step", "original_csv_row", "observation_index",
    "internal_vehicle_partition", "source_derived_binary_target",
    "horizon48_outcome_status", "in_study_repair", "length_of_study_time_step",
    "class_label",
})


def load_json_with_sha(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object from original source audit: {path}")
    return value, hashlib.sha256(raw).hexdigest()


def exact_int(obj: dict, key: str, expected: int) -> None:
    if type(obj.get(key)) is not int or obj[key] != expected:
        raise ValueError(f"Real SCANIA source value disagrees: {key} != {expected}")


def exact_value(obj: dict, key: str, expected: object) -> None:
    if obj.get(key) != expected or (
        isinstance(expected, bool) and type(obj.get(key)) is not bool
    ):
        raise ValueError(f"Genuine source quality safeguard mismatch: {key}")


def original_feature_profile_ok(feat: str, values: dict) -> tuple[int, int]:
    if not isinstance(feat, str) or not feat or feat in FORBIDDEN:
        raise ValueError("Found forbidden/empty target or identity in original sensor names")
    if not isinstance(values, dict):
        raise ValueError(f"Malformed observed SCANIA feature profile: {feat}")
    observed = values.get("observed_actual_values")
    missing = values.get("original_missing_values")
    if any(type(v) is not int or v < 0 for v in (observed, missing)):
        raise ValueError(f"Non-integer counts in source feature {feat}")
    if observed + missing != KNOWN_FIT:
        raise ValueError(f"Observed+missing count mismatch in original source {feat}")
    if values.get("all_missing_in_fit") is not False:
        raise ValueError(f"Unexpected completely missing genuine feature {feat}")
    if values.get("constant_in_fit") is not False:
        raise ValueError(f"Unexpected constant source feature {feat}")
    measurements = (
        values.get("mean_of_observed_train_fit_values"),
        values.get("population_std_of_observed_train_fit_values"),
        values.get("minimum_original_observed_value"),
        values.get("maximum_original_observed_value"),
    )
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) for v in measurements):
        raise ValueError(f"Malformed original numeric statistics: {feat}")
    mean, std, minimum, maximum = (float(v) for v in measurements)
    if (std < 0 or minimum > maximum or
            not minimum - max(1e-7, abs(minimum)*1e-10, abs(maximum)*1e-10) <= mean <=
            maximum + max(1e-7, abs(minimum)*1e-10, abs(maximum)*1e-10)):
        raise ValueError(f"Inconsistent real feature stats: {feat}")
    return observed, missing


def build(manifest_path: Path, profile_path: Path, review_path: Path) -> dict:
    manifest, manifest_sha = load_json_with_sha(manifest_path)
    profile, profile_sha = load_json_with_sha(profile_path)
    review, review_sha = load_json_with_sha(review_path)

    exact_value(manifest, "status", "ORIGINAL_SCANIA_V2_TRAINING_MANIFEST_CREATED")
    exact_value(manifest, "source", SOURCE)
    exact_int(manifest, "original_training_vehicles", TRAIN_VEHICLES)
    exact_int(manifest, "original_training_readouts_referenced", ALL_TRAIN)
    exact_int(manifest, "prediction_horizon_original_steps", 48)
    exact_int(manifest, "source_missing_sensor_cells_confirmed", TRAIN_SOURCE_MISSING)
    exact_value(manifest, "unknown_short_censored_has_blank_binary_target", True)
    exact_value(manifest, "original_csv_sha256_matches_owner_audit", True)
    exact_value(manifest, "original_horizon_audit_counts_match", True)
    exact_value(manifest, "source_csvs_modified", False)
    exact_value(manifest, "new_sensor_observations_generated", False)
    exact_value(manifest, "model_trained", False)
    exact_value(manifest, "publisher_file_hashes_verified", False)

    partition = manifest.get("readout_outcome_by_partition")
    if not isinstance(partition, dict) or set(partition) != {"train_fit", "internal_holdout"}:
        raise ValueError("Expected two real ID-grouped internal training partitions")
    for group, positives, negatives, unknown in (
        ("train_fit", 20721, 717274, UNKNOWN_FIT),
        ("internal_holdout", 5037, 177026, UNKNOWN_HOLDOUT),
    ):
        counts = partition[group]
        if not isinstance(counts, dict):
            raise ValueError(f"Missing genuine status counts for {group}")
        for key, expected in (
            ("recorded_repair_within_48", positives),
            ("no_recorded_repair_within_48", negatives),
            ("unknown_short_censored_followup", unknown),
        ):
            exact_int(counts, key, expected)
    counts = manifest.get("unique_source_vehicle_counts_by_partition")
    if counts != {"train_fit": 18869, "internal_holdout": 4681}:
        raise ValueError("Genuine ID-grouped split differs from owner-run manifest")

    exact_value(profile, "status", "ORIGINAL_SCANIA_TRAIN_FIT_SENSOR_PROFILE_CREATED")
    exact_value(profile, "source", SOURCE)
    exact_value(profile, "only_group_for_fitted_stats", "train_fit")
    exact_value(profile, "only_target_status_for_fitted_stats",
                "source-known binary 48-step outcome")
    exact_int(profile, "original_sensor_feature_columns", N_SENSORS)
    exact_int(profile, "original_training_readouts_verified", ALL_TRAIN)
    exact_int(profile, "original_training_vehicles_verified", TRAIN_VEHICLES)
    exact_int(profile, "actual_original_readouts_used_to_fit_stats", KNOWN_FIT)
    exact_int(profile, "actual_train_fit_readouts_with_unknown_outcome_excluded", UNKNOWN_FIT)
    exact_int(profile, "original_train_missing_sensor_cells_verified", TRAIN_SOURCE_MISSING)
    for k, expected in (
        ("source_csv_sha256_matches_owners_raw_audit", True),
        ("publisher_sha256_independently_verified", False),
        ("prediction_endpoint_fields_in_features", False),
        ("vehicle_id_or_time_step_in_features", False),
        ("unknown_outcomes_used_to_fit_stats", False),
        ("internal_holdout_values_used_to_fit_stats", False),
        ("original_source_rows_added_or_modified", False),
        ("missing_cells_imputed", False),
        ("sensor_matrix_created", False),
        ("model_trained", False),
    ):
        exact_value(profile, k, expected)

    exact_value(review, "status", "ORIGINAL_SCANIA_105_FEATURE_PROFILE_REVIEW_COMPLETED")
    exact_value(review, "source", SOURCE)
    exact_value(review, "local_original_profile_sha256", profile_sha)
    exact_int(review, "source_features_checked", N_SENSORS)
    exact_int(review, "actual_known_train_fit_readouts_per_feature", KNOWN_FIT)
    exact_int(review, "observed_source_sensor_values_in_fit", 77263458)
    exact_int(review, "original_missing_sensor_cells_in_fit", FIT_KNOWN_MISSING)
    exact_int(review, "descriptive_extreme_distance_candidates_count", 95)
    for k, expected in (
        ("all_missing_sensor_features", []),
        ("constant_observed_sensor_features", []),
        ("features_at_least_1pct_missing", []),
        ("review_thresholds_are_not_drop_or_imputation_rules", True),
        ("source_rows_modified_or_generated", False),
        ("source_sensor_values_imputed", False),
        ("model_feature_matrix_created", False),
        ("model_trained", False),
        ("publisher_hashes_verified", False),
    ):
        exact_value(review, k, expected)

    feats = profile.get("feature_profile")
    if not isinstance(feats, dict) or len(feats) != N_SENSORS:
        raise ValueError("Expected exactly 105 genuine original sensor profile entries")
    actual_observed, actual_missing = 0, 0
    for name, stats in feats.items():
        n, miss = original_feature_profile_ok(name, stats)
        actual_observed += n
        actual_missing += miss
    if (actual_missing != FIT_KNOWN_MISSING or actual_observed !=
            review["observed_source_sensor_values_in_fit"] or
            actual_observed + actual_missing != KNOWN_FIT * N_SENSORS):
        raise ValueError("Feature population does not reconcile with real owner-run quality report")

    # No fitted imputation/scaling parameters are needed: preserve missing
    # values and numeric sensor scales. The next model MUST support missing
    # numeric inputs natively; otherwise block training and define a distinct
    # fit-only learned imputation strategy.
    return {
        "status": "ORIGINAL_SCANIA_MODEL_INPUT_CONTRACT_PREPARED",
        "source": SOURCE,
        "original_training_vehicles": TRAIN_VEHICLES,
        "original_training_readouts": ALL_TRAIN,
        "horizon_original_time_steps": 48,
        "source_sensor_column_names_in_original_order": list(feats.keys()),
        "source_sensor_column_count": N_SENSORS,
        "numeric_input_policy": "parse_original_sensor_values_as_numeric",
        "source_missing_input_policy": "preserve_missing_as_missing_at_model_runtime",
        "required_model_capability": "native_missing_numeric_features",
        "scale_input_values": False,
        "clip_extreme_input_values": False,
        "automatically_drop_sensor_columns": False,
        "impute_missing_values": False,
        "original_vehicle_id_is_predictor": False,
        "original_time_step_is_predictor": False,
        "outcome_target_or_censor_endpoint_is_predictor": False,
        "internal_holdout_used_for_transform_fitting": False,
        "official_validation_test_used_for_transform_fitting": False,
        "source_readout_selection": "all existing train as-of readouts; never select by future repair time",
        "supervised_fit_known_original_readouts": KNOWN_FIT,
        "fit_unknown_short_censored_masked_from_binary_loss": UNKNOWN_FIT,
        "internal_holdout_known_original_readouts": KNOWN_HOLDOUT,
        "internal_holdout_unknown_short_censored_masked_from_binary_loss": UNKNOWN_HOLDOUT,
        "internal_split_group_key": "original vehicle_id only (never model predictor)",
        "source_feature_extreme_distance_flags_for_review": 95,
        "source_feature_flags_are_drop_rules": False,
        "source_profile_sha256": profile_sha,
        "source_quality_review_sha256": review_sha,
        "source_manifest_report_sha256": manifest_sha,
        "source_original_csv_hashes_verified_against_owner_audit_only": True,
        "publisher_file_hashes_verified": False,
        "creates_feature_matrix": False,
        "creates_source_readouts_or_events": False,
        "modifies_original_source": False,
        "fits_model": False,
        "pending_modeling_work": [
            "Select and version a learner that natively supports missing numeric inputs.",
            "At training time, read only original as-of sensor values and join targets by checked source row reference.",
            "Never use source vehicle_id, study endpoint, censor flag, future readouts or 48-step status as model predictors.",
            "Use original vehicle-grouped internal holdout; evaluate with vehicle-cluster-aware aggregation and imbalance-sensitive metrics.",
            "Unknown short-right-censored rows are not negative; masking for binary classification may cause selection bias.",
            "Assess the mismatch between train as-of candidates and source validation/test truncated histories.",
            "Keep original official validation for tuning/calibration and official test for one final evaluation.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest-report", required=True, type=Path)
    ap.add_argument("--profile", required=True, type=Path)
    ap.add_argument("--review", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite previously sealed real-source contract: {args.output}")
    result = build(args.manifest_report, args.profile, args.review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "source_sensor_column_count": result["source_sensor_column_count"],
        "supervised_fit_known_original_readouts": result["supervised_fit_known_original_readouts"],
        "fit_unknown_short_censored_masked_from_binary_loss":
            result["fit_unknown_short_censored_masked_from_binary_loss"],
        "internal_holdout_known_original_readouts":
            result["internal_holdout_known_original_readouts"],
        "internal_holdout_unknown_short_censored_masked_from_binary_loss":
            result["internal_holdout_unknown_short_censored_masked_from_binary_loss"],
        "source_missing_input_policy": result["source_missing_input_policy"],
        "scale_input_values": False,
        "clip_extreme_input_values": False,
        "impute_missing_values": False,
        "creates_feature_matrix": False,
        "fits_model": False,
        "contract_file": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
