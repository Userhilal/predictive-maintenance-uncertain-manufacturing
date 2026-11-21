"""Read-only Stage 6 AI4I feature integrity and train-only fit verification.

Reopens the exact approved original 10,000-row AI4I CSV, Stage 5 signed-off
assignment metadata and the already-created Stage 6 feature outputs.
Verifies 4 output SHA-256 values, all 9,973 original UDI memberships and
ALL eight predictor values against source and train-only fitted statistics.

Does NOT write/recreate features, overwrite evidence, create more splits,
download other datasets, train models or handle restricted source images.

    py -3.11 src/preprocessing/review_stage6_ai4i_features.py \
      --ai4i data/raw/ai4i2020.csv \
      --stage5-dir data/processed/stage5_eligible_splits \
      --stage6-dir data/processed/stage6_ai4i_features
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from prepare_ai4i import INPUTS, MODES, SOURCE_SHA256, TARGET, load_and_validate
from review_stage5_splits import AI_FILES, AI_QUARANTINE, review as review_stage5

STAGE5_APPROVED_REPORT_SHA = "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda"
STAGE4_APPROVED_REPORT_SHA = "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29"
SPLITS = ("train", "validation", "test")
ORIGINAL_NUMERIC = (
    "Air temperature [K]", "Process temperature [K]",
    "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]",
)
DERIVED_NUMERIC = (
    "air_temperature_K_train_z", "process_temperature_K_train_z",
    "rotational_speed_rpm_train_z", "torque_Nm_train_z", "tool_wear_min_train_z",
)
TYPE_ORDER = ("H", "L", "M")
DERIVED_TYPE = ("type_H", "type_L", "type_M")
FEATURES = (*DERIVED_TYPE, *DERIVED_NUMERIC)
HEADER = ("source_udi_not_a_feature", *FEATURES, "original_machine_failure_target_not_a_feature")
FORBIDDEN = ("UDI", "Product ID", *MODES, TARGET)
PARAMS_FILE = "ai4i_train_only_feature_contract.json"
REPORT_FILE = "stage6_feature_report.json"
EXPECTED_COUNTS = {"train": 6981, "validation": 1497, "test": 1495}
EXPECTED_LABELS = {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49},
}
OUTPUT_NAMES = {f"ai4i_{s}_features.csv" for s in SPLITS} | {PARAMS_FILE}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(path: Path, expected_fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(expected_fields):
            raise ValueError(f"Unexpected derived CSV header: {path}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Malformed original-derived CSV row: {path}")
    return rows


def nearly(a: float, b: float, label: str, *, abs_tol: float = 1e-10) -> None:
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError(f"Nonfinite original or derived numeric value in {label}")
    if not math.isclose(a, b, rel_tol=1e-12, abs_tol=abs_tol):
        raise ValueError(f"Stage 6 numerical value differs from source/train-only rule: {label}")


def verify_report(report: dict, contract: dict, prior_stage5: dict, original_sha: str) -> None:
    if (report.get("status") != "STAGE6_AI4I_TRAIN_ONLY_FEATURES_CREATED_REVIEW_REQUIRED"
            or report.get("stage6_signed_off") is not False
            or report.get("prior_stage5_report_sha256") != STAGE5_APPROVED_REPORT_SHA
            or report.get("prior_stage4_report_sha256") != STAGE4_APPROVED_REPORT_SHA
            or prior_stage5["original_stage5_report_sha256"] != STAGE5_APPROVED_REPORT_SHA
            or report.get("original_ai4i_csv_sha256") != original_sha
            or report.get("only_approved_source_dataset_engineered") != "AI4I 2020"
            or report.get("exactly_three_approved_original_sources_remain_in_project") != [
                "SCANIA Component X v2", "AI4I 2020",
                "Industrial Machinery Fault Image Dataset",
            ]
            or report.get("eligible_original_ai4i_rows") != 9973
            or report.get("original_ai4i_disputed_udis_not_used_as_features_or_training_rows") != 27
            or report.get("feature_count") != 8
            or report.get("approved_feature_names") != list(FEATURES)
            or report.get("numeric_columns_fitted_only_on_training_rows") != list(ORIGINAL_NUMERIC)
            or report.get("training_only_fit_population") != 6981):
        raise ValueError("Stage 6 source evidence/provenance/feature contract mismatch")
    for key in (
        "original_target_and_udi_present_only_as_output_metadata_not_predictors",
        "train_only_fitted_stats_applied_to_validation_and_test",
        "no_original_source_files_or_labels_modified",
        "no_extra_dataset_or_supporting_manuals",
        "no_fabricated_cross_source_same_machine_links",
        "no_synthetic_row_or_photo_generated",
        "no_model_training_or_evaluation",
    ):
        if report.get(key) is not True:
            raise ValueError(f"Stage 6 forbidden operation or missing safeguard: {key}")
    sc = report.get("scania", {})
    im = report.get("industrial_fault_images", {})
    if (sc.get("source_official_vehicles_train_validation_test_preserved") != [23550, 5046, 5045]
            or sc.get("source_readouts_not_resplit_or_engineered") != 1516819
            or sc.get("source_train_repair_censor_target_differs_from_official_five_class_validation_test") is not True
            or sc.get("supervised_source_task_compatible_feature_matrix_created") is not False
            or sc.get("no_scania_sensor_values_modified") is not True
            or im.get("source_members") != 234
            or im.get("independently_verified_original_image_class_count") != 0
            or im.get("per_photo_reuse_rights_verified") is not False
            or im.get("supervised_image_features_created") is not False
            or im.get("image_bytes_read_written_or_transmitted") is not False):
        raise ValueError("SCANIA source-task / image rights restrictions incorrectly cleared")
    if (contract.get("status") != "STAGE6_AI4I_TRAIN_ONLY_FEATURE_CONTRACT_PRELIMINARY"
            or contract.get("original_ai4i_csv_sha256") != original_sha
            or contract.get("stage5_owner_verified_report_sha256") != STAGE5_APPROVED_REPORT_SHA
            or contract.get("approved_feature_columns_in_order") != list(FEATURES)
            or contract.get("original_source_columns_used_as_predictors") != list(INPUTS)
            or contract.get("forbidden_columns_not_in_predictors") != list(FORBIDDEN)
            or contract.get("type_one_hot_categories") != list(TYPE_ORDER)
            or contract.get("prediction_target_metadata_only") != HEADER[-1]
            or contract.get("identifier_metadata_only") != HEADER[0]
            or contract.get("train_only_fit_original_udi_count") != 6981):
        raise ValueError("Train-only model input feature contract no longer matches original sources")
    for key in (
        "no_feature_selection_using_validation_or_test",
        "no_label_derived_predictors", "no_original_udi_as_predictor",
        "no_imputation_or_clipping_or_outlier_deletion",
        "no_class_rebalancing_or_synthetic_rows",
        "no_model_fitted",
    ):
        if contract.get(key) is not True:
            raise ValueError(f"Train-only feature contract violated restriction: {key}")
    if set(FEATURES) & set(FORBIDDEN):
        raise ValueError("The original target/identifier/flag leaked into predictor columns")


def verify_train_parameters(
    train_source: list[dict[str, str]], contract: dict
) -> dict[str, dict[str, float]]:
    if len(train_source) != 6981:
        raise ValueError("Stage 6 numeric statistics must be trained on exactly 6,981 original UDI rows")
    actual = contract.get("numeric_fitted_original_train_only")
    if not isinstance(actual, dict) or set(actual) != set(ORIGINAL_NUMERIC):
        raise ValueError("Five train-only numeric fields missing or extra")
    params = {}
    for name, feature in zip(ORIGINAL_NUMERIC, DERIVED_NUMERIC):
        nums = [float(row[name]) for row in train_source]
        mean = math.fsum(nums) / len(nums)
        variance = math.fsum((v - mean) ** 2 for v in nums) / len(nums)
        std = math.sqrt(variance)
        if not all(map(math.isfinite, (mean, variance, std))) or std <= 0:
            raise ValueError(f"Unexpected invalid original train feature: {name}")
        stored = actual[name]
        if (stored.get("derived_feature_name") != feature
                or stored.get("train_fit_rows") != 6981
                or stored.get("missing_original_train_values") != 0):
            raise ValueError(f"Train-only feature population/schema changed: {name}")
        for key, expected in (
            ("train_only_mean", mean),
            ("train_only_population_std", std),
            ("train_only_min_observed", min(nums)),
            ("train_only_max_observed", max(nums)),
        ):
            try:
                result = float(stored[key])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Unusable train-only statistic {name}: {key}") from exc
            nearly(result, expected, f"{name}/{key}")
        params[name] = {"mean": mean, "std": std}
    return params


def verify(
    original_ai4i_path: Path, stage5_dir: Path, stage6_dir: Path,
) -> dict:
    # Check Stage 5 original assignment hashes and exact seeded partitions
    # BEFORE examining any derived feature output.
    prior = review_stage5(stage5_dir)
    if (prior["status"] != "STAGE5_ACTUAL_SOURCE_SPLIT_MANIFESTS_REVIEWED_READ_ONLY"
            or prior["original_stage5_report_sha256"] != STAGE5_APPROVED_REPORT_SHA
            or prior["all_seven_original_assignment_csv_sha256_verified"] is not True
            or prior["ai4i_exact_seeded_class_type_assignment_reconstructed"] is not True):
        raise ValueError("Actual Stage 5 eligible source partition provenance has changed")
    source, source_sha = load_and_validate(original_ai4i_path)
    if source_sha != SOURCE_SHA256 or len(source) != 10000:
        raise ValueError("Original publisher AI4I source SHA/row count invalid")
    raw_by_udi = {r["UDI"]: r for r in source}
    if len(raw_by_udi) != 10000:
        raise ValueError("Original source UDI references not unique")
    report_path = stage6_dir / REPORT_FILE
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    contract_path = stage6_dir / PARAMS_FILE
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    verify_report(report, contract, prior, source_sha)

    hashes = report.get("output_file_sha256")
    if not isinstance(hashes, dict) or set(hashes) != OUTPUT_NAMES:
        raise ValueError("Four Stage 6 source-derived output hashes missing/extra")
    for name in sorted(OUTPUT_NAMES):
        if digest(stage6_dir / name) != hashes[name]:
            raise ValueError(f"Stage 6 original output bytes disagree with manifest SHA: {name}")

    # Read the Stage 5 original assignments exactly and preserve their order.
    original_by_split: dict[str, list[dict[str, str]]] = {}
    eligible_udis = set()
    for split in SPLITS:
        assignments = csv_rows(
            stage5_dir / AI_FILES[split],
            ("UDI", "original_machine_failure", "original_product_type"),
        )
        if len(assignments) != EXPECTED_COUNTS[split]:
            raise ValueError(f"Original Stage 5 cohort size changed: {split}")
        selected = []
        for a in assignments:
            udi = a["UDI"]
            if udi in eligible_udis:
                raise ValueError(f"Original source UDI reused across splits: {udi}")
            eligible_udis.add(udi)
            src = raw_by_udi.get(udi)
            if (src is None or src[TARGET] != a["original_machine_failure"]
                    or src["Type"] != a["original_product_type"]):
                raise ValueError(f"Stage 5 assignment differs from source row: {udi}")
            selected.append(src)
        original_by_split[split] = selected
    quarantine_csv = stage5_dir / AI_QUARANTINE
    with quarantine_csv.open(encoding="utf-8-sig", newline="") as stream:
        queue = list(csv.DictReader(stream))
    quarantined = {r["UDI"] for r in queue}
    if len(queue) != 27:
        raise ValueError("Original 27-case quarantine size changed")
    if (len(quarantined) != 27 or eligible_udis & quarantined
            or len(eligible_udis) != 9973
            or eligible_udis | quarantined != set(raw_by_udi)):
        raise ValueError("Stage 6 UDI coverage includes excluded original source rows")
    # Check the exact disputed original target/flag membership, not just counts.
    real_disputed = {
        r["UDI"] for r in source
        if r[TARGET] != str(int(any(r[m] == "1" for m in MODES)))
    }
    if real_disputed != quarantined:
        raise ValueError("Original 27 source label disagreements not preserved")

    train_params = verify_train_parameters(original_by_split["train"], contract)
    results = {}
    values_checked = 0
    for split in SPLITS:
        output_path = stage6_dir / f"ai4i_{split}_features.csv"
        transformed = csv_rows(output_path, HEADER)
        originals = original_by_split[split]
        counts = Counter()
        if len(transformed) != len(originals):
            raise ValueError(f"Engineered feature population changed: {split}")
        for original, derived in zip(originals, transformed):
            udi = original["UDI"]
            if (derived["source_udi_not_a_feature"] != udi
                    or derived["original_machine_failure_target_not_a_feature"] != original[TARGET]):
                raise ValueError(f"Original source metadata label/UDI mismatch in {split}: {udi}")
            counts[original[TARGET]] += 1
            for category, feature in zip(TYPE_ORDER, DERIVED_TYPE):
                if derived[feature] != ("1" if original["Type"] == category else "0"):
                    raise ValueError(f"Original Type one-hot derivation mismatch: {split}/{udi}/{feature}")
                values_checked += 1
            for column, feature in zip(ORIGINAL_NUMERIC, DERIVED_NUMERIC):
                try:
                    observed = float(derived[feature])
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid derived feature in {split}: {udi}/{feature}") from exc
                params = train_params[column]
                expected = (float(original[column]) - params["mean"]) / params["std"]
                nearly(observed, expected, f"{split}/{udi}/{feature}")
                values_checked += 1
        expected_counts = EXPECTED_LABELS[split]
        stored = report.get("per_partition", {}).get(split, {})
        if (dict(counts) != expected_counts
                or stored.get("source_eligible_rows") != EXPECTED_COUNTS[split]
                or stored.get("original_target_counts") != expected_counts
                or stored.get("source_udi_membership_unchanged") is not True
                or stored.get("same_original_training_fitted_numeric_parameters_used") is not True):
            raise ValueError(f"Stage 6 original cohort label/UDI population altered: {split}")
        results[split] = {
            "original_udis_verified": len(originals),
            "original_failure_target_counts": dict(sorted(counts.items())),
            "all_eight_predictors_recomputed_from_original_source": True,
        }

    return {
        "status": "STAGE6_ACTUAL_TRAIN_ONLY_FEATURES_VERIFIED_READ_ONLY",
        "original_stage6_report_sha256": digest(report_path),
        "prior_stage5_owner_verified_report_sha256": STAGE5_APPROVED_REPORT_SHA,
        "actual_original_ai4i_source_sha256_verified": True,
        "all_four_stage6_output_file_sha256_verified": True,
        "all_9973_original_source_udi_memberships_and_targets_verified": True,
        "all_27_original_disputed_udis_excluded_and_quarantined": True,
        "numeric_original_features_fit_only_on_6981_training_udis_verified": len(train_params),
        "numeric_train_only_fitted_means_standard_deviations_and_ranges_recomputed": True,
        "all_8_predictor_values_recomputed_from_original_source": True,
        "individual_predictor_values_verified": values_checked,
        "per_partition": results,
        "scania_unified_supervised_feature_matrix_created": False,
        "supervised_image_features_created": False,
        "image_class_truth_and_reuse_rights_verified": False,
        "source_data_or_original_labels_modified_by_review": False,
        "feature_stage6_technical_signoff_still_requires_review": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ai4i", type=Path, required=True)
    parser.add_argument("--stage5-dir", type=Path, required=True)
    parser.add_argument("--stage6-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.ai4i, args.stage5_dir, args.stage6_dir),
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
