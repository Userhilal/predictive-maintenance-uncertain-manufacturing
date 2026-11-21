r"""Stage 7 ONLY: final original-source pipeline integrity & scope/eligibility audit.

No extra datasets. Rerun Stage 3/4/5/6 read-only provenance and exact
row-level feature checks, verify all 9 original SCANIA CSV SHA-256 hashes,
the original unmodified AI4I CSV and original Kaggle ZIP fingerprint,
and produce transparent per-partition AI4I tabular diagnostics.

Stage 7 does NOT create another dataset, split, feature fit, model, photo
annotation, authorized license, or common SCANIA train/val/test target.
It cannot certify FULL three-source supervised multimodal readiness.

PowerShell from repository root, after Stage 6 qualified signoff merged:
    py -3.11 src/preprocessing/validate_stage7_final_data.py \
      --scania-data "C:\Users\hindh\Documents\2024-34-2\data" \
      --images-zip "C:\Users\hindh\Downloads\archive.zip" \
      --output-dir data/processed/stage7_final_validation
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

from prepare_ai4i import SOURCE_SHA256 as AI4I_SHA, load_and_validate
from prepare_scania import EXPECTED_FILES as SCANIA_FILES, validate_audit
from prepare_fault_images import SOURCE_SHA256 as IMAGE_ARCHIVE_SHA
from review_stage3_cleaning import review as review_stage3
from review_stage4_labels import review as review_stage4
from review_stage5_splits import review as review_stage5
from review_stage6_ai4i_features import (
    DERIVED_NUMERIC, DERIVED_TYPE, HEADER, verify as review_stage6,
)
from verify_stage4_labels import scan_source_labels

# Actual owner-run read-only review fingerprints, not publisher signatures.
STAGE2_SHA = "07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67"
STAGE3_SHA = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
STAGE4_SHA = "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29"
STAGE5_SHA = "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda"
STAGE6_SHA = "0250e7063eaae1f551a843cde3f963ba95f16f08cb261bd40b592783c58a3973"
SOURCES = (
    "SCANIA Component X v2", "AI4I 2020",
    "Industrial Machinery Fault Image Dataset",
)
COUNTS = {"train": 6981, "validation": 1497, "test": 1495}
LABELS = {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49},
}
TYPES = {
    "train": {"H": 699, "L": 4189, "M": 2093},
    "validation": {"H": 150, "L": 898, "M": 449},
    "test": {"H": 149, "L": 897, "M": 449},
}
FULL_BLOCKS = (
    "Original SCANIA train repair-event/right-censor targets are not a ready common supervised task with official validation/test five-class labels",
    "All 234 original Kaggle image labels lack independent class verification, with 8 quarantined label/provenance cases",
    "Exact archive and individual image reuse rights are not verified, so supervised image and permission-dependent use remain blocked",
    "The three independent original sources do not demonstrate same-machine pairing or linked multimodal training records",
    "AI4I is an originally publisher-synthetic, IID-like internal benchmark and cannot demonstrate real-factory/future-machine generalization",
)
REPORT_FILE = "stage7_final_source_validation_report.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_policy(policy_path: Path, stage5_dir: Path) -> dict:
    policy = json.loads(policy_path.read_text(encoding="utf-8-sig"))
    old_stage5 = json.loads(
        (stage5_dir / "stage5_split_report.json").read_text(encoding="utf-8-sig")
    )
    p = policy["source_policy"]
    if (digest(policy_path) != old_stage5["stage4_label_eligibility_policy_sha256"]
            or p["exactly_three_original_sources"] != list(SOURCES)
            or p["ai4i"]["source_target_mode_mismatches"] != 27
            or p["ai4i"]["provisionally_eligible_original_rows"] != 9973
            or p["ai4i"]["disputed_original_rows_training_status"] !=
               "quarantined_not_in_supervised_split"
            or p["scania"]["inventing_common_binary_target_from_source_five_class_labels_prohibited"] is not True
            or p["industrial_fault_images"]["all_234_supervised_image_training_or_evaluation_eligibility"] != "BLOCKED"
            or p["industrial_fault_images"]["source_folder_labeled_but_independently_truth_verified"] != 0
            or p["industrial_fault_images"]["rights_and_provenance_evidence_required_before_permission_dependent_use"] is not True
            or policy["full_three_source_supervised_training_approved"] is not False):
        raise ValueError("Previously signed-off Stage 4 label/rights restrictions were altered")
    return policy


def verify_scania_sources(data_dir: Path, audit_path: Path) -> dict:
    audit = validate_audit(audit_path)
    if audit["overall"]["vehicles"] != 33641 or audit["overall"]["readouts"] != 1516819:
        raise ValueError("SCANIA approved original source dataset population changed")
    original_files = {}
    for filename in SCANIA_FILES:
        actual = data_dir / filename
        actual_hash = digest(actual)
        expected_hash = audit["checksums"][filename]["sha256"]
        if actual_hash != expected_hash:
            raise ValueError(f"Original SCANIA CSV differs from owner-run audit: {filename}")
        original_files[filename] = actual_hash
    source_labels = scan_source_labels(data_dir, audit)
    counts = {split: source_labels[split]["source_vehicle_rows"]
              for split in ("train", "validation", "test")}
    if counts != {"train": 23550, "validation": 5046, "test": 5045}:
        raise ValueError("SCANIA official distinct original vehicle cohort sizes changed")
    return {
        "original_source_csv_files_hashed_and_verified": len(original_files),
        "original_source_csv_sha256": original_files,
        "original_vehicle_cohorts": counts,
        "original_operational_readouts_preserved": 1516819,
        "original_missing_sensor_cells_preserved": 481376,
        "original_source_train_right_censor_target_and_val_test_five_class_distinct": True,
        "unified_cross_cohort_supervised_target_approved": False,
        "original_source_file_bytes_unchanged_relative_to_owner_audit": True,
    }


def verify_image_archive(archive: Path, stage3_dir: Path, stage3: dict, stage4: dict) -> dict:
    archive_hash = digest(archive)
    stage3_original_report = json.loads(
        (stage3_dir / "stage3_cleaning_report.json").read_text(encoding="utf-8-sig")
    )
    if (archive_hash != IMAGE_ARCHIVE_SHA
            or archive_hash !=
               stage3_original_report["industrial_fault_images"]["original_archive_sha256"]
            or stage3["all_three_image_manifests_sha256_verified"] is not True
            or stage4["image_review_queue_unresolved_entries"] != 8
            or stage4["individual_image_labels_independently_verified"] != 0
            or stage4["kaggle_image_reuse_rights_verified"] is not False):
        raise ValueError("Original ZIP identity / image source-label rights quarantine changed")
    # Hash the original ZIP without decoding, extracting, copying, forwarding
    # or deriving embeddings/visual class labels from any contained image.
    return {
        "original_archive_file_sha256": archive_hash,
        "original_archive_bytes_match_owner_stage3_source": True,
        "original_zip_member_references_from_owner_reviewed_stage3": 234,
        "provisional_source_folder_labels_not_independently_verified": 219,
        "previously_quarantined_source_image_label_or_provenance_cases": 8,
        "source_archive_individual_image_classes_independently_verified": 0,
        "license_or_per_photo_reuse_rights_verified": False,
        "supervised_image_eligibility": "BLOCKED",
        "photo_bytes_extracted_transformed_or_uploaded": False,
        "this_run_did_not_independently_inspect_image_pixels": True,
    }


def source_feature_diagnostics(stage6_dir: Path, original_ai4i: Path) -> dict:
    original_rows, original_hash = load_and_validate(original_ai4i)
    if len(original_rows) != 10000 or original_hash != AI4I_SHA:
        raise ValueError("Original AI4I 2020 source file changed")
    stats = {}
    for split in ("train", "validation", "test"):
        path = stage6_dir / f"ai4i_{split}_features.csv"
        with path.open("r", newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != list(HEADER):
                raise ValueError(f"Original AI4I derived feature CSV header changed: {split}")
            counts = Counter()
            types = Counter()
            values = {field: [] for field in DERIVED_NUMERIC}
            n = 0
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"Malformed Stage 6 feature row: {split}")
                n += 1
                label = row["original_machine_failure_target_not_a_feature"]
                counts[label] += 1
                flags = tuple(row[name] for name in DERIVED_TYPE)
                if flags not in (("1","0","0"),("0","1","0"),("0","0","1")):
                    raise ValueError(f"Non-one-hot original Type values in {split}")
                types[("H", "L", "M")[flags.index("1")]] += 1
                for field in DERIVED_NUMERIC:
                    value = float(row[field])
                    if not math.isfinite(value):
                        raise ValueError(f"Nonfinite source derived numeric feature: {split}/{field}")
                    values[field].append(value)
        if n != COUNTS[split] or dict(counts) != LABELS[split] or dict(types) != TYPES[split]:
            raise ValueError(f"AI4I original-derived source labels/Type changed in {split}")
        per_feature = {}
        for name, nums in values.items():
            mean = math.fsum(nums) / n
            pop_std = math.sqrt(math.fsum((v - mean) ** 2 for v in nums) / n)
            if split == "train" and (abs(mean) > 1e-9 or abs(pop_std - 1.0) > 1e-9):
                raise ValueError(f"Training-only original z-score centered/scaled incorrectly: {name}")
            per_feature[name] = {
                "observed_original_derived_rows": n,
                "mean_source_derived_train_z": mean,
                "population_std_source_derived_train_z": pop_std,
                "observed_min_z": min(nums),
                "observed_max_z": max(nums),
                "observed_abs_z_greater_than_3_count_descriptive_only":
                    sum(abs(v) > 3 for v in nums),
            }
        stats[split] = {
            "eligible_original_source_rows": n,
            "original_target_counts": dict(sorted(counts.items())),
            "original_Type_counts": dict(sorted(types.items())),
            "original_failure_prevalence": counts["1"] / n,
            "numeric_feature_diagnostics": per_feature,
        }
    return {
        "original_source_ai4i_csv_sha256": original_hash,
        "original_published_synthetic_source_rows": len(original_rows),
        "source_consistent_eligible_udi_rows": sum(s["eligible_original_source_rows"]
                                                   for s in stats.values()),
        "quarantined_original_disputed_udis": 27,
        "derived_predictor_columns": 8,
        "train_fitted_normalization_diagnostics_pass": True,
        "validation_and_test_shift_diagnostics_are_descriptive_not_gate_or_generalization_proof": True,
        "source_partitions": stats,
    }


def validate(sc_data: Path, sc_audit: Path, ai4i: Path, images_zip: Path,
             stage2_report: Path, stage3_dir: Path, stage4_dir: Path,
             policy_path: Path, stage5_dir: Path, stage6_dir: Path,
             output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite prior Stage 7 original-source audit: {output_dir}")
    if digest(stage2_report) != STAGE2_SHA:
        raise ValueError("Stage 2 original quality audit changed since owner sign-off")
    policy = check_policy(policy_path, stage5_dir)
    s3 = review_stage3(stage3_dir)
    s4 = review_stage4(stage4_dir)
    s5 = review_stage5(stage5_dir)
    s6 = review_stage6(ai4i, stage5_dir, stage6_dir)
    if (s3["stage3_report_sha256"] != STAGE3_SHA
            or s4["stage4_local_report_sha256"] != STAGE4_SHA
            or s5["original_stage5_report_sha256"] != STAGE5_SHA
            or s6["original_stage6_report_sha256"] != STAGE6_SHA
            or s4["all_four_stage4_lineage_csv_sha256_verified"] is not True
            or s5["all_seven_original_assignment_csv_sha256_verified"] is not True
            or s6["all_four_stage6_output_file_sha256_verified"] is not True
            or s6["all_9973_original_source_udi_memberships_and_targets_verified"] is not True
            or s6["all_27_original_disputed_udis_excluded_and_quarantined"] is not True
            or s6["individual_predictor_values_verified"] != 79784):
        raise ValueError("Stage 3–6 original-source lineage or source-value validation changed")
    original_scania = verify_scania_sources(sc_data, sc_audit)
    image_evidence = verify_image_archive(images_zip, stage3_dir, s3, s4)
    ai4i_evidence = source_feature_diagnostics(stage6_dir, ai4i)
    if (ai4i_evidence["source_consistent_eligible_udi_rows"] != 9973
            or len(ai4i_evidence["source_partitions"]) != 3
            or policy["unresolved_label_and_photo_rights_risks_accepted_as_documented_restrictions"] is not True):
        raise ValueError("AI4I supervised eligibility or original image rights restriction changed")
    report = {
        "status": "STAGE7_SOURCE_INTEGRITY_VALIDATED_AI4I_ONLY_FULL_MULTIMODAL_BLOCKED_REVIEW_REQUIRED",
        "validation_scope": "exactly three original-source provenance and eligible AI4I tabular feature lineage; no full multimodal training certification",
        "exactly_three_user_approved_original_sources": list(SOURCES),
        "validated_original_stage_report_sha256": {
            "stage2_owner_local": STAGE2_SHA,
            "stage3_owner_local": STAGE3_SHA,
            "stage4_owner_local": STAGE4_SHA,
            "stage5_owner_local": STAGE5_SHA,
            "stage6_owner_local": STAGE6_SHA,
        },
        "stage4_eligibility_policy_sha256": digest(policy_path),
        "source_original_scania_audit_sha256": digest(sc_audit),
        "source_original_stage2_audit_sha256_verified": True,
        "stage3_original_three_image_manifests_sha256_verified": True,
        "stage4_original_four_label_manifests_sha256_verified": True,
        "stage5_original_seven_assignment_manifests_sha256_verified": True,
        "stage6_original_four_output_file_sha256_verified": True,
        "stage6_original_79784_predictor_values_verified_against_source": True,
        "scania_component_x_v2": original_scania,
        "ai4i_2020_publisher_synthetic": ai4i_evidence,
        "industrial_machinery_fault_images": image_evidence,
        "stage7_eligible_ai4i_tabular_data_quality_gate": "PASS_FOR_SOURCE_CONSISTENT_INTERNAL_BENCHMARK_ONLY",
        "stage7_scania_unified_supervised_task_gate": "BLOCKED_TASK_TARGET_MISMATCH",
        "stage7_original_fault_image_supervised_gate": "BLOCKED_LABEL_TRUTH_AND_REUSE_RIGHTS",
        "full_three_source_supervised_multimodal_dataset_approved": False,
        "cross_dataset_same_machine_pairing_verified": False,
        "all_sources_real_factory_measurements": False,
        "blocked_or_unresolved_items": list(FULL_BLOCKS),
        "no_original_source_or_prior_stage_artifacts_modified": True,
        "no_new_dataset_or_generated_synthetic_observations": True,
        "no_new_train_validation_test_splits": True,
        "no_feature_fitting_or_model_training": True,
        "no_image_bytes_extracted_or_transmitted": True,
        "stage7_signed_off": False,
        "review_decision_needed": "Owner-run report review; qualified AI4I-only internal data-validation sign-off vs full three-source multimodal dataset blocked",
    }
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".stage7-original-source-qa-", dir=output_dir.parent))
    try:
        (stage / REPORT_FILE).write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        stage.rename(output_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scania-data", type=Path, required=True)
    parser.add_argument("--images-zip", type=Path, required=True)
    parser.add_argument("--scania-audit", type=Path, default=Path("data/processed/scania_audit.json"))
    parser.add_argument("--stage2-report", type=Path, default=Path("data/processed/stage2_original_data_quality.json"))
    parser.add_argument("--ai4i", type=Path, default=Path("data/raw/ai4i2020.csv"))
    parser.add_argument("--stage3-dir", type=Path, default=Path("data/processed/stage3_cleaning"))
    parser.add_argument("--stage4-dir", type=Path, default=Path("data/processed/stage4_label_verification"))
    parser.add_argument("--stage4-policy", type=Path, default=Path("docs/datasets/stage4-label-eligibility-policy.json"))
    parser.add_argument("--stage5-dir", type=Path, default=Path("data/processed/stage5_eligible_splits"))
    parser.add_argument("--stage6-dir", type=Path, default=Path("data/processed/stage6_ai4i_features"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/stage7_final_validation"))
    a = parser.parse_args()
    result = validate(
        a.scania_data, a.scania_audit, a.ai4i, a.images_zip,
        a.stage2_report, a.stage3_dir, a.stage4_dir, a.stage4_policy,
        a.stage5_dir, a.stage6_dir, a.output_dir,
    )
    print(json.dumps({
        "status": result["status"],
        "stage6_owner_verified_report_sha256":
            result["validated_original_stage_report_sha256"]["stage6_owner_local"],
        "original_scania_csvs_sha256_checked":
            result["scania_component_x_v2"]["original_source_csv_files_hashed_and_verified"],
        "original_scania_readouts_preserved":
            result["scania_component_x_v2"]["original_operational_readouts_preserved"],
        "ai4i_eligible_rows_checked":
            result["ai4i_2020_publisher_synthetic"]["source_consistent_eligible_udi_rows"],
        "ai4i_train_only_feature_values_previously_verified": 79784,
        "ai4i_original_disputed_udis_excluded": 27,
        "original_images_archive_sha256_verified":
            result["industrial_machinery_fault_images"]["original_archive_bytes_match_owner_stage3_source"],
        "original_image_supervised_use": "BLOCKED",
        "scania_unified_supervised_model_target": "BLOCKED",
        "full_three_source_supervised_multimodal_dataset_approved": False,
        "stage7_signed_off": False,
        "report": str(a.output_dir / REPORT_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
