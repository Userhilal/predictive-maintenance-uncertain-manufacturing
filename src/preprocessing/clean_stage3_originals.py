r"""Stage 3 ONLY: conservative, reproducible cleaning policy for 3 original datasets.

No original data changed or copied, no labels corrected, no train/val/test
splits, no feature engineering, no image recompression, no extra datasets.
For SCANIA preserve native missing values; for AI4I retain all original rows
and explicitly leave 27 source label disputes for Stage 4; for images create
an exact-byte-deduplicated, quarantined *manifest* referencing ZIP members,
not a folder of copied images. Source ownership/reuse rights remain open.

Run from project root, after Stage 2 detailed risk-qualified sign-off:
    py -3.11 src/preprocessing/clean_stage3_originals.py \
      --stage2 data/processed/stage2_original_data_quality.json \
      --scania-audit data/processed/scania_audit.json \
      --ai4i data/raw/ai4i2020.csv \
      --images "C:\Users\hindh\Downloads\archive.zip" \
      --review-file docs/datasets/fault-image-manual-review.csv \
      --output-dir data/processed/stage3_cleaning
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from prepare_ai4i import SOURCE_SHA256 as AI4I_SHA, TARGET, find_label_conflicts, load_and_validate
from prepare_fault_images import (
    SOURCE_SHA256 as IMAGE_SHA,
    assign_review_status,
    read_images,
    read_review_queue,
)
from prepare_scania import validate_audit

# Fingerprint of actual owner-run Stage 2 report, shared in original user terminal.
# It is NOT a publisher-issued checksum. Refuse silently revised source audits.
OWNER_STAGE2_REPORT_SHA256 = "07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67"
EXPECTED_REVIEW_PATHS = {
    "Dataset/Crack/1_.jpg",
    "Dataset/Misalignment/1_.jpg",
    "Dataset/Normal condition/11_.jpg",
    "Dataset/Wear/4_.jpg",
}
EXPECTED_ACTION_COUNTS = {
    "provisional_candidate": 219,
    "exclude_same_class_duplicate": 7,
    "quarantine_conflicting_labels": 4,
    "quarantine_manual_review": 4,
}
MANIFEST_FIELDS = (
    "original_zip_member_path", "original_folder_class", "original_image_sha256",
    "source_image_bytes", "source_width", "source_height", "source_decode_format",
    "original_filename_format_mismatch", "exact_byte_group_size", "stage3_action",
    "stage3_reason", "human_label_verified", "source_photo_reuse_rights_verified",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_stage2(path: Path, scan_audit_path: Path) -> dict:
    report_bytes = path.read_bytes()
    if sha256_bytes(report_bytes) != OWNER_STAGE2_REPORT_SHA256:
        raise ValueError("Local Stage 2 JSON differs from the actual owner-reviewed audit fingerprint")
    report = json.loads(report_bytes.decode("utf-8-sig"))
    if report.get("status") != "STAGE2_THREE_ORIGINAL_DATA_SOURCE_AUDIT_CREATED_REVIEW_REQUIRED":
        raise ValueError("Not the observed owner-run Stage 2 original-source audit")
    if (report.get("stage2_completed_or_signed_off") is not False
            or report.get("all_original_source_files_unchanged") is not True
            or report.get("records_removed_or_created") is not False
            or report.get("source_labels_modified") is not False
            or report.get("splits_created_or_modified") is not False
            or report.get("features_engineered") is not False
            or report.get("model_trained") is not False):
        raise ValueError("Stage 2 prerequisite violates original-only strict phase policy")
    if sha256_file(scan_audit_path) != report.get("prior_original_scania_audit_sha256"):
        raise ValueError("Cached SCANIA original raw audit changed since Stage 2 source review")
    return report


def read_manual_review(path: Path) -> dict[str, str]:
    # Stage 3 is not allowed to treat changes to pending image labels as approved.
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["path", "reason", "review_status"]:
            raise ValueError("Unexpected original review queue schema")
        records = list(reader)
    if (len(records) != 4
            or {r["path"] for r in records} != EXPECTED_REVIEW_PATHS
            or any(r["review_status"] != "pending" or not r["reason"].strip() for r in records)):
        raise ValueError("Original four review flags were changed; do not accept Stage 4 decisions in Stage 3")
    original_queue = read_review_queue(path)
    if set(original_queue) != EXPECTED_REVIEW_PATHS:
        raise ValueError("Manual source-review flags differ from original policy")
    return original_queue


def image_rows(archive: Path, manual_queue: dict[str, str]) -> tuple[list[dict], str]:
    rows, archive_sha = read_images(archive, IMAGE_SHA)
    if len(rows) != 234:
        raise ValueError("Expected exactly 234 original source ZIP image members")
    assign_review_status(rows, manual_queue)  # NEVER calls make_provisional_split()
    counts = dict(Counter(r["status"] for r in rows))
    if counts != EXPECTED_ACTION_COUNTS:
        raise ValueError(f"Original conservative image curation counts unexpected: {counts}")
    if any(r["split"] or r["license_verified"] for r in rows):
        raise ValueError("Stage 3 cannot create splits or certify source image reuse")
    groups = defaultdict(list)
    for r in rows:
        groups[r["sha256"]].append(r)
    cross_class = {
        r["path"] for g in groups.values()
        if len({r["class"] for r in g}) > 1
        for r in g
    }
    if (len([g for g in groups.values() if len(g) > 1]) != 9
            or len(cross_class) != 4
            or any(r["status"] != "quarantine_conflicting_labels" for r in rows if r["path"] in cross_class)):
        raise ValueError("Previously audited exact duplicate/conflicting-label groups changed")
    # Keep source member paths and untouched original labels; status is a curation
    # decision only, not proof of true diagnosis or permission to use the photo.
    return rows, archive_sha


def manifest_row(r: dict) -> dict:
    return {
        "original_zip_member_path": r["path"],
        "original_folder_class": r["class"],
        "original_image_sha256": r["sha256"],
        "source_image_bytes": r["byte_size"],
        "source_width": r["width"],
        "source_height": r["height"],
        "source_decode_format": r["image_format"],
        "original_filename_format_mismatch": str(r["extension_mismatch"]).lower(),
        "exact_byte_group_size": r["duplicate_group_size"],
        "stage3_action": r["status"],
        "stage3_reason": r["review_reason"],
        "human_label_verified": "false",
        "source_photo_reuse_rights_verified": "false",
    }


def csv_out(path: Path, rows: list[dict]) -> None:
    with path.open("x", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(manifest_row(r) for r in rows)


def clean(stage2_file: Path, scania_audit: Path, ai4i: Path, archive: Path,
          review_file: Path, output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing Stage 3 curation: {output_dir}")
    stage2 = load_stage2(stage2_file, scania_audit)
    scan = validate_audit(scania_audit)
    if (scan["overall"]["vehicles"] != 33641
            or scan["overall"]["readouts"] != 1516819
            or stage2["scania_component_x_v2"]["source_missing_sensor_cells"] != 481376):
        raise ValueError("Original SCANIA source populations/missingness do not match real Stage 2 audit")
    ai_rows, ai_hash = load_and_validate(ai4i)
    if (ai_hash != AI4I_SHA
            or ai_hash != stage2["ai4i_2020"]["original_file_sha256"]
            or len(ai_rows) != 10000
            or len(find_label_conflicts(ai_rows)) != 27):
        raise ValueError("Original AI4I rows/label-review flags differ from actual Stage 2 audit")
    ai_labels = dict(sorted(Counter(row[TARGET] for row in ai_rows).items()))
    if ai_labels != {"0": 9661, "1": 339}:
        raise ValueError("Original AI4I target class count differs from Stage 2 audit")
    manual_flags = read_manual_review(review_file)
    images, image_hash = image_rows(archive, manual_flags)
    if image_hash != stage2["industrial_machinery_fault_images"]["original_zip_sha256"]:
        raise ValueError("Original image archive bytes differ from actual Stage 2 audit")

    selected = [r for r in images if r["status"] == "provisional_candidate"]
    flagged = [r for r in images if r["status"] != "provisional_candidate"]
    if len(selected) != 219 or len(flagged) != 15:
        raise ValueError("Stage 3 original-image curation math inconsistent")
    # No split labels are assigned. Preserve every original source path in
    # the full manifest so future Stage 4 can review all exclusions precisely.
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".stage3-cleaning-", dir=output_dir.parent))
    try:
        csv_out(staging / "original_images_full_action_manifest.csv", images)
        csv_out(staging / "image_provisional_candidates_219.csv", selected)
        csv_out(staging / "image_quarantine_and_exact_duplicates_15.csv", flagged)
        report = {
            "status": "STAGE3_CONSERVATIVE_SOURCE_CLEANING_CREATED_REVIEW_REQUIRED",
            "actual_owner_reviewed_stage2_json_sha256": sha256_file(stage2_file),
            "only_original_approved_datasets": [
                "SCANIA Component X v2",
                "AI4I 2020",
                "Industrial Machinery Fault Image Dataset",
            ],
            "scania": {
                "source_original_vehicles_retained": 33641,
                "source_original_readouts_retained": 1516819,
                "source_missing_sensor_cells_retained_as_missing": 481376,
                "source_sensor_columns": 105,
                "cleaning_policy": "Preserve all original source rows; native missing values; no imputation/clipping/scale transforms; original repair/censor and class targets unchanged",
                "original_source_csv_modified": False,
            },
            "ai4i": {
                "original_rows_retained": len(ai_rows),
                "original_failure_label_counts_preserved": ai_labels,
                "original_target_mode_conflict_rows_retained_for_stage4": 27,
                "original_source_csv_sha256": ai_hash,
                "cleaning_policy": "Source passes schema/numeric/nonmissing/unique feature-vector audit; preserve all original rows and flags without correction, scaling or splitting",
                "original_source_csv_modified": False,
            },
            "industrial_fault_images": {
                "original_archive_sha256": image_hash,
                "source_image_members_retained_in_original_archive": 234,
                "provisional_image_candidate_references": len(selected),
                "same_class_exact_duplicate_references_excluded_from_candidate_view": 7,
                "conflicting_class_duplicate_source_members_quarantined": 4,
                "unresolved_original_manual_review_members_quarantined": 4,
                "image_action_counts": dict(sorted(Counter(r["status"] for r in images).items())),
                "candidate_view_is_not_license_or_label_approved": True,
                "source_image_pixels_rewritten_or_converted": False,
                "source_archive_modified": False,
                "all_image_original_folder_labels_preserved": True,
                "all_source_members_accounted_for": len(images) == len(selected) + len(flagged),
                "image_reuse_rights_verified": False,
            },
            "outputs_are_manifests_not_new_source_measurements": True,
            "source_labels_modified": False,
            "feature_engineering_performed": False,
            "train_validation_test_splits_assigned": False,
            "model_trained": False,
            "synthetic_rows_or_images_created": False,
            "original_source_files_modified": False,
            "stage3_signed_off": False,
            "blocking_followup": [
                "Review actual original Stage 3 output counts and manifest consistency",
                "Keep photo licensing/provenance unverified and usage permission gated",
                "Stage 4 alone decides ambiguous source labels and conflicts",
                "Stage 5 alone decides leakage-safe train/validation/test partitions",
                "Stage 6 alone decides learned feature transformations and train-only fitting",
            ],
            "manifest_sha256": {
                p.name: sha256_file(p)
                for p in sorted(staging.glob("*.csv"))
            },
        }
        (staging / "stage3_cleaning_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        staging.rename(output_dir)
        return report
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage2", required=True, type=Path)
    p.add_argument("--scania-audit", required=True, type=Path)
    p.add_argument("--ai4i", required=True, type=Path)
    p.add_argument("--images", required=True, type=Path)
    p.add_argument("--review-file", default=Path("docs/datasets/fault-image-manual-review.csv"), type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    a = p.parse_args()
    report = clean(a.stage2, a.scania_audit, a.ai4i, a.images, a.review_file, a.output_dir)
    print(json.dumps({
        "status": report["status"],
        "scania_original_readouts_retained": report["scania"]["source_original_readouts_retained"],
        "scania_missing_sensor_cells_left_missing": report["scania"]["source_missing_sensor_cells_retained_as_missing"],
        "ai4i_original_rows_retained": report["ai4i"]["original_rows_retained"],
        "ai4i_source_label_conflicts_left_for_stage4": report["ai4i"]["original_target_mode_conflict_rows_retained_for_stage4"],
        "images_original_archive_members": report["industrial_fault_images"]["source_image_members_retained_in_original_archive"],
        "images_provisional_candidates": report["industrial_fault_images"]["provisional_image_candidate_references"],
        "images_exact_duplicates_and_quarantined": report["industrial_fault_images"]["image_action_counts"],
        "original_files_modified": False,
        "stage3_signed_off": False,
        "local_report": str(a.output_dir / "stage3_cleaning_report.json"),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
