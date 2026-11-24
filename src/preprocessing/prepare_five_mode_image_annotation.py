r"""Prepare ONLY source-grounded failure-mode label index and blank image annotation queue.

There are no real shared machine/event IDs linking original AI4I rows to
the 234 images. Original photos are NOT labelled TWF/HDF/PWF/OSF/RNF.
This tool NEVER guesses their modes, claims individual photo reuse rights,
generates fake sensor/photo pairs, or creates a training set.

Reads approved Stage 3/4/5 local metadata and original AI4I source only.
Writes local CSV review artifacts without copying, decoding, or uploading images.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from prepare_ai4i import MODES, SOURCE_SHA256 as AI4I_SHA256, TARGET, load_and_validate
from review_stage3_cleaning import FULL, review as review_stage3
from review_stage4_labels import review as review_stage4
from review_stage5_splits import AI_FILES, AI_QUARANTINE, review as review_stage5

SPLITS = ("train", "validation", "test")
STAGE3_SHA = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
STAGE4_SHA = "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29"
STAGE5_SHA = "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda"
IMAGE_FIELDS = (
    "original_zip_member_path",
    "original_source_folder_label_not_a_failure_mode",
    "original_image_sha256",
    "original_stage3_action",
    "annotation_status",
    "expert_verified_failure_modes_pipe_separated",
    "expert_verified_no_failure",
    "annotation_evidence_reference",
    "annotator_identity",
    "annotation_review_date",
    "individual_photo_reuse_rights_status",
    "source_machine_event_id",
    "sensor_image_same_event_link_status",
)
AI_FIELDS = (
    "original_udi",
    "original_stage5_split",
    "original_machine_failure_label_not_a_predictor",
    "original_Type_not_a_failure_mode",
    "source_TWF_label_not_a_predictor",
    "source_HDF_label_not_a_predictor",
    "source_PWF_label_not_a_predictor",
    "source_OSF_label_not_a_predictor",
    "source_RNF_label_not_a_predictor",
    "source_positive_failure_modes_pipe_separated",
    "source_positive_failure_mode_count",
    "verified_physical_photo_event_link",
)
IMAGE_OUT = "original_234_image_five_mode_annotation_queue.csv"
AI_OUT = "original_ai4i_9973_eligible_five_mode_source_index.csv"
REPORT_OUT = "five_mode_alignment_evidence_report.json"


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_csv(path: Path, fields: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        head = reader.fieldnames or []
        if len(head) != len(set(head)) or not head:
            raise ValueError(f"Invalid source-derived header: {path}")
        if fields is not None and head != list(fields):
            raise ValueError(f"Changed original assignment schema: {path}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Malformed source-derived CSV row: {path}")
    return rows


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def build(stage3_dir: Path, stage4_dir: Path, stage5_dir: Path,
          source_ai4i: Path, out_dir: Path) -> dict:
    if out_dir.exists():
        raise FileExistsError(f"Refusing to overwrite the previous original-source annotation queue: {out_dir}")
    s3 = review_stage3(stage3_dir)
    s4 = review_stage4(stage4_dir)
    s5 = review_stage5(stage5_dir)
    if (s3["stage3_report_sha256"] != STAGE3_SHA
            or s4["stage4_local_report_sha256"] != STAGE4_SHA
            or s5["original_stage5_report_sha256"] != STAGE5_SHA
            or s3["all_three_image_manifests_sha256_verified"] is not True
            or s4["all_four_stage4_lineage_csv_sha256_verified"] is not True
            or s5["all_seven_original_assignment_csv_sha256_verified"] is not True
            or s4["individual_image_labels_independently_verified"] != 0
            or s4["kaggle_image_reuse_rights_verified"] is not False):
        raise ValueError("Original source provenance or image/AI4I label restrictions changed")

    image_raw = read_csv(stage3_dir / FULL)
    if len(image_raw) != 234:
        raise ValueError("Original 234 image member metadata incomplete")
    image_rows: list[dict[str, str]] = []
    img_actions = Counter()
    seen_paths = set()
    for r in image_raw:
        path = r["original_zip_member_path"]
        if not path or path in seen_paths:
            raise ValueError("Original image ZIP member path missing or duplicated")
        seen_paths.add(path)
        action = r["stage3_action"]
        img_actions[action] += 1
        status = {
            "provisional_candidate": "PENDING_INDEPENDENT_VISUAL_AND_CAUSAL_EVIDENCE",
            "exclude_same_class_duplicate": "EXCLUDED_EXACT_SAME_CLASS_DUPLICATE",
            "quarantine_conflicting_labels": "QUARANTINED_CROSS_CLASS_SOURCE_CONFLICT",
            "quarantine_manual_review": "QUARANTINED_SOURCE_VISUAL_OR_PROVENANCE",
        }.get(action)
        if status is None:
            raise ValueError(f"Unexpected original Stage 3 image action: {action}")
        image_rows.append({
            "original_zip_member_path": path,
            "original_source_folder_label_not_a_failure_mode": r["original_folder_class"],
            "original_image_sha256": r["original_image_sha256"],
            "original_stage3_action": action,
            "annotation_status": status,
            "expert_verified_failure_modes_pipe_separated": "",
            "expert_verified_no_failure": "",
            "annotation_evidence_reference": "",
            "annotator_identity": "",
            "annotation_review_date": "",
            "individual_photo_reuse_rights_status": "UNVERIFIED",
            "source_machine_event_id": "",
            "sensor_image_same_event_link_status": "UNVERIFIED",
        })
    if img_actions != {
        "provisional_candidate": 219,
        "exclude_same_class_duplicate": 7,
        "quarantine_conflicting_labels": 4,
        "quarantine_manual_review": 4,
    }:
        raise ValueError("Original image source quarantine partition changed")

    original_ai_rows, original_ai_sha = load_and_validate(source_ai4i)
    if len(original_ai_rows) != 10000 or original_ai_sha != AI4I_SHA256:
        raise ValueError("Only exact published original AI4I 2020 CSV is approved")
    ai_by_udi = {r["UDI"]: r for r in original_ai_rows}
    if len(ai_by_udi) != 10000:
        raise ValueError("Original AI4I source UDI population altered")
    excluded = read_csv(stage5_dir / AI_QUARANTINE)
    excluded_ids = {r["UDI"] for r in excluded}
    if len(excluded) != 27 or len(excluded_ids) != 27:
        raise ValueError("AI4I 27 unadjudicated original source mode/target contradictions not preserved")
    all_disputed = {
        r["UDI"] for r in original_ai_rows
        if r[TARGET] != str(int(any(r[m] == "1" for m in MODES)))
    }
    if excluded_ids != all_disputed:
        raise ValueError("Exact original 27 disputed failure labels not excluded")

    source_mode_rows: list[dict[str, str]] = []
    mode_positive_counts = Counter()
    seen_eligible = set()
    multiple = 0
    for split in SPLITS:
        assignments = read_csv(
            stage5_dir / AI_FILES[split],
            ("UDI", "original_machine_failure", "original_product_type"),
        )
        for item in assignments:
            udi = item["UDI"]
            if udi in seen_eligible or udi in excluded_ids:
                raise ValueError("An original source UDI was repeated or a disputed UDI included")
            seen_eligible.add(udi)
            raw = ai_by_udi.get(udi)
            if (raw is None or raw[TARGET] != item["original_machine_failure"]
                    or raw["Type"] != item["original_product_type"]):
                raise ValueError("Original AI4I source target/type membership mismatch")
            modes = [m for m in MODES if raw[m] == "1"]
            if len(modes) > 1:
                multiple += 1
            mode_positive_counts.update(modes)
            source_mode_rows.append({
                "original_udi": udi,
                "original_stage5_split": split,
                "original_machine_failure_label_not_a_predictor": raw[TARGET],
                "original_Type_not_a_failure_mode": raw["Type"],
                **{f"source_{m}_label_not_a_predictor": raw[m] for m in MODES},
                "source_positive_failure_modes_pipe_separated": "|".join(modes),
                "source_positive_failure_mode_count": str(len(modes)),
                "verified_physical_photo_event_link": "",
            })
    if (len(source_mode_rows) != 9973
            or len(seen_eligible) != 9973
            or len(seen_eligible | excluded_ids) != 10000
            or set(seen_eligible) & excluded_ids):
        raise ValueError("AI4I original source UDI coverage inconsistent with Stage 5")

    result = {
        "status": "FIVE_MODE_ANNOTATION_WORKSHEETS_CREATED_NO_PHOTO_LABELS_OR_EVENT_LINKS_VERIFIED",
        "original_source_evidence": {
            "stage3_report_sha256": STAGE3_SHA,
            "stage4_report_sha256": STAGE4_SHA,
            "stage5_report_sha256": STAGE5_SHA,
            "original_ai4i_source_sha256": original_ai_sha,
        },
        "approved_original_failure_modes": list(MODES),
        "original_image_archive_references": 234,
        "image_original_folder_labels_not_equivalent_to_five_modes": True,
        "image_annotation_status_counts": dict(sorted(Counter(
            row["annotation_status"] for row in image_rows).items()
        )),
        "photos_with_independently_verified_five_mode_labels": 0,
        "images_with_verified_source_event_link_to_ai4i_row": 0,
        "original_image_rights_verified": False,
        "original_ai4i_source_rows": 10000,
        "original_ai4i_source_consistent_eligible_udi_records": 9973,
        "original_ai4i_disputed_source_udis_excluded": 27,
        "eligible_ai4i_source_positive_mode_flag_counts": dict(sorted(mode_positive_counts.items())),
        "eligible_ai4i_source_multiple_mode_positive_rows": multiple,
        "ai4i_rows_are_not_verified_machine_specific_timestamped_trajectories": True,
        "original_scania_has_no_verified_mapping_to_five_ai4i_failure_modes": True,
        "automatic_folder_to_failure_mode_label_mapping": "PROHIBITED",
        "same_physical_machine_or_timestamp_pairing": "NOT_VERIFIED",
        "class_level_fusion": "BLOCKED_PENDING_SOURCE_GROUNDED_IMAGE_ANNOTATIONS_AND_RIGHTS",
        "no_photo_or_sensor_pairs_generated": True,
        "no_original_data_or_labels_modified": True,
        "no_models_or_new_splits_or_features_created": True,
        "next_action": "Review original photos with legitimate permissions and attach credible per-image failure-mode evidence; only then create class-aligned unpaired dataset (never claim same-machine pairs)",
    }
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".five-mode-original-review-", dir=out_dir.parent))
    try:
        write_csv(temp / IMAGE_OUT, IMAGE_FIELDS, image_rows)
        write_csv(temp / AI_OUT, AI_FIELDS, source_mode_rows)
        result["output_sha256"] = {
            IMAGE_OUT: sha256(temp / IMAGE_OUT),
            AI_OUT: sha256(temp / AI_OUT),
        }
        (temp / REPORT_OUT).write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        temp.rename(out_dir)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage3-dir", type=Path, default=Path("data/processed/stage3_cleaning"))
    ap.add_argument("--stage4-dir", type=Path, default=Path("data/processed/stage4_label_verification"))
    ap.add_argument("--stage5-dir", type=Path, default=Path("data/processed/stage5_eligible_splits"))
    ap.add_argument("--ai4i", type=Path, default=Path("data/raw/ai4i2020.csv"))
    ap.add_argument("--output-dir", type=Path, default=Path("data/processed/five_mode_image_annotation"))
    args = ap.parse_args()
    r = build(args.stage3_dir, args.stage4_dir, args.stage5_dir, args.ai4i, args.output_dir)
    print(json.dumps({
        "status": r["status"],
        "original_image_references": r["original_image_archive_references"],
        "original_image_source_folders_are_not_failure_mode_labels":
            r["image_original_folder_labels_not_equivalent_to_five_modes"],
        "independently_verified_image_failure_mode_labels":
            r["photos_with_independently_verified_five_mode_labels"],
        "original_ai4i_eligible_mode_flag_records":
            r["original_ai4i_source_consistent_eligible_udi_records"],
        "source_disputed_ai4i_udis_excluded":
            r["original_ai4i_disputed_source_udis_excluded"],
        "verified_same_machine_image_sensor_pairs":
            r["images_with_verified_source_event_link_to_ai4i_row"],
        "original_image_rights_verified": r["original_image_rights_verified"],
        "full_multimodal_training_data_ready": False,
        "local_output_dir": str(args.output_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
