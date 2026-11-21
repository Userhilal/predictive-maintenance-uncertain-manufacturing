r"""Stage 6 ONLY: leak-safe AI4I feature engineering from approved Stage 5 IDs.

The sole supervised source used for feature transforms is the original
publisher-synthetic AI4I 2020 CSV. Exactly 9,973 previously accepted UDIs
are joined to the ORIGINAL CSV after Stage 5 manifest hash/membership checks;
27 original disputed labels remain excluded. Fit numerical standardization
on TRAIN ONLY and apply unchanged parameters to validation/test.

8 predictors: 3 one-hot original Type indicators (H,L,M), plus 5
train-only standardized original numeric sensor/process measurements.
Source UDI/target are output provenance/label metadata, NEVER predictors.
No source edits, invented examples, target-derived features, class balancing,
temporal assumptions, learned parameters from validation/test, or models.
SCANIA distinct original outcome tasks NOT converted to one shared target.
Fault image label/rights evidence still BLOCKS supervised image features.

Run from Windows repository root:
    py -3.11 src/preprocessing/engineer_stage6_ai4i_features.py \
      --ai4i data/raw/ai4i2020.csv \
      --stage5-dir data/processed/stage5_eligible_splits \
      --stage4-policy docs/datasets/stage4-label-eligibility-policy.json \
      --output-dir data/processed/stage6_ai4i_features
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from prepare_ai4i import (
    INPUTS, MODES, SOURCE_SHA256, TARGET, load_and_validate,
)
from review_stage5_splits import (
    AI_FILES, AI_QUARANTINE, STAGE4_HASH, review as review_stage5,
)

STAGE5_ORIGINAL_REPORT_SHA256 = "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda"
STAGE4_POLICY_ID = "STAGE4_SOURCE_LABEL_VERIFICATION_RISK_QUALIFIED_2026_11_21"
SPLITS = ("train", "validation", "test")
NUMERIC_ORIGINALS = INPUTS[1:]
TYPE_DOMAIN = ("H", "L", "M")
TYPE_FEATURES = ("type_H", "type_L", "type_M")
NUMERIC_FEATURES = (
    "air_temperature_K_train_z",
    "process_temperature_K_train_z",
    "rotational_speed_rpm_train_z",
    "torque_Nm_train_z",
    "tool_wear_min_train_z",
)
FEATURES = (*TYPE_FEATURES, *NUMERIC_FEATURES)
ROW_FIELDS = ("source_udi_not_a_feature", *FEATURES, "original_machine_failure_target_not_a_feature")
EXPECTED_COUNT = {"train": 6981, "validation": 1497, "test": 1495}
EXPECTED_LABELS = {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49},
}
FORBIDDEN_MODEL_FEATURES = ("UDI", "Product ID", *MODES, TARGET)
PARAMS_FILE = "ai4i_train_only_feature_contract.json"
REPORT_FILE = "stage6_feature_report.json"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_assignment(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["UDI", "original_machine_failure", "original_product_type"]:
            raise ValueError(f"Unexpected previously verified Stage 5 assignment schema: {path}")
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError(f"Malformed Stage 5 source assignment: {path}")
    return rows


def check_inputs(source: Path, stage5_dir: Path, policy_file: Path) -> tuple[dict, dict, dict]:
    reviewed = review_stage5(stage5_dir)
    if (reviewed["status"] != "STAGE5_ACTUAL_SOURCE_SPLIT_MANIFESTS_REVIEWED_READ_ONLY"
            or reviewed["original_stage5_report_sha256"] != STAGE5_ORIGINAL_REPORT_SHA256
            or reviewed["original_stage4_report_sha256"] != STAGE4_HASH
            or reviewed["all_seven_original_assignment_csv_sha256_verified"] is not True
            or reviewed["ai4i_exact_seeded_class_type_assignment_reconstructed"] is not True
            or reviewed["ai4i_all_10000_original_udi_references_accounted"] is not True
            or reviewed["images_supervised_partitions_created"] is not False):
        raise ValueError("Stage 5 original eligible source assignments no longer match approved review")
    stage5_report = json.loads((stage5_dir / "stage5_split_report.json").read_text(encoding="utf-8-sig"))
    if sha256(policy_file) != stage5_report["stage4_label_eligibility_policy_sha256"]:
        raise ValueError("Stage 4 source-label eligibility policy changed after Stage 5")
    policy = json.loads(policy_file.read_text(encoding="utf-8-sig"))
    p = policy["source_policy"]
    if (policy.get("policy_id") != STAGE4_POLICY_ID
            or p["ai4i"]["provisionally_eligible_original_rows"] != 9973
            or p["ai4i"]["source_target_mode_mismatches"] != 27
            or p["ai4i"]["failure_mode_columns_must_not_be_input_features_for_global_failure_prediction"] is not True
            or p["industrial_fault_images"]["all_234_supervised_image_training_or_evaluation_eligibility"] != "BLOCKED"
            or p["industrial_fault_images"]["source_folder_labeled_but_independently_truth_verified"] != 0
            or p["scania"]["inventing_common_binary_target_from_source_five_class_labels_prohibited"] is not True
            or policy["full_three_source_supervised_training_approved"] is not False):
        raise ValueError("Original Stage 4 photo/SCANIA/AI4I usage restrictions not satisfied")
    original_rows, original_hash = load_and_validate(source)
    if len(original_rows) != 10000 or original_hash != SOURCE_SHA256:
        raise ValueError("Only exactly the owner's original publisher AI4I CSV is allowed")
    originals = {r["UDI"]: r for r in original_rows}
    if len(originals) != 10000:
        raise ValueError("Duplicate original AI4I UDI in source")
    # The genuine source has precisely 27 original binary/mode disagreements.
    disputed = {
        r["UDI"] for r in original_rows
        if r[TARGET] != str(int(any(r[m] == "1" for m in MODES)))
    }
    quarantine = set()
    with (stage5_dir / AI_QUARANTINE).open(encoding="utf-8-sig", newline="") as file:
        quarantine_rows = list(csv.DictReader(file))
    for r in quarantine_rows:
        quarantine.add(r["UDI"])
    if (len(quarantine_rows) != 27 or len(quarantine) != 27
            or disputed != quarantine):
        raise ValueError("Stage 5 quarantine no longer excludes the exact 27 source-disputed UDIs")
    return reviewed, original_hash, originals


def source_rows_by_split(stage5_dir: Path, originals: dict) -> dict[str, list[dict[str, str]]]:
    by_split = {}
    seen = set()
    for split in SPLITS:
        assignments = read_assignment(stage5_dir / AI_FILES[split])
        if len(assignments) != EXPECTED_COUNT[split]:
            raise ValueError(f"Unexpected eligible original AI4I split size: {split}")
        verified_rows = []
        for r in assignments:
            udi = r["UDI"]
            if udi in seen:
                raise ValueError(f"Source UDI appears in more than one Stage 5 split: {udi}")
            seen.add(udi)
            original = originals.get(udi)
            if (original is None or original[TARGET] != r["original_machine_failure"]
                    or original["Type"] != r["original_product_type"]):
                raise ValueError(f"Stage 5 cohort assignment mismatches original AI4I source: {udi}")
            verified_rows.append(original)
        if dict(Counter(row[TARGET] for row in verified_rows)) != EXPECTED_LABELS[split]:
            raise ValueError(f"Original source label counts changed in {split}")
        by_split[split] = verified_rows
    if len(seen) != 9973:
        raise ValueError("Stage 6 original-source supervised UDI coverage changed")
    return by_split


def fit_train_only(train: list[dict[str, str]]) -> dict[str, dict]:
    if len(train) != EXPECTED_COUNT["train"]:
        raise ValueError("Fit must see only the 6,981 genuinely assigned Stage 5 train rows")
    if set(row["Type"] for row in train) != set(TYPE_DOMAIN):
        raise ValueError("Original AI4I training source Type domain is incomplete")
    contract = {}
    for original_name, output_name in zip(NUMERIC_ORIGINALS, NUMERIC_FEATURES):
        values = [float(row[original_name]) for row in train]
        mean = math.fsum(values) / len(values)
        variance = math.fsum((x - mean) ** 2 for x in values) / len(values)
        std = math.sqrt(variance)
        if not all(map(math.isfinite, (mean, variance, std))) or std <= 0:
            raise ValueError(f"Nonfinite/constant original feature in eligible training source: {original_name}")
        contract[original_name] = {
            "derived_feature_name": output_name,
            "train_fit_rows": len(values),
            "train_only_mean": mean,
            "train_only_population_std": std,
            "train_only_min_observed": min(values),
            "train_only_max_observed": max(values),
            "missing_original_train_values": 0,
        }
    return contract


def create_feature_rows(rows: list[dict[str, str]], params: dict) -> list[dict[str, str]]:
    out = []
    for source in rows:
        row: dict[str, str] = {"source_udi_not_a_feature": source["UDI"]}
        for t, feature in zip(TYPE_DOMAIN, TYPE_FEATURES):
            row[feature] = "1" if source["Type"] == t else "0"
        for original_name, output_name in zip(NUMERIC_ORIGINALS, NUMERIC_FEATURES):
            number = float(source[original_name])
            stat = params[original_name]
            z = (number - stat["train_only_mean"]) / stat["train_only_population_std"]
            if not math.isfinite(z):
                raise ValueError(f"Nonfinite derived feature on genuine original UDI {source['UDI']}")
            row[output_name] = format(z, ".17g")
        row["original_machine_failure_target_not_a_feature"] = source[TARGET]
        out.append(row)
    return out


def write_feature_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=ROW_FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def build(original_ai4i: Path, stage5_dir: Path, policy_file: Path,
          output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite previously created Stage 6 feature evidence: {output_dir}")
    if set(FEATURES) & set(FORBIDDEN_MODEL_FEATURES):
        raise ValueError("Original labels/identifiers/failure mode flags cannot be predictors")
    reviewed, source_hash, original = check_inputs(original_ai4i, stage5_dir, policy_file)
    by_split = source_rows_by_split(stage5_dir, original)
    params = fit_train_only(by_split["train"])
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".stage6-original-ai4i-", dir=output_dir.parent))
    try:
        per_cohort = {}
        for split in SPLITS:
            feature_rows = create_feature_rows(by_split[split], params)
            write_feature_csv(stage / f"ai4i_{split}_features.csv", feature_rows)
            counts = dict(sorted(Counter(r["original_machine_failure_target_not_a_feature"]
                                        for r in feature_rows).items()))
            if len(feature_rows) != EXPECTED_COUNT[split] or counts != EXPECTED_LABELS[split]:
                raise ValueError(f"Stage 6 output row/label counts mismatch original source: {split}")
            per_cohort[split] = {
                "source_eligible_rows": len(feature_rows),
                "original_target_counts": counts,
                "source_udi_membership_unchanged": True,
                "same_original_training_fitted_numeric_parameters_used": True,
            }
        feature_contract = {
            "status": "STAGE6_AI4I_TRAIN_ONLY_FEATURE_CONTRACT_PRELIMINARY",
            "original_ai4i_csv_sha256": source_hash,
            "stage5_owner_verified_report_sha256": reviewed["original_stage5_report_sha256"],
            "source": "AI4I 2020 unchanged Mendeley published-synthetic CSV",
            "prediction_target_metadata_only": "original_machine_failure_target_not_a_feature",
            "identifier_metadata_only": "source_udi_not_a_feature",
            "approved_feature_columns_in_order": list(FEATURES),
            "original_source_columns_used_as_predictors": list(INPUTS),
            "forbidden_columns_not_in_predictors": list(FORBIDDEN_MODEL_FEATURES),
            "type_one_hot_categories": list(TYPE_DOMAIN),
            "numeric_normalization": "train-only fitted mean and population standard deviation; applied unchanged to validation/test",
            "train_only_fit_original_udi_count": 6981,
            "numeric_fitted_original_train_only": params,
            "no_feature_selection_using_validation_or_test": True,
            "no_label_derived_predictors": True,
            "no_original_udi_as_predictor": True,
            "no_imputation_or_clipping_or_outlier_deletion": True,
            "no_class_rebalancing_or_synthetic_rows": True,
            "no_model_fitted": True,
        }
        params_path = stage / PARAMS_FILE
        params_path.write_text(json.dumps(feature_contract, indent=2) + "\n", encoding="utf-8")
        report = {
            "status": "STAGE6_AI4I_TRAIN_ONLY_FEATURES_CREATED_REVIEW_REQUIRED",
            "only_approved_source_dataset_engineered": "AI4I 2020",
            "exactly_three_approved_original_sources_remain_in_project": [
                "SCANIA Component X v2", "AI4I 2020",
                "Industrial Machinery Fault Image Dataset",
            ],
            "prior_stage5_report_sha256": reviewed["original_stage5_report_sha256"],
            "prior_stage4_report_sha256": reviewed["original_stage4_report_sha256"],
            "original_ai4i_csv_sha256": source_hash,
            "eligible_original_ai4i_rows": 9973,
            "original_ai4i_disputed_udis_not_used_as_features_or_training_rows": 27,
            "feature_count": len(FEATURES),
            "approved_feature_names": list(FEATURES),
            "numeric_columns_fitted_only_on_training_rows": list(NUMERIC_ORIGINALS),
            "training_only_fit_population": 6981,
            "original_target_and_udi_present_only_as_output_metadata_not_predictors": True,
            "train_only_fitted_stats_applied_to_validation_and_test": True,
            "per_partition": per_cohort,
            "scania": {
                "source_official_vehicles_train_validation_test_preserved": [23550, 5046, 5045],
                "source_readouts_not_resplit_or_engineered": 1516819,
                "source_train_repair_censor_target_differs_from_official_five_class_validation_test": True,
                "supervised_source_task_compatible_feature_matrix_created": False,
                "no_scania_sensor_values_modified": True,
            },
            "industrial_fault_images": {
                "source_members": 234,
                "independently_verified_original_image_class_count": 0,
                "per_photo_reuse_rights_verified": False,
                "supervised_image_features_created": False,
                "image_bytes_read_written_or_transmitted": False,
                "image_use_remains_blocked_by_issue": 43,
            },
            "no_original_source_files_or_labels_modified": True,
            "no_extra_dataset_or_supporting_manuals": True,
            "no_fabricated_cross_source_same_machine_links": True,
            "no_synthetic_row_or_photo_generated": True,
            "no_model_training_or_evaluation": True,
            "stage6_signed_off": False,
            "output_file_sha256": {
                path.name: sha256(path) for path in sorted(stage.iterdir()) if path.is_file()
            },
            "next_review": "Review actual original-owner feature output and verify all train-only parameters and cohort source UDI memberships before Stage 6 technical sign-off",
        }
        (stage / REPORT_FILE).write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        stage.rename(output_dir)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ai4i", type=Path, required=True)
    p.add_argument("--stage5-dir", type=Path, required=True)
    p.add_argument("--stage4-policy", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    report = build(a.ai4i, a.stage5_dir, a.stage4_policy, a.output_dir)
    print(json.dumps({
        "status": report["status"],
        "actual_prior_stage5_report_sha256": report["prior_stage5_report_sha256"],
        "ai4i_train_only_fit_rows": report["training_only_fit_population"],
        "ai4i_eligible_original_rows": report["eligible_original_ai4i_rows"],
        "ai4i_disputed_source_udis_excluded": report[
            "original_ai4i_disputed_udis_not_used_as_features_or_training_rows"
        ],
        "ai4i_derived_feature_count": report["feature_count"],
        "ai4i_feature_names": report["approved_feature_names"],
        "ai4i_partition_rows": {
            key: part["source_eligible_rows"] for key, part in report["per_partition"].items()
        },
        "ai4i_target_counts_by_partition": {
            key: part["original_target_counts"] for key, part in report["per_partition"].items()
        },
        "scania_supervised_feature_matrix_created": False,
        "supervised_image_features_created": False,
        "source_files_or_labels_changed": False,
        "stage6_signed_off": False,
        "full_report": str(a.output_dir / REPORT_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
