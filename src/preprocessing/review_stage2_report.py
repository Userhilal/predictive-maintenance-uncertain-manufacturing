"""Read-only concise review of real Stage 2 original-data audit JSON.

No input CSV, ZIP, PDF or audit report is written, edited, downloaded, split,
cleaned or passed into model training. Emits selected factual fields only.

Run from repository root:
    py -3.11 src/preprocessing/review_stage2_report.py \
      --input data/processed/stage2_original_data_quality.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def summary(path: Path) -> dict:
    original = path.read_bytes()
    report = json.loads(original.decode("utf-8-sig"))
    if report.get("status") != "STAGE2_THREE_ORIGINAL_DATA_SOURCE_AUDIT_CREATED_REVIEW_REQUIRED":
        raise ValueError("Not a successful original-only Stage 2 data audit")
    if report.get("stage2_completed_or_signed_off") is not False:
        raise ValueError("Expected honest preliminary audit, not a claimed final sign-off")
    if (report.get("all_original_source_files_unchanged") is not True
            or report.get("source_labels_modified") is not False
            or report.get("splits_created_or_modified") is not False
            or report.get("records_removed_or_created") is not False
            or report.get("features_engineered") is not False
            or report.get("model_trained") is not False):
        raise ValueError("Cannot accept a Stage 2 file reporting source mutation or later-stage work")
    scans = report["scania_component_x_v2"]
    ai4i = report["ai4i_2020"]
    photos = report["industrial_machinery_fault_images"]
    if (scans["total_vehicles"] != 33641
            or scans["total_source_readouts"] != 1516819
            or ai4i["original_rows"] != 10000
            or photos["original_image_count"] != 234):
        raise ValueError("Source populations do not match actual original-file collection")
    scan_splits = {}
    for key in ("train", "validation", "test"):
        s = scans["scania_splits"][key]
        scan_splits[key] = {
            "vehicles": s["source_vehicles"],
            "readouts": s["source_readouts"],
            "missing_sensor_cells": s["original_sensor_missing_cells"],
            "missing_pct_of_sensor_cells": s["missing_pct_of_original_sensor_cells"],
            "features_with_missing_values": s["features_with_missing_source_values"],
            "highest_missing_sensor_features": s["highest_missing_source_features"][:3],
            "source_event_or_label_counts": s["source_target_counts"],
            "original_specification_missing_cells": s["original_specification_missing_cells"],
            "original_target_missing_cells": s["original_target_missing_cells"],
        }
    return {
        "status": "STAGE2_ACTUAL_REPORT_DETAILS_READ_ONLY",
        "original_report_sha256": hashlib.sha256(original).hexdigest(),
        "scania_source_splits": scan_splits,
        "scania_original_source_warnings": scans["original_audit_warnings"],
        "ai4i_original_type_counts": ai4i["original_type_counts"],
        "ai4i_original_failure_mode_counts": ai4i["original_failure_mode_positive_counts"],
        "ai4i_original_numeric_ranges": ai4i["actual_numeric_min_max"],
        "ai4i_original_udi_band_positive_counts": {
            k: v.get("1", 0)
            for k, v in ai4i["original_udi_1000_bins_binary_target_counts"].items()
        },
        "ai4i_binary_failure_vs_mode_flag_disagreements": {
            "total": ai4i["original_source_binary_vs_mode_disagreements"],
            "mode_positive_but_binary_negative": ai4i["original_mode_positive_but_binary_negative"],
            "binary_positive_without_positive_mode": ai4i["original_binary_positive_without_positive_mode"],
            "multiple_mode_flags_positive": ai4i["original_multi_mode_positive_rows"],
        },
        "images_original_class_counts": photos["folder_label_counts"],
        "images_below_300px_minimum_side": photos["original_images_below_300px_shortest_side"],
        "images_below_200px_minimum_side": photos["original_images_below_200px_shortest_side"],
        "images_extension_content_mismatches": photos["original_image_extension_content_mismatches"],
        "images_exact_duplicate_groups": photos["original_exact_duplicate_groups"],
        "images_cross_class_exact_duplicate_groups_paths": photos[
            "original_exact_duplicates_with_conflicting_folder_classes"
        ],
        "images_dhash_near_duplicate_candidates_at_threshold": photos[
            "candidate_perceptual_similar_pairs_nonidentical_exact_byte_groups"
        ],
        "kaggle_per_photo_reuse_rights_verified": photos[
            "image_licensing_per_photo_provenance_verified"
        ],
        "not_stage3_cleaning_or_stage4_relabeling": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True,
                    help="Existing local Stage 2 original-source quality JSON")
    args = ap.parse_args()
    print(json.dumps(summary(args.input), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
