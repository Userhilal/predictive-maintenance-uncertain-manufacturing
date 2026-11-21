"""Read-only review of owner-generated Stage 5 source split assignment manifests.

Checks the existing 7 original-source-derived CSV metadata manifests and
report, plus exact seeded AI4I split reproducibility from their combined
eligible UDI/label/Type rows. Reads NO original source data or images.
Does not modify files, generate samples, change labels, create new splits,
fit transformers, or train models.

    py -3.11 src/preprocessing/review_stage5_splits.py \
      --input-dir data/processed/stage5_eligible_splits
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

SPLITS = ("train", "validation", "test")
SCANIA_FILES = {s: f"scania_official_{s}_vehicle_targets.csv" for s in SPLITS}
AI_FILES = {s: f"ai4i_{s}_eligible_udi_assignments.csv" for s in SPLITS}
AI_QUARANTINE = "ai4i_quarantined_27_source_udis.csv"
ALL_FILES = (*SCANIA_FILES.values(), *AI_FILES.values(), AI_QUARANTINE)
SCANIA_FIELDS = ("vehicle_id", "official_original_source_split",
                 "original_target_field", "original_target_value",
                 "original_study_endpoint_time_step")
AI_FIELDS = ("UDI", "original_machine_failure", "original_product_type")
QUARANTINE_FIELDS = ("UDI", "original_machine_failure",
                     "source_any_failure_mode_positive", "source_disagreement_type")
EXPECTED_SC_ROWS = {"train": 23550, "validation": 5046, "test": 5045}
EXPECTED_SC_READS = {"train": 1122452, "validation": 196227, "test": 198140}
EXPECTED_SC_LABELS = {
    "train": {"0": 21278, "1": 2272},
    "validation": {"0": 4910, "1": 16, "2": 14, "3": 30, "4": 76},
    "test": {"0": 4903, "1": 26, "2": 15, "3": 41, "4": 60},
}
EXPECTED_AI_LENGTH = {"train": 6981, "validation": 1497, "test": 1495}
EXPECTED_AI_LABELS = {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49},
}
STAGE4_HASH = "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29"
STAGE3_HASH = "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186"
ORIGINAL_SOURCES = ["SCANIA Component X v2", "AI4I 2020",
                    "Industrial Machinery Fault Image Dataset"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path, expected: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(expected):
            raise ValueError(f"Derived assignment CSV schema changed: {path}")
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"Malformed derived assignment CSV row in {path}")
    return rows


def verify_source_id(key: str, label: str) -> None:
    if not key.strip():
        raise ValueError(f"Blank original {label}")
    if label == "UDI" and (not key.isdecimal() or int(key) < 1 or int(key) > 10000):
        raise ValueError(f"Invalid original AI4I UDI: {key}")


def verify_scans(report: dict, tables: dict[str, list[dict]]) -> dict:
    sc_report = report["scania_original_official_cohorts"]
    if (set(sc_report) != set(SPLITS)
            or report["scania_official_partitioning_preserved"] is not True
            or report["scania_no_mixed_train_repair_censor_and_val_test_five_class_target"] is not True
            or report["scania_source_readout_totals_not_resplit"] != 1516819):
        raise ValueError("Original SCANIA cohorts or target semantics not preserved")
    globally_seen = set()
    results = {}
    for split in SPLITS:
        rows = tables[SCANIA_FILES[split]]
        meta = sc_report[split]
        labels = Counter()
        seen_this = set()
        target = "in_study_repair" if split == "train" else "class_label"
        valid_labels = {"0", "1"} if split == "train" else {"0", "1", "2", "3", "4"}
        for row in rows:
            vid = row["vehicle_id"]
            verify_source_id(vid, "vehicle")
            if vid in globally_seen or vid in seen_this:
                raise ValueError(f"SCANIA original vehicle overlaps or repeats: {vid}")
            globally_seen.add(vid)
            seen_this.add(vid)
            if (row["official_original_source_split"] != split
                    or row["original_target_field"] != target
                    or row["original_target_value"] not in valid_labels):
                raise ValueError(f"SCANIA source target domain or field mismatch: {vid}")
            if split == "train":
                try:
                    endpoint = Decimal(row["original_study_endpoint_time_step"])
                except InvalidOperation as exc:
                    raise ValueError(f"Invalid source study endpoint: {vid}") from exc
                if not endpoint.is_finite() or endpoint < 0:
                    raise ValueError(f"Negative/nonfinite original study endpoint: {vid}")
            elif row["original_study_endpoint_time_step"] != "":
                raise ValueError(f"SCANIA five-class cohort contains made-up repair endpoint: {vid}")
            labels[row["original_target_value"]] += 1
        if (len(rows) != EXPECTED_SC_ROWS[split]
                or dict(labels) != EXPECTED_SC_LABELS[split]
                or meta["official_vehicle_rows"] != len(rows)
                or meta["original_label_counts"] != EXPECTED_SC_LABELS[split]
                or meta["original_label_field"] != target
                or meta["original_operational_readouts"] != EXPECTED_SC_READS[split]
                or meta["official_cohort_preserved_not_newly_generated"] is not True
                or meta["original_source_target_csv"] !=
                ("train_tte.csv" if split == "train" else f"{split}_labels.csv")
                or not re.fullmatch(r"[a-f0-9]{64}", meta["original_source_target_sha256"])):
            raise ValueError(f"SCANIA original source cohort mismatch: {split}")
        results[split] = {"original_vehicles": len(rows),
                          "original_source_labels": dict(sorted(labels.items()))}
    if len(globally_seen) != 33641:
        raise ValueError("SCANIA official partitions missing source vehicles")
    return results


def verify_ai4i(report: dict, tables: dict[str, list[dict]]) -> dict:
    ai = report["ai4i_2020"]
    if (ai["source_original_rows"] != 10000
            or ai["eligible_source_consistent_rows"] != 9973
            or ai["eligible_original_binary_label_counts"] != {"0": 9643, "1": 330}
            or ai["disputed_original_rows_excluded_from_all_supervised_partitions"] != 27
            or ai["disputed_original_binary_label_counts"] != {"0": 18, "1": 9}
            or ai["no_source_disputed_udis_in_supervised_partitions"] is not True
            or ai["no_original_labels_rewritten"] is not True
            or ai["forbidden_model_features"] != [
                "UDI", "Product ID", "TWF", "HDF", "PWF", "OSF", "RNF"
            ]
            or ai["allowed_original_input_features_without_fitting"] != [
                "Type", "Air temperature [K]", "Process temperature [K]",
                "Rotational speed [rpm]", "Torque [Nm]", "Tool wear [min]"
            ]
            or not isinstance(ai["seed"], int)
            or ai["split_proportions"] != {
                "train": 0.70, "validation": 0.15, "test": 0.15
            }):
        raise ValueError("Unexpected original AI4I label eligibility or leak-safe split policy")
    seen: dict[str, str] = {}
    all_rows: list[dict[str, str]] = []
    summary = {}
    for split in SPLITS:
        rows = tables[AI_FILES[split]]
        if len(rows) != EXPECTED_AI_LENGTH[split]:
            raise ValueError(f"AI4I unexpected supervised cohort size: {split}")
        targets, types, bands = Counter(), Counter(), Counter()
        for r in rows:
            udi = r["UDI"]
            verify_source_id(udi, "UDI")
            if udi in seen:
                raise ValueError(f"AI4I UDI present in multiple partitions: {udi}")
            seen[udi] = split
            if (r["original_machine_failure"] not in {"0", "1"}
                    or r["original_product_type"] not in {"L", "M", "H"}):
                raise ValueError(f"Unexpected original AI4I target or Type: {udi}")
            targets[r["original_machine_failure"]] += 1
            types[r["original_product_type"]] += 1
            if r["original_machine_failure"] == "1":
                band = (int(udi) - 1) // 1000
                bands[f"{band*1000+1}-{(band+1)*1000}"] += 1
            all_rows.append(r)
        stored = ai["split_counts"][split]
        if (dict(targets) != EXPECTED_AI_LABELS[split]
                or stored["source_eligible_rows_assigned"] != len(rows)
                or stored["original_binary_target_counts"] != dict(sorted(targets.items()))
                or stored["original_product_type_counts"] != dict(sorted(types.items()))
                or stored["original_udi_1000_band_failure_positives_audit_only"] != dict(sorted(bands.items()))):
            raise ValueError(f"AI4I derived split labels, types or UDI audit disagree: {split}")
        summary[split] = {
            "source_rows": len(rows),
            "original_binary_target_counts": dict(sorted(targets.items())),
            "original_type_counts": dict(sorted(types.items())),
        }
    if len(seen) != 9973:
        raise ValueError("AI4I original source eligible UDI coverage incomplete")
    quarantine = tables[AI_QUARANTINE]
    if len(quarantine) != 27:
        raise ValueError("Stage 4 original AI4I source disagreement queue missing 27")
    quarantine_ids = set()
    quarantined_targets = Counter()
    reasons = Counter()
    for row in quarantine:
        udi = row["UDI"]
        verify_source_id(udi, "UDI")
        if udi in seen or udi in quarantine_ids:
            raise ValueError(f"Disputed original AI4I source UDI entered split or repeated: {udi}")
        quarantine_ids.add(udi)
        label = row["original_machine_failure"]
        flagged = row["source_any_failure_mode_positive"]
        reason = row["source_disagreement_type"]
        if (label not in {"0", "1"} or flagged not in {"0", "1"}
                or label == flagged
                or reason != (
                    "mode_flag_positive_but_binary_target_zero"
                    if label == "0" else
                    "binary_target_one_but_no_mode_flag_positive"
                )):
            raise ValueError(f"AI4I original disputed source label altered: {udi}")
        quarantined_targets[label] += 1
        reasons[reason] += 1
    if (dict(quarantined_targets) != {"0": 18, "1": 9}
            or dict(reasons) != {
                "mode_flag_positive_but_binary_target_zero": 18,
                "binary_target_one_but_no_mode_flag_positive": 9
            }
            or len(seen | quarantine_ids) != 10000):
        raise ValueError("AI4I eligible + quarantined original UDIs do not account for all 10,000 rows")

    # Reconstruct the seeded stratified shuffle solely from existing derived
    # eligible assignment records. This is a consistency/reproducibility check,
    # NOT another original-data split or a new output file.
    strata: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in all_rows:
        strata[(row["original_machine_failure"], row["original_product_type"])].append(row)
    randomizer = random.Random(ai["seed"])
    expected: dict[str, str] = {}
    for key in sorted(strata):
        cohort = sorted(strata[key], key=lambda r: int(r["UDI"]))
        randomizer.shuffle(cohort)
        cut_train = round(0.70 * len(cohort))
        cut_val = round(0.15 * len(cohort))
        for split, part in (
            ("train", cohort[:cut_train]),
            ("validation", cohort[cut_train:cut_train + cut_val]),
            ("test", cohort[cut_train + cut_val:]),
        ):
            for row in part:
                expected[row["UDI"]] = split
    if expected != seen:
        raise ValueError("AI4I Stage 5 derived UDI split differs from deterministic class+Type seed assignment")

    return {
        "original_eligible_udi_count": len(seen),
        "quarantined_udi_count": len(quarantine_ids),
        "original_eligible_class_counts": {"0": 9643, "1": 330},
        "cohorts": summary,
        "exact_stratified_seed_reconstruction_match": True,
        "original_udi_disjointness_and_total_10000_accounted": True,
        "source_udi_1000_bands_are_diagnostics_only": True,
    }


def review(directory: Path) -> dict:
    report_path = directory / "stage5_split_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if (report.get("status") !=
            "STAGE5_SOURCE_RESPECTING_TABULAR_SPLIT_MANIFESTS_CREATED_REVIEW_REQUIRED"
            or report.get("stage5_signed_off") is not False
            or report.get("only_three_approved_source_datasets") != ORIGINAL_SOURCES
            or report.get("owner_reviewed_stage4_report_sha256") != STAGE4_HASH
            or report.get("stage3_report_sha256") != STAGE3_HASH
            or not re.fullmatch(r"[a-f0-9]{64}",
                                report.get("stage4_label_eligibility_policy_sha256", ""))):
        raise ValueError("Stage 5 report changed original approved provenance or source status")
    for key in (
        "no_original_source_files_modified", "no_original_source_labels_modified",
        "no_extra_datasets_or_manuals_collected", "no_cross_source_same_machine_join",
        "no_synthetic_rows_created", "no_feature_engineering_or_fitting", "no_model_training",
    ):
        if report.get(key) is not True:
            raise ValueError(f"Stage 5 reports prohibited change: {key}")
    im = report["industrial_fault_images"]
    if (im["original_zip_member_references"] != 234
            or im["source_folder_label_only_provisional_refs"] != 219
            or im["source_rights_and_independent_label_verification_status"] != "UNVERIFIED_AND_BLOCKED"
            or im["supervised_image_partitions_created"] is not False
            or im["image_bytes_read_or_changed"] is not False
            or im["image_labels_reclassified"] is not False
            or im["image_reuse_rights_claimed"] is not False):
        raise ValueError("Original image labels and reuse rights still require blocking")
    listed = report["assignment_manifest_sha256"]
    if set(listed) != set(ALL_FILES):
        raise ValueError("Stage 5 report missing or unexpectedly listing original assignment manifests")
    tables = {}
    for path in ALL_FILES:
        actual = directory / path
        if digest(actual) != listed[path]:
            raise ValueError(f"Actual Stage 5 original assignment manifest SHA-256 mismatch: {path}")
        fields = (QUARANTINE_FIELDS if path == AI_QUARANTINE
                  else AI_FIELDS if path in AI_FILES.values()
                  else SCANIA_FIELDS)
        tables[path] = read_rows(actual, fields)
    scans = verify_scans(report, tables)
    ai4i = verify_ai4i(report, tables)
    return {
        "status": "STAGE5_ACTUAL_SOURCE_SPLIT_MANIFESTS_REVIEWED_READ_ONLY",
        "original_stage5_report_sha256": digest(report_path),
        "original_stage4_report_sha256": report["owner_reviewed_stage4_report_sha256"],
        "all_seven_original_assignment_csv_sha256_verified": True,
        "scania_official_partition_vehicles": {
            s: scans[s]["original_vehicles"] for s in SPLITS
        },
        "scania_original_repair_censor_and_five_class_tasks_kept_distinct": True,
        "original_scania_readouts_not_resplit": 1516819,
        "ai4i_eligible_original_udi_count": ai4i["original_eligible_udi_count"],
        "ai4i_quarantined_original_udis": ai4i["quarantined_udi_count"],
        "ai4i_original_eligible_partition_counts": {
            s: ai4i["cohorts"][s]["source_rows"] for s in SPLITS
        },
        "ai4i_original_target_counts_per_partition": {
            s: ai4i["cohorts"][s]["original_binary_target_counts"] for s in SPLITS
        },
        "ai4i_original_product_type_counts_per_partition": {
            s: ai4i["cohorts"][s]["original_type_counts"] for s in SPLITS
        },
        "ai4i_exact_seeded_class_type_assignment_reconstructed": True,
        "ai4i_all_10000_original_udi_references_accounted": True,
        "images_supervised_partitions_created": False,
        "image_original_labels_or_reuse_rights_verified": False,
        "original_source_files_or_labels_modified": False,
        "stage5_signoff_requires_review_of_this_output": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-dir", required=True, type=Path)
    args = ap.parse_args()
    print(json.dumps(review(args.input_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
