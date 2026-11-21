r"""Stage 5 ONLY: source-respecting partitions for eligible SCANIA / AI4I.

Original SCANIA train/validation/test vehicle cohorts remain exactly as
published, with their DISTINCT repair/censor vs five-class target semantics.
Original AI4I 27 disputed UDIs are EXCLUDED from each supervised split;
remaining 9,973 source-consistent rows get a deterministic stratified IID
benchmark split. Original 234-image source: NO supervised image split
because photo labels and reuse rights remain unverified.

Only derived local CSV assignment metadata and JSON are written. Never
overwrite/relabel original source files, create synthetic records, fit
features, or train models. Exactly the three owner-approved originals.

Run from Windows repository root after Stage 4 policy sign-off:
    py -3.11 src/preprocessing/split_stage5_eligible_sources.py \
      --scania-data "C:\Users\hindh\Documents\2024-34-2\data" \
      --scania-audit data/processed/scania_audit.json \
      --ai4i data/raw/ai4i2020.csv \
      --stage4-dir data/processed/stage4_label_verification \
      --policy docs/datasets/stage4-label-eligibility-policy.json \
      --output-dir data/processed/stage5_eligible_splits
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from prepare_ai4i import (
    INPUTS, MODES, SOURCE_SHA256 as AI4I_ORIGINAL_SHA, TARGET, load_and_validate,
)
from prepare_scania import validate_audit
from review_stage4_labels import review as review_stage4
from verify_stage4_labels import AI4I_QUEUE, scan_source_labels

SPLITS = ("train", "validation", "test")
SCANIA_TARGET_FILES = {
    "train": "train_tte.csv",
    "validation": "validation_labels.csv",
    "test": "test_labels.csv",
}
SCANIA_EXPECTED_SOURCE_ROWS = {"train": 23550, "validation": 5046, "test": 5045}
SCANIA_EXPECTED_READOUTS = {"train": 1122452, "validation": 196227, "test": 198140}
SOURCE_DATASETS = [
    "SCANIA Component X v2", "AI4I 2020",
    "Industrial Machinery Fault Image Dataset",
]
EXPECTED_STAGE4_SHA = "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29"
EXPECTED_STAGE3_SHA = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
EXPECTED_AI_COUNTS = {"0": 9643, "1": 330}
EXPECTED_QUARANTINE_COUNTS = {"0": 18, "1": 9}
SCANIA_FIELDS = (
    "vehicle_id", "official_original_source_split", "original_target_field",
    "original_target_value", "original_study_endpoint_time_step",
)
AI4I_FIELDS = ("UDI", "original_machine_failure", "original_product_type")
QUARANTINE_FIELDS = (
    "UDI", "original_machine_failure", "source_any_failure_mode_positive",
    "source_disagreement_type",
)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(part)
    return value.hexdigest()


def source_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames or []
        if not header or len(header) != len(set(header)):
            raise ValueError(f"Malformed original CSV header: {path}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Malformed original CSV rows: {path}")
    return header, rows


def write_csv(path: Path, fields: tuple[str, ...], records: list[dict[str, str]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(records)


def check_stage4(stage4_dir: Path, policy_file: Path) -> tuple[dict, dict]:
    policy = json.loads(policy_file.read_text(encoding="utf-8-sig"))
    evidence = policy["evidence"]
    source = policy["source_policy"]
    image = source["industrial_fault_images"]
    ai = source["ai4i"]
    sc = source["scania"]
    limits = policy["project_limits"]
    if (not policy.get("stage4_technical_source_label_verification_completed")
            or policy.get("all_three_sources_independently_truth_labeled") is not False
            or policy.get("full_three_source_supervised_training_approved") is not False
            or source["exactly_three_original_sources"] != SOURCE_DATASETS
            or evidence["owner_reviewed_stage4_report_sha256"] != EXPECTED_STAGE4_SHA
            or evidence["owner_reviewed_stage3_report_sha256"] != EXPECTED_STAGE3_SHA):
        raise ValueError("Unapproved/changed Stage 4 original-source eligibility policy")
    if (ai["source_target_mode_mismatches"] != 27
            or ai["provisionally_eligible_original_rows"] != 9973
            or ai["provisionally_eligible_original_binary_target_counts"] != EXPECTED_AI_COUNTS
            or ai["disputed_original_rows_training_status"] != "quarantined_not_in_supervised_split"
            or ai["original_records_or_labels_rewritten"] is not False
            or ai["failure_mode_columns_must_not_be_input_features_for_global_failure_prediction"] is not True
            or image["all_234_supervised_image_training_or_evaluation_eligibility"] != "BLOCKED"
            or image["source_folder_labeled_but_independently_truth_verified"] != 0
            or image["original_source_archive_members"] != 234
            or image["rights_and_provenance_evidence_required_before_permission_dependent_use"] is not True
            or image["no_source_folder_label_may_be_claimed_expert_verified"] is not True
            or sc["use_original_source_cohorts_only"] is not True
            or sc["converting_censoring_to_healthy_label_prohibited"] is not True
            or sc["inventing_common_binary_target_from_source_five_class_labels_prohibited"] is not True
            or limits["image_supervised_splits_must_remain_blocked_until_approved"] is not True
            or limits["no_cross_dataset_same_machine_join_without_source_proof"] is not True):
        raise ValueError("Stage 4 restricted source-label policy has changed")
    existing = review_stage4(stage4_dir)
    if (existing["stage4_local_report_sha256"] != EXPECTED_STAGE4_SHA
            or not existing["all_four_stage4_lineage_csv_sha256_verified"]
            or existing["ai4i_disputed_source_rows_in_review_queue"] != 27
            or existing["individual_image_labels_independently_verified"] != 0
            or existing["kaggle_image_reuse_rights_verified"] is not False
            or existing["original_files_or_source_labels_modified"] is not False):
        raise ValueError("Owner-reviewed Stage 4 evidence no longer matches approved source")
    return policy, existing


def scania_official_cohorts(
    original_data: Path, original_audit: Path
) -> tuple[dict[str, list[dict[str, str]]], dict]:
    audited = validate_audit(original_audit)
    checked = scan_source_labels(original_data, audited)
    all_ids: set[str] = set()
    cohort_rows: dict[str, list[dict[str, str]]] = {}
    summary = {}
    for split, source_name in SCANIA_TARGET_FILES.items():
        path = original_data / source_name
        if sha256(path) != audited["checksums"][source_name]["sha256"]:
            raise ValueError(f"Original SCANIA target file changed since source audit: {source_name}")
        header, raw = source_csv(path)
        source_target = "in_study_repair" if split == "train" else "class_label"
        if (set(header) != ({"vehicle_id", "length_of_study_time_step", "in_study_repair"}
                            if split == "train" else {"vehicle_id", "class_label"})
                or len(raw) != SCANIA_EXPECTED_SOURCE_ROWS[split]
                or checked[split]["source_vehicle_rows"] != len(raw)):
            raise ValueError(f"Original SCANIA label table does not match official source: {split}")
        rows = []
        for r in raw:
            vid = r["vehicle_id"]
            if not vid.strip() or vid in all_ids:
                raise ValueError(f"SCANIA original vehicle crossed official source cohorts: {vid}")
            all_ids.add(vid)
            rows.append({
                "vehicle_id": vid,
                "official_original_source_split": split,
                "original_target_field": source_target,
                "original_target_value": r[source_target],
                "original_study_endpoint_time_step": (
                    r["length_of_study_time_step"] if split == "train" else ""
                ),
            })
        rows.sort(key=lambda r: r["vehicle_id"])
        cohort_rows[split] = rows
        summary[split] = {
            "original_source_target_csv": source_name,
            "original_source_target_sha256": sha256(path),
            "official_vehicle_rows": len(rows),
            "original_label_field": source_target,
            "original_label_counts": checked[split]["source_class_or_event_counts"],
            "original_operational_readouts": SCANIA_EXPECTED_READOUTS[split],
            "official_cohort_preserved_not_newly_generated": True,
        }
    if len(all_ids) != 33641:
        raise ValueError("Not all original SCANIA source vehicles are assigned to their official cohorts")
    return cohort_rows, summary


def ai4i_review_queue(stage4_dir: Path) -> dict[str, dict[str, str]]:
    headers, records = source_csv(stage4_dir / AI4I_QUEUE)
    expected = {
        "source_udi", "source_binary_machine_failure", "source_mode_any_positive",
        "original_label_review_reason", "label_reverification_status",
        "source_TWF", "source_HDF", "source_PWF", "source_OSF", "source_RNF",
        "proposed_corrected_label",
    }
    if set(headers) != expected or len(records) != 27:
        raise ValueError("Incorrect original Stage 4 27-row UDI conflict queue")
    index = {r["source_udi"]: r for r in records}
    if len(index) != 27 or any(r["proposed_corrected_label"] for r in records):
        raise ValueError("The 27 original AI4I disagreements changed or were auto-corrected")
    if any(r["label_reverification_status"] != "unresolved_source_target_mode_disagreement" for r in records):
        raise ValueError("An original disputed target was silently treated as resolved")
    return index


def ai4i_stratified_assignment(
    source_path: Path, stage4_dir: Path, seed: int
) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]], dict]:
    source_rows, source_hash = load_and_validate(source_path)
    if source_hash != AI4I_ORIGINAL_SHA or len(source_rows) != 10000:
        raise ValueError("Actual AI4I original publisher-synthetic CSV differs from approved local source")
    queue = ai4i_review_queue(stage4_dir)
    originals = {r["UDI"]: r for r in source_rows}
    if len(originals) != len(source_rows) or set(queue) - set(originals):
        raise ValueError("Stage 4 AI4I excluded UDI lineage not found in genuine source")
    for udi, manifest in queue.items():
        row = originals[udi]
        flags = str(int(any(row[m] == "1" for m in MODES)))
        if (row[TARGET] != manifest["source_binary_machine_failure"]
                or flags != manifest["source_mode_any_positive"]
                or row[TARGET] == flags
                or any(row[m] != manifest[f"source_{m}"] for m in MODES)):
            raise ValueError(f"Disputed UDI cannot be reconciled against original AI4I source: {udi}")
    all_disputes = {
        r["UDI"] for r in source_rows
        if r[TARGET] != str(int(any(r[m] == "1" for m in MODES)))
    }
    if all_disputes != set(queue):
        raise ValueError("AI4I 27-source-row queue and actual source label contradictions diverged")
    eligible = [r for r in source_rows if r["UDI"] not in queue]
    label_counts = dict(Counter(r[TARGET] for r in eligible))
    disputed_counts = dict(Counter(originals[uid][TARGET] for uid in queue))
    if (len(eligible) != 9973 or label_counts != EXPECTED_AI_COUNTS
            or disputed_counts != EXPECTED_QUARANTINE_COUNTS):
        raise ValueError("Label eligibility count violated Stage 4 source policy")

    strata: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in eligible:
        strata[(r[TARGET], r["Type"])].append(r)
    rng = random.Random(seed)
    assigned: dict[str, list[dict[str, str]]] = {name: [] for name in SPLITS}
    for key in sorted(strata):
        group = sorted(strata[key], key=lambda r: int(r["UDI"]))
        rng.shuffle(group)
        n = len(group)
        ntrain = round(0.70 * n)
        nval = round(0.15 * n)
        if ntrain + nval > n:
            raise ValueError(f"Invalid deterministic stratified assignment size: {key}")
        for split, subset in (
            ("train", group[:ntrain]),
            ("validation", group[ntrain:ntrain + nval]),
            ("test", group[ntrain + nval:]),
        ):
            assigned[split].extend({
                "UDI": r["UDI"],
                "original_machine_failure": r[TARGET],
                "original_product_type": r["Type"],
            } for r in subset)
    for split in SPLITS:
        assigned[split].sort(key=lambda r: int(r["UDI"]))
    all_in = [r["UDI"] for group in assigned.values() for r in group]
    if (len(all_in) != 9973 or len(set(all_in)) != 9973
            or set(all_in) != {r["UDI"] for r in eligible}
            or set(all_in) & set(queue)):
        raise ValueError("AI4I original eligible assignments overlap, lose rows or include disputed UDIs")

    invalid_model_features = ["UDI", "Product ID", *MODES]
    if any(c in INPUTS for c in invalid_model_features):
        raise ValueError("Forbidden source identifiers or failure flags appear as model input features")
    summary = {}
    for split in SPLITS:
        group = assigned[split]
        labels = dict(sorted(Counter(r["original_machine_failure"] for r in group).items()))
        if not all(labels.get(k, 0) > 0 for k in ("0", "1")):
            raise ValueError(f"AI4I {split} lacks a source binary failure class")
        udi_1000_band_positive = Counter()
        type_counts = Counter()
        for r in group:
            type_counts[r["original_product_type"]] += 1
            if r["original_machine_failure"] == "1":
                i = (int(r["UDI"]) - 1) // 1000
                udi_1000_band_positive[f"{i*1000+1}-{(i+1)*1000}"] += 1
        summary[split] = {
            "source_eligible_rows_assigned": len(group),
            "original_binary_target_counts": labels,
            "original_product_type_counts": dict(sorted(type_counts.items())),
            "original_udi_1000_band_failure_positives_audit_only": dict(sorted(udi_1000_band_positive.items())),
        }
    quarantine_rows = [{
        "UDI": udi,
        "original_machine_failure": originals[udi][TARGET],
        "source_any_failure_mode_positive": queue[udi]["source_mode_any_positive"],
        "source_disagreement_type": queue[udi]["original_label_review_reason"],
    } for udi in sorted(queue, key=int)]
    return assigned, quarantine_rows, {
        "original_csv_sha256": source_hash,
        "source_original_rows": len(source_rows),
        "eligible_source_consistent_rows": len(eligible),
        "eligible_original_binary_label_counts": dict(sorted(label_counts.items())),
        "disputed_original_rows_excluded_from_all_supervised_partitions": len(queue),
        "disputed_original_binary_label_counts": dict(sorted(disputed_counts.items())),
        "seed": seed,
        "stratification": "original Machine failure 0/1 and original Type L/M/H; deterministic seeded shuffle",
        "split_proportions": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "split_counts": summary,
        "split_type": "IID-like within-original synthetic benchmark, NOT vehicle/machine longitudinal generalization or future-time testing",
        "source_udi_1000_bands_are_diagnostics_not_prediction_features": True,
        "no_source_disputed_udis_in_supervised_partitions": True,
        "no_original_labels_rewritten": True,
        "forbidden_model_features": invalid_model_features,
        "allowed_original_input_features_without_fitting": list(INPUTS),
    }


def make_stage5(
    scania_data: Path, scania_audit: Path, ai4i_path: Path,
    stage4_dir: Path, policy_path: Path, output_dir: Path, seed: int
) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing Stage 5 source assignment evidence: {output_dir}")
    policy, stage4_evidence = check_stage4(stage4_dir, policy_path)
    scania, scania_summary = scania_official_cohorts(scania_data, scania_audit)
    ai_splits, ai_quarantine, ai_summary = ai4i_stratified_assignment(ai4i_path, stage4_dir, seed)
    if sum(len(v) for v in ai_splits.values()) != 9973:
        raise ValueError("Missing original AI4I source rows in supervised partitions")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".stage5-source-splits-", dir=output_dir.parent))
    try:
        for split in SPLITS:
            write_csv(staging / f"scania_official_{split}_vehicle_targets.csv", SCANIA_FIELDS, scania[split])
            write_csv(staging / f"ai4i_{split}_eligible_udi_assignments.csv", AI4I_FIELDS, ai_splits[split])
        write_csv(staging / "ai4i_quarantined_27_source_udis.csv", QUARANTINE_FIELDS, ai_quarantine)
        report = {
            "status": "STAGE5_SOURCE_RESPECTING_TABULAR_SPLIT_MANIFESTS_CREATED_REVIEW_REQUIRED",
            "only_three_approved_source_datasets": SOURCE_DATASETS,
            "stage4_label_eligibility_policy_sha256": sha256(policy_path),
            "owner_reviewed_stage4_report_sha256": stage4_evidence["stage4_local_report_sha256"],
            "stage3_report_sha256": policy["evidence"]["owner_reviewed_stage3_report_sha256"],
            "scania_original_official_cohorts": scania_summary,
            "scania_official_partitioning_preserved": True,
            "scania_no_mixed_train_repair_censor_and_val_test_five_class_target": True,
            "scania_source_readout_totals_not_resplit": sum(SCANIA_EXPECTED_READOUTS.values()),
            "ai4i_2020": ai_summary,
            "industrial_fault_images": {
                "original_zip_member_references": 234,
                "source_folder_label_only_provisional_refs": 219,
                "source_rights_and_independent_label_verification_status": "UNVERIFIED_AND_BLOCKED",
                "supervised_image_partitions_created": False,
                "image_bytes_read_or_changed": False,
                "image_labels_reclassified": False,
                "image_reuse_rights_claimed": False,
                "pending_annotation_rights_issue": 43,
            },
            "no_original_source_files_modified": True,
            "no_original_source_labels_modified": True,
            "no_extra_datasets_or_manuals_collected": True,
            "no_cross_source_same_machine_join": True,
            "no_synthetic_rows_created": True,
            "no_feature_engineering_or_fitting": True,
            "no_model_training": True,
            "stage5_signed_off": False,
            "next_checks": [
                "Owner executes and shares this actual original-source Stage 5 report",
                "Verify all seven derived assignment manifests by hash and row membership",
                "Check each official SCANIA vehicle belongs to its pre-existing original cohort and targets preserve distinct meanings",
                "Confirm none of the 27 exact original AI4I disputed UDIs appears in any supervised assignment",
                "Check deterministic AI4I class-and-Type stratification, no overlapping original UDI membership and UDI-band concentration caveat",
                "All 234 image references remain BLOCKED from approved supervised image splitting pending annotation and reuse-rights evidence",
            ],
            "assignment_manifest_sha256": {
                p.name: sha256(p) for p in sorted(staging.glob("*.csv"))
            },
        }
        (staging / "stage5_split_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        staging.rename(output_dir)
        return report
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scania-data", type=Path, required=True)
    p.add_argument("--scania-audit", type=Path, required=True)
    p.add_argument("--ai4i", type=Path, required=True)
    p.add_argument("--stage4-dir", type=Path, required=True)
    p.add_argument("--policy", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    summary = make_stage5(
        args.scania_data, args.scania_audit, args.ai4i, args.stage4_dir,
        args.policy, args.output_dir, args.seed,
    )
    print(json.dumps({
        "status": summary["status"],
        "scania_official_vehicles": {
            k: v["official_vehicle_rows"]
            for k, v in summary["scania_original_official_cohorts"].items()
        },
        "scania_source_readouts_not_resplit": summary["scania_source_readout_totals_not_resplit"],
        "ai4i_eligible_original_rows": summary["ai4i_2020"]["eligible_source_consistent_rows"],
        "ai4i_original_disputed_udis_quarantined": summary["ai4i_2020"][
            "disputed_original_rows_excluded_from_all_supervised_partitions"
        ],
        "ai4i_assigned_source_rows_by_cohort": {
            k: v["source_eligible_rows_assigned"]
            for k,v in summary["ai4i_2020"]["split_counts"].items()
        },
        "ai4i_source_binary_target_by_cohort": {
            k: v["original_binary_target_counts"]
            for k,v in summary["ai4i_2020"]["split_counts"].items()
        },
        "images_supervised_splits_created": False,
        "all_original_files_unchanged": True,
        "stage5_signed_off": False,
        "full_report": str(args.output_dir / "stage5_split_report.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
