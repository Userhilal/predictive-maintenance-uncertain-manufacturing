"""Review an EXISTING real-SCANIA v2 105-feature JSON profile without rereading or altering source data.

Consumes only the profile already generated locally by profile_scania_trainfit_sensors.py
from original SCANIA Component X v2 sensor CSVs. Checks internal consistency and
reports names of features with missingness, constants or descriptive extremes.
No new observations, labels, numeric imputations, transformations or model training.

PowerShell:
 py -3.11 src/preprocessing/review_scania_sensor_profile.py --profile data/processed/scania_trainfit_sensor_profile.json --output data/processed/scania_sensor_quality_review.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE_URL = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
FIT_KNOWN = 737995
TRAIN_READOUTS = 1122452
TRAIN_VEHICLES = 23550
FIT_UNKNOWN = 162292
TRAIN_MISSING_CELLS = 354634
N_FEATURES = 105
MISSING_REVIEW_RATE = 0.01  # Priority for human inspection, NOT a drop rule
EXTREME_SD_REVIEW = 10.0    # Descriptive flag, NOT proof of corruption or outliers


def required_count(value: object, expected: int, field: str) -> None:
    if type(value) is not int or value != expected:
        raise ValueError(f"Actual source feature profile has unexpected {field}: {value!r}")


def numeric(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Missing/non-numeric original profile value: {name}")
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f"Non-finite source profile statistic: {name}")
    return v


def review(path: Path) -> dict:
    raw_bytes = path.read_bytes()
    profile = json.loads(raw_bytes.decode("utf-8-sig"))
    if not isinstance(profile, dict):
        raise ValueError("Actual SCANIA profile must be a JSON object")

    expected = {
        "status": "ORIGINAL_SCANIA_TRAIN_FIT_SENSOR_PROFILE_CREATED",
        "source": SOURCE_URL,
        "only_group_for_fitted_stats": "train_fit",
        "only_target_status_for_fitted_stats": "source-known binary 48-step outcome",
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
    }
    for k, v in expected.items():
        if profile.get(k) != v:
            raise ValueError(f"Missing or unexpected source-profile safeguard {k}")

    for name, number in (
        ("original_sensor_feature_columns", N_FEATURES),
        ("original_training_readouts_verified", TRAIN_READOUTS),
        ("original_training_vehicles_verified", TRAIN_VEHICLES),
        ("actual_original_readouts_used_to_fit_stats", FIT_KNOWN),
        ("actual_train_fit_readouts_with_unknown_outcome_excluded", FIT_UNKNOWN),
        ("original_train_missing_sensor_cells_verified", TRAIN_MISSING_CELLS),
        ("original_train_readouts_with_missing_verified", 22481),
    ):
        required_count(profile.get(name), number, name)

    feature_map = profile.get("feature_profile")
    if not isinstance(feature_map, dict) or len(feature_map) != N_FEATURES:
        raise ValueError("Need 105 original per-feature entries in the actual profile JSON")
    forbidden = {
        "vehicle_id", "time_step", "in_study_repair",
        "length_of_study_time_step", "class_label",
        "source_derived_binary_target", "horizon48_outcome_status",
        "internal_vehicle_partition", "original_csv_row", "observation_index",
    }
    if forbidden.intersection(feature_map):
        raise ValueError("Leakage-prone target/ID fields found among the 105 sensor features")

    flagged_missing = []
    constant_features = []
    all_missing_features = []
    extreme_candidates = []
    by_missing = []
    fit_missing_cells = 0
    fit_observed_cells = 0

    for feature, stats in feature_map.items():
        if not isinstance(feature, str) or not feature or not isinstance(stats, dict):
            raise ValueError("Invalid real source feature entry")
        n = stats.get("observed_actual_values")
        missing = stats.get("original_missing_values")
        if type(n) is not int or type(missing) is not int or n < 0 or missing < 0:
            raise ValueError(f"Invalid original missing/observed counts for {feature}")
        if n + missing != FIT_KNOWN:
            raise ValueError(f"Actual readout count mismatch in source sensor feature {feature}")
        if stats.get("all_missing_in_fit") is not (n == 0):
            raise ValueError(f"Original all-missing flag disagrees for {feature}")

        fit_missing_cells += missing
        fit_observed_cells += n
        missing_fraction = missing / FIT_KNOWN
        feature_missing = {
            "source_feature": feature,
            "original_missing_count": missing,
            "missing_pct_of_known_train_fit_readouts": round(missing_fraction * 100, 6),
        }
        by_missing.append(feature_missing)
        if missing_fraction >= MISSING_REVIEW_RATE:
            flagged_missing.append(feature_missing)

        keys = {
            "mean": "mean_of_observed_train_fit_values",
            "std": "population_std_of_observed_train_fit_values",
            "min": "minimum_original_observed_value",
            "max": "maximum_original_observed_value",
        }
        if n == 0:
            all_missing_features.append(feature)
            if any(stats.get(k) is not None for k in keys.values()):
                raise ValueError(f"All-missing source feature has numeric statistics: {feature}")
            if stats.get("constant_in_fit") is not False:
                raise ValueError(f"Incorrect constant flag for all-missing feature {feature}")
            continue

        mean = numeric(stats.get(keys["mean"]), feature + "/mean")
        std = numeric(stats.get(keys["std"]), feature + "/std")
        minimum = numeric(stats.get(keys["min"]), feature + "/min")
        maximum = numeric(stats.get(keys["max"]), feature + "/max")
        if std < 0 or minimum > maximum:
            raise ValueError(f"Invalid numeric range/std in real source profile: {feature}")
        tol = max(1e-7, abs(minimum) * 1e-10, abs(maximum) * 1e-10)
        if not (minimum - tol <= mean <= maximum + tol):
            raise ValueError(f"Mean outside recorded source feature min/max: {feature}")
        is_constant = minimum == maximum
        if stats.get("constant_in_fit") is not is_constant:
            raise ValueError(f"Constant flag inconsistent with real profile: {feature}")
        if is_constant:
            constant_features.append(feature)
        if std > 0:
            distance = max(abs(minimum - mean), abs(maximum - mean)) / std
            if math.isfinite(distance) and distance >= EXTREME_SD_REVIEW:
                extreme_candidates.append({
                    "source_feature": feature,
                    "max_distance_from_mean_in_profile_std": round(distance, 3),
                    "minimum_original_observed_value": minimum,
                    "maximum_original_observed_value": maximum,
                })

    if fit_missing_cells > TRAIN_MISSING_CELLS:
        raise ValueError("Known train-fit missing cells exceed all original train missing cells")
    if fit_observed_cells + fit_missing_cells != FIT_KNOWN * N_FEATURES:
        raise ValueError("Original source per-feature population not conserved")

    by_missing.sort(key=lambda x: (-x["original_missing_count"], x["source_feature"]))
    flagged_missing.sort(key=lambda x: (-x["original_missing_count"], x["source_feature"]))
    extreme_candidates.sort(
        key=lambda x: (-x["max_distance_from_mean_in_profile_std"], x["source_feature"])
    )
    return {
        "status": "ORIGINAL_SCANIA_105_FEATURE_PROFILE_REVIEW_COMPLETED",
        "source": SOURCE_URL,
        "local_original_profile_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "source_features_checked": len(feature_map),
        "actual_known_train_fit_readouts_per_feature": FIT_KNOWN,
        "observed_source_sensor_values_in_fit": fit_observed_cells,
        "original_missing_sensor_cells_in_fit": fit_missing_cells,
        "missing_sensor_pct_among_known_train_fit_cells":
            round(100 * fit_missing_cells / (FIT_KNOWN * N_FEATURES), 6),
        "all_missing_sensor_features": sorted(all_missing_features),
        "constant_observed_sensor_features": sorted(constant_features),
        "features_at_least_1pct_missing": flagged_missing,
        "top_15_original_missing_sensor_features": by_missing[:15],
        "descriptive_extreme_distance_candidates_count": len(extreme_candidates),
        "top_15_descriptive_extreme_distance_candidates": extreme_candidates[:15],
        "review_thresholds_are_not_drop_or_imputation_rules": True,
        "source_rows_modified_or_generated": False,
        "source_sensor_values_imputed": False,
        "model_feature_matrix_created": False,
        "model_trained": False,
        "publisher_hashes_verified": False,
        "remaining_decisions": [
            "Review real individual missingness, constant features and large numeric ranges before selecting any model-only feature transforms.",
            "Extreme standardized range may reflect genuine rare values or scale; flags alone do not imply faulty sensor data.",
            "Any later fill/scale parameters must be fitted using fit-only source observations; never modify original CSVs.",
            "Original vehicle-grouped validation and UNKNOWN short-censored outcomes must be respected; no model fit here.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        default=Path("data/processed/scania_sensor_quality_review.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite prior real-source feature review: {args.output}")
    result = review(args.profile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
