"""Stage 7+ evidence-only photo-class → AI4I failure-mode proxy association.

This tool does NOT give photo verified failure-mode labels. It makes a
weak, explicitly unpaired candidate-reference index for source-folder classes
from the already-owner-generated 234 original photo annotation metadata.
It NEVER creates individual image-to-AI4I UDI/machine/time/event pairs,
does not train models, inspect/copy image pixels, or change source labels.
The original five AI4I mode flags remain LABELS, NOT predictors.

Example Windows command, repo root:
 py -3.11 src/preprocessing/build_five_mode_visual_proxies.py \
  --annotation-dir data/processed/five_mode_image_annotation \
  --policy docs/datasets/five-mode-visual-proxy-policy.json \
  --output-dir data/processed/five_mode_visual_proxy_review
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

from prepare_five_mode_image_annotation import (
    AI_FIELDS, AI_OUT, IMAGE_FIELDS, IMAGE_OUT, REPORT_OUT,
)

MODE_ORDER = ("TWF", "HDF", "PWF", "OSF", "RNF")
EXPECTED_FOLDERS = {
    "Crack": 47, "Misalignment": 53, "Normal condition": 48,
    "Surface defects": 43, "Wear": 43,
}
EXPECTED_STAGE3_ACTIONS = {
    "provisional_candidate": 219, "exclude_same_class_duplicate": 7,
    "quarantine_conflicting_labels": 4, "quarantine_manual_review": 4,
}
EVIDENCE_STAGE3_SHA = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
EVIDENCE_STAGE4_SHA = "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29"
EVIDENCE_STAGE5_SHA = "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda"
IMAGE_FIELDS_OUT = (
    "original_zip_member_path", "original_source_folder",
    "original_image_sha256", "original_stage3_action",
    "previous_source_annotation_status", "candidate_failure_mode_for_review_only",
    "association_evidence_level", "mechanism_justification_from_folder_hypothesis",
    "verified_AI4I_failure_mode_from_photo", "ground_truth_label_available",
    "photo_reuse_rights_verified", "verified_same_machine_event_time_pair",
    "approved_for_supervised_image_training", "alignment_type",
)
COVERAGE_FIELDS_OUT = (
    "failure_mode", "AI4I_original_source_positive_mode_flag_rows",
    "original_photo_weak_candidate_refs_ALL",
    "original_photo_weak_candidate_refs_STAGE3_provisional_only",
    "original_photo_verified_mode_labels",
    "verified_same_machine_event_image_sensor_pairs",
    "status",
)
IMAGE_FILE = "original_234_photo_weak_mode_candidates_NOT_GROUND_TRUTH.csv"
COVERAGE_FILE = "five_mode_unpaired_reference_coverage_NOT_TRAINING.csv"
REPORT_FILE = "visual_proxy_association_evidence_report.json"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path, expected: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(expected):
            raise ValueError(f"Original image/AI4I annotation schema unexpectedly changed: {path}")
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError(f"Malformed original source annotation record: {path}")
    return rows


def write_csv(path: Path, fields: tuple[str, ...], records: list[dict[str, str]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(records)


def build(annotation_dir: Path, policy_file: Path, out_dir: Path) -> dict:
    if out_dir.exists():
        raise FileExistsError(f"Stage 7+ source proxy view is write-once: {out_dir}")

    policy = json.loads(policy_file.read_text(encoding="utf-8-sig"))
    if (
        policy.get("policy_id") !=
        "FIVE_MODE_EXPLORATORY_VISUAL_PROXY_NOT_VERIFIED_CAUSE_2026_11_24"
        or set(policy.get("canonical_modes", {})) != set(MODE_ORDER)
        or set(policy.get("modes_without_direct_original_photo_class", []))
        != {"HDF", "PWF", "RNF"}
        or policy.get("all_photo_candidate_modes_are_unverified") is not True
        or policy.get("all_photo_rights_remain_unverified") is not True
        or policy.get("all_234_original_photo_supervised_training_or_evaluation_blocked") is not True
        or policy.get("source_folder_label_to_verified_failure_mechanism_mapping_prohibited") is not True
        or policy.get("no_same_machine_event_or_timestamp_pairs_exist_in_approved_sources") is not True
        or policy.get("class_alignment_type") != "UNPAIRED_REFERENCE_ONLY"
    ):
        raise ValueError("Weak-reference policy changed its original-source safety restrictions")
    rules = policy["original_photo_folder_rules"]
    if (len(rules) != 5
            or {r["original_folder"]: r["original_count"] for r in rules} != EXPECTED_FOLDERS
            or len({r["original_folder"] for r in rules}) != 5):
        raise ValueError("Expected exactly five original unmodified image source-folder rules")
    by_folder = {r["original_folder"]: r for r in rules}
    if any(not isinstance(r["justification"], str) or not r["justification"].strip() for r in rules):
        raise ValueError("Missing visual mapping uncertainty/physical justification")
    if (
        by_folder["Wear"]["candidate_mode"] != "TWF"
        or by_folder["Crack"]["candidate_mode"] != "OSF"
        or by_folder["Misalignment"]["candidate_mode"] != "OSF"
        or by_folder["Surface defects"]["candidate_mode"] != "OSF"
        or by_folder["Normal condition"]["candidate_mode"] is not None
        or {r["visual_proxy_strength"] for r in rules}
        != {"WEAK", "VERY_WEAK", "SOURCE_FOLDER_NORMAL_UNVERIFIED"}
    ):
        raise ValueError("Proposed weak visual proxy semantics changed unexpectedly")

    old_report_path = annotation_dir / REPORT_OUT
    old = json.loads(old_report_path.read_text(encoding="utf-8-sig"))
    evidence = old["original_source_evidence"]
    if (
        old.get("status") !=
        "FIVE_MODE_ANNOTATION_WORKSHEETS_CREATED_NO_PHOTO_LABELS_OR_EVENT_LINKS_VERIFIED"
        or evidence.get("stage3_report_sha256") != EVIDENCE_STAGE3_SHA
        or evidence.get("stage4_report_sha256") != EVIDENCE_STAGE4_SHA
        or evidence.get("stage5_report_sha256") != EVIDENCE_STAGE5_SHA
        or old.get("original_image_archive_references") != 234
        or old.get("photos_with_independently_verified_five_mode_labels") != 0
        or old.get("images_with_verified_source_event_link_to_ai4i_row") != 0
        or old.get("original_image_rights_verified") is not False
        or old.get("original_ai4i_source_consistent_eligible_udi_records") != 9973
        or old.get("original_ai4i_disputed_source_udis_excluded") != 27
        or old.get("same_physical_machine_or_timestamp_pairing") != "NOT_VERIFIED"
    ):
        raise ValueError("Original owner-run five-mode annotation source evidence has changed")

    first_image = annotation_dir / IMAGE_OUT
    first_ai = annotation_dir / AI_OUT
    saved_hashes = old.get("output_sha256", {})
    if (saved_hashes.get(IMAGE_OUT) != sha256(first_image)
            or saved_hashes.get(AI_OUT) != sha256(first_ai)):
        raise ValueError("Original two metadata-only annotation output fingerprints changed")
    images = read_csv(first_image, IMAGE_FIELDS)
    ai = read_csv(first_ai, AI_FIELDS)
    if len(images) != 234 or len(ai) != 9973:
        raise ValueError("Original source metadata record counts changed")

    img_out = []
    folder_counts = Counter()
    action_counts = Counter()
    mode_candidate_all = Counter()
    mode_candidate_provisional = Counter()
    seen_images = set()
    for image in images:
        path = image["original_zip_member_path"]
        src = image["original_source_folder_label_not_a_failure_mode"]
        action = image["original_stage3_action"]
        if (path in seen_images or not path.startswith("Dataset/" + src + "/")
                or src not in by_folder
                or action not in EXPECTED_STAGE3_ACTIONS):
            raise ValueError("Original source image identity/folder/status is incompatible with review")
        seen_images.add(path)
        if (
            image["expert_verified_failure_modes_pipe_separated"] != ""
            or image["expert_verified_no_failure"] != ""
            or image["individual_photo_reuse_rights_status"] != "UNVERIFIED"
            or image["source_machine_event_id"] != ""
            or image["sensor_image_same_event_link_status"] != "UNVERIFIED"
        ):
            raise ValueError("Unexpected approved photo label, rights, or event evidence in original queue")
        folder_counts[src] += 1
        action_counts[action] += 1
        rule = by_folder[src]
        mode = rule["candidate_mode"] or ""
        if mode:
            mode_candidate_all[mode] += 1
            if action == "provisional_candidate":
                mode_candidate_provisional[mode] += 1
        img_out.append({
            "original_zip_member_path": path,
            "original_source_folder": src,
            "original_image_sha256": image["original_image_sha256"],
            "original_stage3_action": action,
            "previous_source_annotation_status": image["annotation_status"],
            "candidate_failure_mode_for_review_only": mode,
            "association_evidence_level": rule["visual_proxy_strength"],
            "mechanism_justification_from_folder_hypothesis": rule["justification"],
            "verified_AI4I_failure_mode_from_photo": "",
            "ground_truth_label_available": "NO",
            "photo_reuse_rights_verified": "NO",
            "verified_same_machine_event_time_pair": "NO",
            "approved_for_supervised_image_training": "NO",
            "alignment_type": "UNPAIRED_REFERENCE_ONLY",
        })

    if dict(folder_counts) != EXPECTED_FOLDERS or dict(action_counts) != EXPECTED_STAGE3_ACTIONS:
        raise ValueError("Source image classes or conservative exact-duplicate exclusions changed")

    pos_modes = Counter()
    per_split = Counter()
    eligible_ids = set()
    multiple_positive = 0
    for r in ai:
        udi = r["original_udi"]
        split = r["original_stage5_split"]
        if not udi.isdecimal() or udi in eligible_ids or split not in ("train","validation","test"):
            raise ValueError("Source original AI4I UDI or stage5 split metadata invalid")
        eligible_ids.add(udi)
        per_split[split] += 1
        if r["verified_physical_photo_event_link"] != "":
            raise ValueError("Unexpected verified physical photo-event link")
        positives = []
        for mode in MODE_ORDER:
            flag = r["source_" + mode + "_label_not_a_predictor"]
            if flag not in ("0", "1"):
                raise ValueError("Original source mode targets must be binary")
            if flag == "1":
                pos_modes[mode] += 1
                positives.append(mode)
        if (r["source_positive_failure_modes_pipe_separated"] != "|".join(positives)
                or r["source_positive_failure_mode_count"] != str(len(positives))
                or r["original_machine_failure_label_not_a_predictor"] not in ("0", "1")):
            raise ValueError("Original AI4I source mode targets differ from prior review")
        if len(positives) > 1:
            multiple_positive += 1
    if dict(per_split) != {"train":6981,"validation":1497,"test":1495}:
        raise ValueError("AI4I original eligible 9,973 target-index cohort sizes changed")
    if multiple_positive != old["eligible_ai4i_source_multiple_mode_positive_rows"]:
        raise ValueError("Original AI4I multi-mode source rows differ from initial label index")
    if dict(sorted(pos_modes.items())) != old["eligible_ai4i_source_positive_mode_flag_counts"]:
        raise ValueError("Original AI4I positive mode frequencies differ from initial label index")

    coverage = []
    for m in MODE_ORDER:
        count = mode_candidate_all[m]
        coverage.append({
            "failure_mode": m,
            "AI4I_original_source_positive_mode_flag_rows": str(pos_modes[m]),
            "original_photo_weak_candidate_refs_ALL": str(count),
            "original_photo_weak_candidate_refs_STAGE3_provisional_only":
                str(mode_candidate_provisional[m]),
            "original_photo_verified_mode_labels": "0",
            "verified_same_machine_event_image_sensor_pairs": "0",
            "status": "UNPAIRED_PROXY_NOT_GROUND_TRUTH" if count else "NO_SOURCE_IMAGE_CLASS_PROXY",
        })

    report = {
        "status": "FIVE_MODE_WEAK_VISUAL_PROXY_REFERENCE_CREATED_NOT_VERIFIED_PAIRING_OR_TRAINING",
        "prior_five_mode_annotation_report_sha256": sha256(old_report_path),
        "original_image_annotation_csv_sha256_verified": True,
        "original_ai4i_source_mode_index_csv_sha256_verified": True,
        "proxy_policy_file_sha256": sha256(policy_file),
        "original_image_references_preserved": len(images),
        "original_image_stage3_source_actions": dict(sorted(action_counts.items())),
        "original_image_source_folder_counts": dict(sorted(folder_counts.items())),
        "candidate_image_refs_by_mode_not_ground_truth": dict(sorted({
            m: mode_candidate_all[m] for m in MODE_ORDER
        }.items())),
        "candidate_image_refs_stage3_provisional_only": dict(sorted({
            m: mode_candidate_provisional[m] for m in MODE_ORDER
        }.items())),
        "images_source_folder_normal_condition_not_independently_verified": folder_counts["Normal condition"],
        "original_ai4i_eligible_source_mode_index_rows": len(ai),
        "original_ai4i_positive_mode_flag_rows": dict(sorted(pos_modes.items())),
        "original_ai4i_rows_with_multiple_positive_mode_labels": multiple_positive,
        "per_original_ai4i_cohort": dict(sorted(per_split.items())),
        "source_original_image_five_mode_verified": 0,
        "source_same_machine_image_Ai4i_timeseries_pairs_verified": 0,
        "all_photo_labels_and_rights_remain_unverified": True,
        "all_image_supervised_training_and_evaluation_remain_blocked": True,
        "three_modes_have_no_direct_source_image_class": ["HDF","PWF","RNF"],
        "SCANIA_operational_variables_are_anonymized_not_verified_torque_temperature_power": True,
        "no_original_or_prior_stage_files_modified": True,
        "no_rows_synthetically_generated_or_linked": True,
        "no_features_or_model_fitted": True,
        "new_file_sha256": {},
    }
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".five-mode-proxy-review-", dir=out_dir.parent))
    try:
        write_csv(stage / IMAGE_FILE, IMAGE_FIELDS_OUT, img_out)
        write_csv(stage / COVERAGE_FILE, COVERAGE_FIELDS_OUT, coverage)
        report["new_file_sha256"] = {
            file.name: sha256(file) for file in sorted(stage.iterdir()) if file.is_file()
        }
        (stage / REPORT_FILE).write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        stage.rename(out_dir)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--annotation-dir", type=Path,
                   default=Path("data/processed/five_mode_image_annotation"))
    p.add_argument("--policy", type=Path,
                   default=Path("docs/datasets/five-mode-visual-proxy-policy.json"))
    p.add_argument("--output-dir", type=Path,
                   default=Path("data/processed/five_mode_visual_proxy_review"))
    a = p.parse_args()
    data = build(a.annotation_dir, a.policy, a.output_dir)
    print(json.dumps({
        "status": data["status"],
        "original_images_preserved": data["original_image_references_preserved"],
        "original_ai4i_mode_flag_records": data["original_ai4i_eligible_source_mode_index_rows"],
        "photo_candidate_counts_UNVERIFIED": data["candidate_image_refs_by_mode_not_ground_truth"],
        "source_folder_normal_not_verified": data["images_source_folder_normal_condition_not_independently_verified"],
        "verified_photo_failure_mode_labels": 0,
        "verified_image_same_machine_sensor_pairs": 0,
        "full_supervised_multimodal_training_ready": False,
        "source_or_previous_outputs_modified": False,
        "report": str(a.output_dir / REPORT_FILE),
    }, indent=2))


if __name__ == "__main__":
    main()
