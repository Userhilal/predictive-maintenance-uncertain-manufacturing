"""Read-only review of actual Stage 3 derived cleaning report and image manifests.

No raw data reads, no source downloads, no image edits, no labels changed,
no train/validation/test splits, no feature engineering or model training.

From the repository root:
    py -3.11 src/preprocessing/review_stage3_cleaning.py \
      --input-dir data/processed/stage3_cleaning
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_ACTIONS = {
    "provisional_candidate": 219,
    "exclude_same_class_duplicate": 7,
    "quarantine_conflicting_labels": 4,
    "quarantine_manual_review": 4,
}
EXPECTED_CLASSES = {
    "Crack": 47,
    "Misalignment": 53,
    "Normal condition": 48,
    "Surface defects": 43,
    "Wear": 43,
}
EXPECTED_CONFLICTS = {
    "Dataset/Crack/29_.jpg",
    "Dataset/Wear/29_.jpg",
    "Dataset/Surface defects/24_.jpg",
    "Dataset/Wear/21_.jpg",
}
EXPECTED_MANUAL = {
    "Dataset/Crack/1_.jpg",
    "Dataset/Misalignment/1_.jpg",
    "Dataset/Normal condition/11_.jpg",
    "Dataset/Wear/4_.jpg",
}
FULL = "original_images_full_action_manifest.csv"
SELECTED = "image_provisional_candidates_219.csv"
FLAGGED = "image_quarantine_and_exact_duplicates_15.csv"
FILES = (FULL, SELECTED, FLAGGED)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not fields:
            raise ValueError(f"Invalid or duplicate manifest columns: {path}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Malformed source member manifest: {path}")
    return rows, fields


def review(folder: Path) -> dict:
    report_file = folder / "stage3_cleaning_report.json"
    report = json.loads(report_file.read_text(encoding="utf-8-sig"))
    if (report.get("status") != "STAGE3_CONSERVATIVE_SOURCE_CLEANING_CREATED_REVIEW_REQUIRED"
            or report.get("stage3_signed_off") is not False):
        raise ValueError("Not the original preliminary Stage 3 cleaning report")
    if (report.get("original_source_files_modified") is not False
            or report.get("source_labels_modified") is not False
            or report.get("feature_engineering_performed") is not False
            or report.get("train_validation_test_splits_assigned") is not False
            or report.get("model_trained") is not False
            or report.get("synthetic_rows_or_images_created") is not False):
        raise ValueError("Stage 3 report claims forbidden operations")
    scan, ai, im = (report["scania"], report["ai4i"], report["industrial_fault_images"])
    if (scan["source_original_vehicles_retained"] != 33641
            or scan["source_original_readouts_retained"] != 1516819
            or scan["source_missing_sensor_cells_retained_as_missing"] != 481376
            or scan.get("original_source_csv_modified") is not False):
        raise ValueError("SCANIA original observations or missing cells were not conserved")
    if (ai["original_rows_retained"] != 10000
            or ai["original_failure_label_counts_preserved"] != {"0": 9661, "1": 339}
            or ai["original_target_mode_conflict_rows_retained_for_stage4"] != 27
            or ai.get("original_source_csv_modified") is not False):
        raise ValueError("AI4I original rows, failures or label flags changed")
    if (im["source_image_members_retained_in_original_archive"] != 234
            or im["provisional_image_candidate_references"] != 219
            or im["same_class_exact_duplicate_references_excluded_from_candidate_view"] != 7
            or im["conflicting_class_duplicate_source_members_quarantined"] != 4
            or im["unresolved_original_manual_review_members_quarantined"] != 4
            or im["image_reuse_rights_verified"] is not False
            or im.get("source_archive_modified") is not False
            or im.get("source_image_pixels_rewritten_or_converted") is not False):
        raise ValueError("Image source conservation, rights or action counts invalid")
    if report["only_original_approved_datasets"] != [
        "SCANIA Component X v2", "AI4I 2020", "Industrial Machinery Fault Image Dataset"
    ]:
        raise ValueError("Stage 3 scope is not exactly the 3 approved datasets")
    if not re.fullmatch(r"[a-f0-9]{64}", report["actual_owner_reviewed_stage2_json_sha256"]):
        raise ValueError("Stage 2 provenance hash malformed")
    if (report["actual_owner_reviewed_stage2_json_sha256"] !=
            "07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67"):
        raise ValueError("Stage 2 original evidence fingerprint changed")

    stored_hashes = report.get("manifest_sha256", {})
    if set(stored_hashes) != set(FILES):
        raise ValueError("Stage 3 reports unexpected or missing source manifest files")
    tables = {}
    fields = None
    for name in FILES:
        manifest = folder / name
        actual_sha = digest(manifest)
        if stored_hashes[name] != actual_sha:
            raise ValueError(f"Stage 3 manifest checksum mismatch: {name}")
        rows, headers = read_manifest(manifest)
        if fields is None:
            fields = headers
        elif headers != fields:
            raise ValueError(f"Stage 3 manifest header mismatch: {name}")
        tables[name] = rows
    full = tables[FULL]
    kept = tables[SELECTED]
    flagged = tables[FLAGGED]
    if (len(full), len(kept), len(flagged)) != (234, 219, 15):
        raise ValueError("Stage 3 manifests do not reconcile to all 234 source members")
    paths = [r["original_zip_member_path"] for r in full]
    if len(set(paths)) != 234:
        raise ValueError("Duplicated/missing original ZIP paths in full manifest")
    if (Counter(r["stage3_action"] for r in full) != EXPECTED_ACTIONS
            or im["image_action_counts"] != EXPECTED_ACTIONS):
        raise ValueError("Wrong cleaning action accounting")
    for r in full:
        path = r["original_zip_member_path"]
        parts = path.split("/")
        if (len(parts) != 3 or parts[0] != "Dataset"
                or parts[1] not in EXPECTED_CLASSES
                or parts[1] != r["original_folder_class"]):
            raise ValueError(f"Source folder class not preserved for {path}")
        if (r["human_label_verified"] != "false"
                or r["source_photo_reuse_rights_verified"] != "false"):
            raise ValueError(f"False label or source-photo rights approval for {path}")
        if not re.fullmatch(r"[0-9a-f]{64}", r["original_image_sha256"]):
            raise ValueError(f"Invalid original image digest for {path}")
    classes = dict(Counter(r["original_folder_class"] for r in full))
    if classes != EXPECTED_CLASSES:
        raise ValueError("Source folder class totals have changed")

    by_path = {r["original_zip_member_path"]: r for r in full}
    def make_path_map(rows: list[dict]) -> dict:
        return {row["original_zip_member_path"]: row for row in rows}
    if (len(make_path_map(kept)) != 219 or len(make_path_map(flagged)) != 15
            or set(make_path_map(kept)) != {p for p,r in by_path.items() if r["stage3_action"] == "provisional_candidate"}
            or set(make_path_map(flagged)) != {p for p,r in by_path.items() if r["stage3_action"] != "provisional_candidate"}):
        raise ValueError("Provisional/flagged manifest members do not form the correct partition")
    for label, rows in ((SELECTED, kept), (FLAGGED, flagged)):
        if any(r != by_path[r["original_zip_member_path"]] for r in rows):
            raise ValueError(f"Manifest row metadata does not match original full manifest: {label}")

    groups: dict[str, list[dict]] = defaultdict(list)
    for r in full:
        groups[r["original_image_sha256"]].append(r)
    duplicate_groups = [g for g in groups.values() if len(g) > 1]
    if len(duplicate_groups) != 9:
        raise ValueError("Unexpected original exact image duplicate group count")
    for g in groups.values():
        if any(int(r["exact_byte_group_size"]) != len(g) for r in g):
            raise ValueError("Incorrect exact duplicate group size metadata")
        actions = Counter(r["stage3_action"] for r in g)
        class_count = len({r["original_folder_class"] for r in g})
        if class_count > 1:
            if actions != {"quarantine_conflicting_labels": len(g)}:
                raise ValueError("Cross-class duplicate source members not all quarantined")
        elif len(g) > 1:
            if actions != {"provisional_candidate": 1, "exclude_same_class_duplicate": len(g)-1}:
                raise ValueError("Same-class duplicate source members not correctly deduplicated")
    actual_conflicts = {r["original_zip_member_path"] for r in full
                        if r["stage3_action"] == "quarantine_conflicting_labels"}
    actual_manual = {r["original_zip_member_path"] for r in full
                     if r["stage3_action"] == "quarantine_manual_review"}
    if actual_conflicts != EXPECTED_CONFLICTS or actual_manual != EXPECTED_MANUAL:
        raise ValueError("Known source ambiguity and label conflict member list changed")
    return {
        "status": "STAGE3_ACTUAL_CLEANING_MANIFESTS_REVIEWED_READ_ONLY",
        "stage3_report_sha256": digest(report_file),
        "stage2_evidence_sha256": report["actual_owner_reviewed_stage2_json_sha256"],
        "original_three_source_readouts_preserved": scan["source_original_readouts_retained"],
        "original_scania_sensor_missing_cells_preserved": scan["source_missing_sensor_cells_retained_as_missing"],
        "original_ai4i_rows_preserved": ai["original_rows_retained"],
        "original_ai4i_disputed_target_rows_retained": ai["original_target_mode_conflict_rows_retained_for_stage4"],
        "original_image_members_accounted_for": len(full),
        "image_action_counts": dict(sorted(Counter(r["stage3_action"] for r in full).items())),
        "image_original_folder_class_counts": dict(sorted(classes.items())),
        "original_exact_image_duplicate_groups": len(duplicate_groups),
        "exact_cross_class_conflicting_members_quarantined": len(actual_conflicts),
        "original_ambiguous_manual_review_members_quarantined": len(actual_manual),
        "all_three_image_manifests_sha256_verified": True,
        "original_source_files_modified": False,
        "image_label_or_license_approved": False,
        "splits_or_features_created": False,
        "stage3_final_signoff_requires_review_of_this_output": True
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(review(a.input_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
