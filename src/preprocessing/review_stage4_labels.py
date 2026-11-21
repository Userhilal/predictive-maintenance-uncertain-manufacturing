"""Read-only integrity review of actual locally generated Stage 4 label-lineage evidence.

Only reads the previously generated Stage 4 JSON and its four CSV manifests.
Never reads or modifies original datasets, edits labels, assigns model splits,
creates features, trains models, or certifies individual source photo rights.

From repository root on Windows:
    py -3.11 src/preprocessing/review_stage4_labels.py \
      --input-dir data/processed/stage4_label_verification
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

STAGE3_HASH = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
STAGE2_HASH = "07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67"
AI_ALL = "ai4i_original_10000_label_lineage.csv"
AI_FLAG = "ai4i_27_source_label_disagreements_for_review.csv"
IM_ALL = "images_original_234_label_lineage.csv"
IM_FLAG = "images_8_source_label_review_cases.csv"
MANIFESTS = (AI_ALL, AI_FLAG, IM_ALL, IM_FLAG)
EXPECTED_SCANS = {
    "train": {"0": 21278, "1": 2272},
    "validation": {"0": 4910, "1": 16, "2": 14, "3": 30, "4": 76},
    "test": {"0": 4903, "1": 26, "2": 15, "3": 41, "4": 60},
}
EXPECTED_IMAGE_CLASSES = {
    "Crack": 47, "Misalignment": 53, "Normal condition": 48,
    "Surface defects": 43, "Wear": 43,
}
EXPECTED_IMAGE_ACTIONS = {
    "provisional_candidate": 219,
    "exclude_same_class_duplicate": 7,
    "quarantine_conflicting_labels": 4,
    "quarantine_manual_review": 4,
}
EXPECTED_IMAGE_CONFLICTS = {
    "Dataset/Crack/29_.jpg", "Dataset/Wear/29_.jpg",
    "Dataset/Surface defects/24_.jpg", "Dataset/Wear/21_.jpg",
}
EXPECTED_IMAGE_MANUAL = {
    "Dataset/Crack/1_.jpg", "Dataset/Misalignment/1_.jpg",
    "Dataset/Normal condition/11_.jpg", "Dataset/Wear/4_.jpg",
}
AI_MODES = ("TWF", "HDF", "PWF", "OSF", "RNF")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames or []
        if not header or len(header) != len(set(header)):
            raise ValueError(f"Invalid source-derived manifest header: {path}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Malformed row in source-derived manifest: {path}")
    return header, rows


def index_original(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    index = {row[key]: row for row in rows}
    if len(index) != len(rows) or any(not k.strip() for k in index):
        raise ValueError(f"Unexpected repeated or blank original {label} identifier")
    return index


def review(folder: Path) -> dict:
    report_file = folder / "stage4_label_verification_report.json"
    report = json.loads(report_file.read_text(encoding="utf-8-sig"))
    if (report.get("status") != "STAGE4_ORIGINAL_SOURCE_LABEL_LINEAGE_CHECKED_ADJUDICATION_OPEN"
            or report.get("stage4_signed_off") is not False
            or report.get("previous_stage2_report_sha256") != STAGE2_HASH
            or report.get("previous_stage3_report_sha256") != STAGE3_HASH):
        raise ValueError("Incorrect original Stage 4 report status or evidence provenance")
    if report.get("only_three_approved_sources") != [
        "SCANIA Component X v2", "AI4I 2020", "Industrial Machinery Fault Image Dataset"
    ]:
        raise ValueError("Stage 4 attempts to use sources outside the approved three")
    for flag in ("no_original_source_file_modified", "no_original_labels_modified",
                 "no_new_synthetic_rows_or_images"):
        if report.get(flag) is not True:
            raise ValueError(f"Stage 4 evidence does not establish {flag}")
    for flag in ("train_validation_test_splits_created", "features_engineered",
                 "models_trained", "ai4i_label_disagreements_fully_resolved",
                 "original_image_disputed_labels_resolved", "all_provisional_image_labels_human_verified",
                 "source_kaggle_photo_reuse_rights_verified"):
        if report.get(flag) is not False:
            raise ValueError(f"Stage 4 incorrectly claims a later-stage or unverified action: {flag}")

    scans = report["scania"]
    if set(scans) != {"train", "validation", "test"}:
        raise ValueError("Missing official original SCANIA target splits")
    for split in ("train", "validation", "test"):
        v = scans[split]
        if (v["source_vehicle_rows"] != sum(EXPECTED_SCANS[split].values())
                or v["source_class_or_event_counts"] != EXPECTED_SCANS[split]
                or v["all_original_vehicle_ids_unique_and_explicit"] is not True
                or v["source_label_domain_and_population_verified"] is not True
                or v["individual_ground_truth_beyond_original_source_verified"] is not False
                or not re.fullmatch(r"[0-9a-f]{64}", v["source_file_sha256"])):
            raise ValueError(f"SCANIA official source label integrity not preserved: {split}")
        if (split == "train" and "right-censored" not in v["label_semantics"]
                or split != "train" and "Five source-defined classes" not in v["label_semantics"]):
            raise ValueError(f"Source train repair/censor and val/test classification meanings conflated: {split}")

    expected_hashes = report.get("output_manifest_sha256", {})
    if set(expected_hashes) != set(MANIFESTS):
        raise ValueError("Stage 4 missing/extra derived label-lineage artifacts")
    tables = {}
    for file in MANIFESTS:
        if sha256(folder / file) != expected_hashes[file]:
            raise ValueError(f"Original Stage 4 derived evidence SHA-256 changed: {file}")
        headers, rows = csv_rows(folder / file)
        tables[file] = (headers, rows)
    a_hdr, ai = tables[AI_ALL]
    b_hdr, ai_disputed = tables[AI_FLAG]
    c_hdr, images = tables[IM_ALL]
    d_hdr, im_disputed = tables[IM_FLAG]
    if a_hdr != b_hdr or c_hdr != d_hdr:
        raise ValueError("Source review queue columns differ from full label-lineage manifest")
    if (len(ai), len(ai_disputed), len(images), len(im_disputed)) != (10000, 27, 234, 8):
        raise ValueError("Stage 4 original source label record counts do not reconcile")
    all_ai = index_original(ai, "source_udi", "AI4I UDI")
    queue_ai = index_original(ai_disputed, "source_udi", "AI4I queue UDI")
    if (len(all_ai) != 10000 or len(queue_ai) != 27
            or any(r != all_ai[udi] for udi, r in queue_ai.items())):
        raise ValueError("AI4I original label/flag queue is not a source-faithful subset")
    ai_counts = Counter(row["source_binary_machine_failure"] for row in ai)
    ai_reasons = Counter()
    detected_ai = set()
    for udi, r in all_ai.items():
        if r["source_binary_machine_failure"] not in {"0", "1"}:
            raise ValueError(f"Nonbinary original AI4I failure label: {udi}")
        modes = [r[f"source_{m}"] for m in AI_MODES]
        if any(f not in {"0", "1"} for f in modes):
            raise ValueError(f"Invalid source AI4I failure-mode label: {udi}")
        union = str(int(any(f == "1" for f in modes)))
        if r["source_mode_any_positive"] != union or r["proposed_corrected_label"] != "":
            raise ValueError(f"AI4I source flags changed or correction invented: {udi}")
        mismatch = r["source_binary_machine_failure"] != union
        if mismatch:
            detected_ai.add(udi)
            expected_reason = ("mode_flag_positive_but_binary_target_zero"
                               if union == "1" else "binary_target_one_but_no_mode_flag_positive")
            ai_reasons[expected_reason] += 1
            if (r["original_label_review_reason"] != expected_reason
                    or r["label_reverification_status"] !=
                    "unresolved_source_target_mode_disagreement"):
                raise ValueError(f"AI4I original disagreement was silently resolved: {udi}")
        elif (r["original_label_review_reason"] != "source_target_and_mode_flags_agree"
              or r["label_reverification_status"] !=
              "source_flags_consistent_not_independently_truth_verified"):
            raise ValueError(f"AI4I source-consistent rows incorrectly marked independently verified: {udi}")
    if (ai_counts != {"0": 9661, "1": 339}
            or detected_ai != set(queue_ai)
            or ai_reasons != {
                "mode_flag_positive_but_binary_target_zero": 18,
                "binary_target_one_but_no_mode_flag_positive": 9,
            }
            or report["ai4i"]["target_flag_disagreement_review_rows"] != 27):
        raise ValueError("AI4I original target/mode inconsistency findings are not preserved")

    all_im = index_original(images, "source_zip_member_path", "image ZIP member")
    queue_im = index_original(im_disputed, "source_zip_member_path", "image review path")
    if any(r != all_im[path] for path, r in queue_im.items()):
        raise ValueError("Image original label review queue is not a source-faithful subset")
    action_counts = Counter(r["prior_cleaning_action"] for r in images)
    class_counts = Counter(r["original_source_folder_label"] for r in images)
    source_hash_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path, r in all_im.items():
        parts = path.split("/")
        if (len(parts) != 3 or parts[0] != "Dataset"
                or parts[1] != r["original_source_folder_label"]
                or r["photo_rights_verified"] != "false"
                or r["image_pixels_modified"] != "false"
                or r["independently_verified_correct_class"] != ""
                or not re.fullmatch(r"[0-9a-f]{64}", r["original_source_image_sha256"])):
            raise ValueError(f"Image label or rights incorrectly certified: {path}")
        action = r["prior_cleaning_action"]
        expected_status = {
            "provisional_candidate": "source_folder_label_only_not_human_verified",
            "exclude_same_class_duplicate": "duplicate_reference_label_not_independently_checked",
            "quarantine_conflicting_labels": "unresolved_original_cross_class_duplicate_conflict",
            "quarantine_manual_review": "unresolved_source_photo_label_or_provenance",
        }.get(action)
        if r["source_label_verification_status"] != expected_status:
            raise ValueError(f"Image source review classification mismatch: {path}")
        if (path in queue_im) != action.startswith("quarantine"):
            raise ValueError(f"Image review queue membership inconsistent: {path}")
        source_hash_groups[r["original_source_image_sha256"]].append(r)
    if (action_counts != EXPECTED_IMAGE_ACTIONS or class_counts != EXPECTED_IMAGE_CLASSES
            or {p for p,r in all_im.items() if r["prior_cleaning_action"] == "quarantine_conflicting_labels"}
                  != EXPECTED_IMAGE_CONFLICTS
            or {p for p,r in all_im.items() if r["prior_cleaning_action"] == "quarantine_manual_review"}
                  != EXPECTED_IMAGE_MANUAL
            or len(queue_im) != 8
            or report["industrial_fault_images"]["source_image_label_truth_verified_count"] != 0
            or report["industrial_fault_images"]["source_image_reuse_rights_verified"] is not False):
        raise ValueError("Image source-folder labels / quarantine counts / rights claims invalid")
    for group in source_hash_groups.values():
        original_classes = {r["original_source_folder_label"] for r in group}
        if len(original_classes) > 1 and any(
            r["prior_cleaning_action"] != "quarantine_conflicting_labels" for r in group
        ):
            raise ValueError("Contradictory original source-folder labels were silently accepted")
    if sum(len(g)>1 for g in source_hash_groups.values()) != 9:
        raise ValueError("Original nine exact-byte duplicate image groups not conserved")

    return {
        "status": "STAGE4_ACTUAL_SOURCE_LABEL_MANIFESTS_REVIEWED_READ_ONLY",
        "stage4_local_report_sha256": sha256(report_file),
        "stage3_owner_verified_report_sha256": STAGE3_HASH,
        "exactly_three_original_sources": True,
        "scania_original_source_target_rows": {
            k: scans[k]["source_vehicle_rows"] for k in ("train","validation","test")
        },
        "scania_repair_censor_vs_five_class_semantics_preserved": True,
        "ai4i_original_source_rows": len(ai),
        "ai4i_original_target_counts": dict(sorted(ai_counts.items())),
        "ai4i_disputed_source_rows_in_review_queue": len(ai_disputed),
        "ai4i_disagreement_categories": dict(sorted(ai_reasons.items())),
        "original_image_source_members": len(images),
        "image_original_source_folder_counts": dict(sorted(class_counts.items())),
        "image_review_queue_unresolved_entries": len(im_disputed),
        "image_original_action_counts": dict(sorted(action_counts.items())),
        "exact_image_duplicate_groups": 9,
        "individual_image_labels_independently_verified": 0,
        "kaggle_image_reuse_rights_verified": False,
        "all_four_stage4_lineage_csv_sha256_verified": True,
        "original_files_or_source_labels_modified": False,
        "label_adjudication_and_stage4_signoff_still_open": True,
        "split_or_feature_or_model_created": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir", type=Path, required=True,
                   help="Previously generated original Stage 4 derived label-lineage folder")
    a = p.parse_args()
    print(json.dumps(review(a.input_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
