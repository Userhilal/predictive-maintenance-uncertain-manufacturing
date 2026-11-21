r"""Stage 4 ONLY: verify source label integrity for the exact 3 approved datasets.

Output immutable-source label-lineage / UNRESOLVED review queues. Do not
derive truth from source-folder names, fill missing labels, relabel originals,
create train/validation/test partitions, engineer features, or train a model.

From the Windows repository root:
    py -3.11 src/preprocessing/verify_stage4_labels.py \
      --scania-data "C:\Users\hindh\Documents\2024-34-2\data" \
      --scania-audit data/processed/scania_audit.json \
      --ai4i data/raw/ai4i2020.csv \
      --stage3-dir data/processed/stage3_cleaning \
      --output-dir data/processed/stage4_label_verification
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
    MODES, SOURCE_SHA256 as AI4I_SHA256, TARGET, load_and_validate,
)
from prepare_scania import validate_audit
from review_stage3_cleaning import (
    FULL as STAGE3_IMAGE_MANIFEST,
    review as verify_stage3_manifest,
)

# Exact local fingerprints supplied by the owner AFTER executing the actual
# read-only Stage 2 and Stage 3 reviews; not independently provider-signed.
REVIEWED_STAGE2_SHA256 = "07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67"
REVIEWED_STAGE3_SHA256 = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
EXPECTED_SCANS = {
    "train": {"0": 21278, "1": 2272},
    "validation": {"0": 4910, "1": 16, "2": 14, "3": 30, "4": 76},
    "test": {"0": 4903, "1": 26, "2": 15, "3": 41, "4": 60},
}
SCANIA_FILES = {
    "train": "train_tte.csv",
    "validation": "validation_labels.csv",
    "test": "test_labels.csv",
}
AI4I_MANIFEST = "ai4i_original_10000_label_lineage.csv"
AI4I_QUEUE = "ai4i_27_source_label_disagreements_for_review.csv"
IMAGES_MANIFEST = "images_original_234_label_lineage.csv"
IMAGES_QUEUE = "images_8_source_label_review_cases.csv"
IMAGE_ACTIONS = {
    "provisional_candidate": 219,
    "exclude_same_class_duplicate": 7,
    "quarantine_conflicting_labels": 4,
    "quarantine_manual_review": 4,
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        if not columns or len(columns) != len(set(columns)):
            raise ValueError(f"Invalid/duplicate source CSV field names: {path.name}")
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError(f"Broken source CSV structure: {path.name}")
    return columns, rows


def csv_write(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def scan_source_labels(folder: Path, source_audit: dict) -> dict:
    results = {}
    for split, filename in SCANIA_FILES.items():
        source_path = folder / filename
        if digest(source_path) != source_audit["checksums"][filename]["sha256"]:
            raise ValueError(f"SCANIA source target CSV SHA changed: {filename}")
        headers, rows = csv_read(source_path)
        expected_fields = ({"vehicle_id", "length_of_study_time_step", "in_study_repair"}
                           if split == "train" else {"vehicle_id", "class_label"})
        if set(headers) != expected_fields or len(rows) != source_audit["splits"][split]["vehicles"]:
            raise ValueError(f"Unexpected source label schema or population: {filename}")
        ids = [r["vehicle_id"] for r in rows]
        if len(set(ids)) != len(ids) or any(not i.strip() for i in ids):
            raise ValueError(f"Missing/repeated original source vehicle IDs: {filename}")
        column = "in_study_repair" if split == "train" else "class_label"
        valid = {"0", "1"} if split == "train" else {"0", "1", "2", "3", "4"}
        counts = dict(sorted(Counter(row[column] for row in rows).items()))
        if (any(v not in valid for v in counts)
                or counts != EXPECTED_SCANS[split]
                or counts != source_audit["splits"][split]["target_counts"]):
            raise ValueError(f"SCANIA actual source label counts/domains differ in {filename}")
        if split == "train":
            for row in rows:
                try:
                    v = float(row["length_of_study_time_step"])
                except ValueError as exc:
                    raise ValueError("Invalid original repair/censor study endpoint") from exc
                if not math.isfinite(v) or v < 0:
                    raise ValueError("Invalid original non-finite/negative repair/censor endpoint")
        results[split] = {
            "source_csv": filename,
            "source_file_sha256": digest(source_path),
            "source_vehicle_rows": len(rows),
            "source_class_or_event_counts": counts,
            "all_original_vehicle_ids_unique_and_explicit": True,
            "source_label_domain_and_population_verified": True,
            "label_semantics": (
                "First observed Component X repair during source study vs right-censored (0 does not mean healthy forever)"
                if split == "train" else
                "Five source-defined classes at last observed readout; not interchangeable with train repair/censor binary"
            ),
            "individual_ground_truth_beyond_original_source_verified": False,
        }
    return results


def ai4i_lineage(path: Path) -> tuple[dict, list[dict], list[dict]]:
    rows, source_hash = load_and_validate(path)
    if source_hash != AI4I_SHA256 or len(rows) != 10000:
        raise ValueError("Unexpected original AI4I source file bytes or number of rows")
    all_labels = []
    disputes = []
    for r in rows:
        reported = r[TARGET]
        from_modes = str(int(any(r[m] == "1" for m in MODES)))
        conflict = reported != from_modes
        category = (
            "mode_flag_positive_but_binary_target_zero"
            if from_modes == "1" and reported == "0" else
            "binary_target_one_but_no_mode_flag_positive"
            if from_modes == "0" and reported == "1" else
            "source_target_and_mode_flags_agree"
        )
        lineage = {
            "source_udi": r["UDI"],
            "source_binary_machine_failure": reported,
            "source_TWF": r["TWF"],
            "source_HDF": r["HDF"],
            "source_PWF": r["PWF"],
            "source_OSF": r["OSF"],
            "source_RNF": r["RNF"],
            "source_mode_any_positive": from_modes,
            "original_label_review_reason": category,
            "label_reverification_status": (
                "unresolved_source_target_mode_disagreement"
                if conflict else "source_flags_consistent_not_independently_truth_verified"
            ),
            "proposed_corrected_label": "",
        }
        all_labels.append(lineage)
        if conflict:
            disputes.append(lineage.copy())
    issues = Counter(r["original_label_review_reason"] for r in disputes)
    if (len(disputes) != 27
            or issues != {
                "mode_flag_positive_but_binary_target_zero": 18,
                "binary_target_one_but_no_mode_flag_positive": 9,
            }
            or Counter(r["source_binary_machine_failure"] for r in all_labels)
               != {"0": 9661, "1": 339}):
        raise ValueError("AI4I original target/flag review queue changed from actual source audit")
    return {
        "original_source_file_sha256": source_hash,
        "original_source_rows": len(all_labels),
        "source_binary_counts": {"0": 9661, "1": 339},
        "target_flag_disagreement_review_rows": len(disputes),
        "disagreement_categories": dict(sorted(issues.items())),
        "original_labels_rewritten": False,
        "source_consistency_is_not_external_label_truth_validation": True,
    }, all_labels, disputes


def image_lineage(stage3_folder: Path) -> tuple[dict, list[dict], list[dict]]:
    reviewed = verify_stage3_manifest(stage3_folder)
    if (reviewed["stage3_report_sha256"] != REVIEWED_STAGE3_SHA256
            or reviewed["stage2_evidence_sha256"] != REVIEWED_STAGE2_SHA256
            or not reviewed["all_three_image_manifests_sha256_verified"]):
        raise ValueError("Stage 3 owner-reviewed image cleaning evidence changed")
    _, originals = csv_read(stage3_folder / STAGE3_IMAGE_MANIFEST)
    if len(originals) != 234:
        raise ValueError("Missing original image source member entries")
    lineage = []
    pending = []
    for r in originals:
        action = r["stage3_action"]
        source_label = r["original_folder_class"]
        status = {
            "provisional_candidate": "source_folder_label_only_not_human_verified",
            "exclude_same_class_duplicate": "duplicate_reference_label_not_independently_checked",
            "quarantine_conflicting_labels": "unresolved_original_cross_class_duplicate_conflict",
            "quarantine_manual_review": "unresolved_source_photo_label_or_provenance",
        }.get(action)
        if status is None:
            raise ValueError("Unrecognized original Stage 3 image action")
        record = {
            "source_zip_member_path": r["original_zip_member_path"],
            "original_source_folder_label": source_label,
            "original_source_image_sha256": r["original_image_sha256"],
            "prior_cleaning_action": action,
            "source_label_verification_status": status,
            "independently_verified_correct_class": "",
            "manual_review_recommendation": (
                "keep_quarantined_do_not_assign_class" if action.startswith("quarantine")
                else "retain_original_source_label_as_unverified_only"
            ),
            "photo_rights_verified": "false",
            "image_pixels_modified": "false",
        }
        lineage.append(record)
        if action.startswith("quarantine"):
            pending.append(record.copy())
    counts = Counter(r["prior_cleaning_action"] for r in lineage)
    if (counts != IMAGE_ACTIONS or len(pending) != 8
            or any(r["photo_rights_verified"] != "false" for r in lineage)):
        raise ValueError("Original-image ambiguity or source-rights accounting invalid")
    return {
        "original_archive_source_members": 234,
        "source_folder_reference_counts": dict(sorted(Counter(
            r["original_source_folder_label"] for r in lineage).items())),
        "image_source_action_counts": dict(sorted(counts.items())),
        "quarantined_image_label_or_provenance_review_cases": len(pending),
        "source_image_label_truth_verified_count": 0,
        "source_image_reuse_rights_verified": False,
        "note": "219 source-folder labels are provisional; no manual or independent per-photo verification was performed",
    }, lineage, pending


def stage4(scania_dir: Path, audit_file: Path, ai4i_file: Path,
           stage3_dir: Path, output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite earlier Stage 4 source review evidence: {output_dir}")
    original_scan = validate_audit(audit_file)
    scan_labels = scan_source_labels(scania_dir, original_scan)
    ai_report, ai_rows, ai_pending = ai4i_lineage(ai4i_file)
    image_report, image_rows, image_pending = image_lineage(stage3_dir)
    ai_fields = tuple(ai_rows[0])
    im_fields = tuple(image_rows[0])
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".stage4-label-verification-", dir=output_dir.parent))
    try:
        csv_write(stage / AI4I_MANIFEST, ai_fields, ai_rows)
        csv_write(stage / AI4I_QUEUE, ai_fields, ai_pending)
        csv_write(stage / IMAGES_MANIFEST, im_fields, image_rows)
        csv_write(stage / IMAGES_QUEUE, im_fields, image_pending)
        result = {
            "status": "STAGE4_ORIGINAL_SOURCE_LABEL_LINEAGE_CHECKED_ADJUDICATION_OPEN",
            "only_three_approved_sources": [
                "SCANIA Component X v2", "AI4I 2020",
                "Industrial Machinery Fault Image Dataset",
            ],
            "previous_stage3_report_sha256": REVIEWED_STAGE3_SHA256,
            "previous_stage2_report_sha256": REVIEWED_STAGE2_SHA256,
            "scania": scan_labels,
            "ai4i": ai_report,
            "industrial_fault_images": image_report,
            "ai4i_label_disagreements_fully_resolved": False,
            "original_image_disputed_labels_resolved": False,
            "all_provisional_image_labels_human_verified": False,
            "source_kaggle_photo_reuse_rights_verified": False,
            "no_original_source_file_modified": True,
            "no_original_labels_modified": True,
            "no_new_synthetic_rows_or_images": True,
            "train_validation_test_splits_created": False,
            "features_engineered": False,
            "models_trained": False,
            "stage4_signed_off": False,
            "review_queues_generated": {
                "ai4i_target_mode_disagreement_rows": 27,
                "original_image_quarantined_label_or_provenance_rows": 8,
            },
            "output_manifest_sha256": {
                item.name: digest(item) for item in sorted(stage.glob("*.csv"))
            },
            "open_decisions": [
                "Check the original AI4I paper/source definition before deciding whether its 27 mode/global target disagreements are errors; no automatic relabel",
                "Cross-class identical image bytes cannot validate both folder labels; leave all 4 such source entries quarantined",
                "The four additional manual-review source images remain unresolved; source-folder labels alone are not independent ground truth",
                "219 nonquarantined image references remain source-labeled but not human-certified; do not claim full image label verification",
                "Image provenance/individual-photo reuse permissions remain unverified; restrict any use requiring permission",
                "Stage 5 splitting and Stage 6 feature engineering may not begin until Stage 4 label/usage decisions are documented and accepted",
            ],
        }
        (stage / "stage4_label_verification_report.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        stage.rename(output_dir)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scania-data", type=Path, required=True)
    parser.add_argument("--scania-audit", type=Path, required=True)
    parser.add_argument("--ai4i", type=Path, required=True)
    parser.add_argument("--stage3-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    a = parser.parse_args()
    result = stage4(a.scania_data, a.scania_audit, a.ai4i, a.stage3_dir, a.output_dir)
    print(json.dumps({
        "status": result["status"],
        "scania_source_label_rows_verified": {
            k: v["source_vehicle_rows"] for k, v in result["scania"].items()
        },
        "scania_source_label_domains_counts": {
            k: v["source_class_or_event_counts"] for k, v in result["scania"].items()
        },
        "ai4i_original_rows": result["ai4i"]["original_source_rows"],
        "ai4i_source_label_flag_disagreements_unresolved":
            result["ai4i"]["target_flag_disagreement_review_rows"],
        "images_original_source_members": result["industrial_fault_images"]["original_archive_source_members"],
        "images_label_or_provenance_quarantined":
            result["industrial_fault_images"]["quarantined_image_label_or_provenance_review_cases"],
        "images_independently_verified_labels":
            result["industrial_fault_images"]["source_image_label_truth_verified_count"],
        "source_labels_modified": False,
        "stage4_signed_off": False,
        "local_output_dir": str(a.output_dir),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
