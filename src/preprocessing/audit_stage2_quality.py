r"""Stage 2 ONLY: audit exactly three already-collected original data sources.

Reads previously passed original SCANIA audit + Stage 1 inventory, original
AI4I CSV and original Kaggle ZIP. Creates descriptive quality evidence ONLY:
no new observations, cleaning, relabeling, provisional splits, feature
engineering, model training, synthetic test fixtures or extra document sources.

Requires Pillow to audit the original source images:
    py -3.11 -m pip install Pillow

From the repository root:
    py -3.11 src/preprocessing/audit_stage2_quality.py \
      --stage1 data/processed/stage1_collection_inventory_verified.json \
      --scania-audit data/processed/scania_audit.json \
      --ai4i data/raw/ai4i2020.csv \
      --images "C:\Users\hindh\Downloads\archive.zip" \
      --output data/processed/stage2_original_data_quality.json
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from zipfile import ZipFile

from prepare_ai4i import (
    COLUMNS, INPUTS, MODES, SOURCE_SHA256 as AI4I_SHA,
    TARGET, find_label_conflicts, load_and_validate,
)
from prepare_fault_images import (
    CLASSES, SOURCE_SHA256 as IMAGE_SHA, read_images,
)
from prepare_scania import EXPECTED_FILES as SCANIA_FILES, validate_audit

SCANIA_URL = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
AI4I_URL = "https://data.mendeley.com/datasets/5ww3zv87y7/1"
IMAGE_URL = "https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data"
EXPECTED_VEHICLES = {"train": 23550, "validation": 5046, "test": 5045}
EXPECTED_READOUTS = {"train": 1122452, "validation": 196227, "test": 198140}
NEAR_HASH_DISTANCE = 5
REPORTED_NEAR_PAIRS_LIMIT = 150


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda: f.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def from_json(path: Path) -> dict:
    v = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(v, dict):
        raise ValueError(f"Expected original JSON audit object: {path}")
    return v


def check_stage1_originals(stage1: dict, scan: dict, ai4i_hash: str, image_hash: str) -> None:
    if (stage1.get("status") != "THREE_ORIGINAL_DATASETS_AND_SCANIA_DOCUMENTS_LOCALLY_VERIFIED"
        or stage1.get("stage1_collection_signoff") != "FILE_ACQUISITION_CHECKS_PASSED_RIGHTS_REVIEW_OPEN"):
        raise ValueError("Need the user's successful original-only three-source Stage 1 inventory")
    datasets = stage1.get("acquisition", {})
    if (datasets.get("all_three_data_sources_original_files_present_and_matching_local_reference") is not True
            or datasets.get("both_original_scania_documentation_pdfs_present") is not True):
        raise ValueError("Stage 1 source acquisition did not pass for original three datasets")
    scania = stage1.get("scania", {})
    if (scania.get("source") != SCANIA_URL
            or scania.get("original_csv_count_verified") != 9):
        raise ValueError("Incorrect source/version or incomplete original SCANIA acquisition")
    src_csvs = scania.get("original_csv_files", {})
    if set(src_csvs) != set(SCANIA_FILES):
        raise ValueError("Missing original SCANIA CSV in verified Stage 1 inventory")
    for file in SCANIA_FILES:
        x = src_csvs[file]
        if (x.get("status") != "PRESENT"
                or x.get("hash_matches_previous_owner_audit") is not True
                or x.get("sha256") != scan["checksums"][file]["sha256"]):
            raise ValueError(f"Stage 1 original SCANIA file does not match its raw audit: {file}")
    docs = scania.get("source_documentation", {})
    if (set(docs) != {"2024_IDA_challenge_v2.pdf", "Scania_component_X_PdM.pdf"}
            or any(v.get("status") != "PRESENT" for v in docs.values())):
        raise ValueError("Original SCANIA provider PDF documentation missing")
    ai = stage1.get("ai4i", {})
    if (ai.get("source") != AI4I_URL
            or ai.get("original_archive_extracted_csv", {}).get("status") != "PRESENT"
            or ai["original_archive_extracted_csv"].get("sha256") != ai4i_hash
            or ai4i_hash != AI4I_SHA):
        raise ValueError("AI4I CSV bytes do not match approved original source")
    im = stage1.get("industrial_fault_images", {})
    if (im.get("source") != IMAGE_URL
            or im.get("original_archive", {}).get("status") != "PRESENT"
            or im["original_archive"].get("sha256") != image_hash
            or image_hash != IMAGE_SHA):
        raise ValueError("Original Kaggle image ZIP differs from approved owner-source archive")


def scania_quality(audit: dict) -> dict:
    validated = audit["splits"]
    out = {}
    missing_total = 0
    warnings = audit.get("warnings", [])
    for split in ("train", "validation", "test"):
        record = validated[split]
        missing_by_feature = record.get("feature_missing_counts", {})
        if not isinstance(missing_by_feature, dict):
            raise ValueError(f"Expected per-feature source missing counts in {split}")
        if any(type(v) is not int or v < 0 for v in missing_by_feature.values()):
            raise ValueError(f"Invalid original SCANIA missing count in {split}")
        count = sum(missing_by_feature.values())
        if (record.get("vehicles") != EXPECTED_VEHICLES[split]
                or record.get("readouts") != EXPECTED_READOUTS[split]
                or record.get("operational_columns") != 107
                or record.get("non_numeric_values") != 0
                or record.get("backwards_order_vehicle_count") != 0
                or record.get("repeated_adjacent_time_steps") != 0):
            raise ValueError(f"SCANIA original source audit failed integrity checks for {split}")
        if count > 105 * record["readouts"]:
            raise ValueError(f"Impossible original missing sensor count in {split}")
        missing_total += count
        ordered = sorted(missing_by_feature.items(), key=lambda x: (-x[1], x[0]))
        out[split] = {
            "source_vehicles": record["vehicles"],
            "source_readouts": record["readouts"],
            "source_sensor_columns": 105,
            "original_sensor_missing_cells": count,
            "missing_pct_of_original_sensor_cells": round(100 * count / (105 * record["readouts"]), 6),
            "features_with_missing_source_values": sum(v > 0 for v in missing_by_feature.values()),
            "highest_missing_source_features": [
                {"source_feature": k, "original_missing": v,
                 "missing_pct_of_source_readouts": round(100*v / record["readouts"], 6)}
                for k, v in ordered[:10]
            ],
            "invalid_original_numeric_sensor_values": 0,
            "backward_order_vehicle_count": 0,
            "repeated_adjacent_source_times": 0,
            "source_target_counts": record.get("target_counts", {}),
            "original_specification_missing_cells": record.get("specification_missing_cells", {}),
            "original_target_missing_cells": record.get("target_missing_cells", {}),
        }
    # Previous owner-run original index reported this aggregate; cross-check all splits.
    if missing_total != 481376:
        raise ValueError("Source readout missing cells do not reconcile with verified owner-run index")
    return {
        "source": SCANIA_URL,
        "original_audit_status": audit["status"],
        "total_vehicles": audit["overall"]["vehicles"],
        "total_source_readouts": audit["overall"]["readouts"],
        "source_missing_sensor_cells": missing_total,
        "scania_splits": out,
        "disjoint_original_vehicle_sets": audit["overall"]["disjoint_vehicle_splits"],
        "vehicle_to_target_source_linkage": audit["overall"]["vehicle_target_linkage_verified"],
        "original_audit_warnings": warnings,
        "publisher_sha256_independently_verified": False,
        "known_limitations": [
            "Real truck component data, not manufacturing plant telemetry",
            "Anonymized sensor semantics and anonymized original time-step units",
            "Right censoring and repair events are not proof of complete physical failures",
            "Original train event/censor outcome and official 5-class validation/test targets differ",
            "Raw source audit checks file order/adjacent timestamps, not all nonadjacent timestamp collisions",
        ],
    }


def ai4i_quality(path: Path) -> tuple[dict, str]:
    rows, digest = load_and_validate(path)  # original-only checks, NO split generator
    if digest != AI4I_SHA or len(rows) != 10000:
        raise ValueError("Actual AI4I CSV differs from 10,000-row approved original")
    label = Counter(x[TARGET] for x in rows)
    modes = {m: sum(x[m] == "1" for x in rows) for m in MODES}
    issues = find_label_conflicts(rows)
    product_ids = Counter(x["Product ID"] for x in rows)
    types = Counter(x["Type"] for x in rows)
    numeric_ranges = {}
    for col in INPUTS[1:]:
        numbers = [float(x[col]) for x in rows]
        numeric_ranges[col] = {"actual_min": min(numbers), "actual_max": max(numbers)}
    id_bins: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        udi = int(row["UDI"])
        band = (udi - 1) // 1000
        id_bins[f"{band*1000 + 1}-{(band+1)*1000}"][row[TARGET]] += 1
    return {
        "source": AI4I_URL,
        "original_file_sha256": digest,
        "publisher_is_synthetic": True,
        "original_rows": len(rows),
        "original_columns": list(COLUMNS),
        "source_missing_cells": 0,
        "unique_original_udi": len({r["UDI"] for r in rows}),
        "unique_original_product_id": len(product_ids),
        "repeated_product_id_values": sum(c > 1 for c in product_ids.values()),
        "original_type_counts": dict(sorted(types.items())),
        "original_binary_target_counts": dict(sorted(label.items())),
        "original_failure_mode_positive_counts": modes,
        "original_source_binary_vs_mode_disagreements": len(issues),
        "original_mode_positive_but_binary_negative": sum(x[TARGET] == "0" for x in issues),
        "original_binary_positive_without_positive_mode": sum(x[TARGET] == "1" for x in issues),
        "original_multi_mode_positive_rows": sum(sum(x[m] == "1" for m in MODES) > 1 for x in rows),
        "actual_numeric_min_max": numeric_ranges,
        "original_udi_1000_bins_binary_target_counts": {
            k: dict(sorted(c.items())) for k, c in sorted(id_bins.items())
        },
        "source_original_labels_changed": False,
        "known_limitations": [
            "Originally publisher-synthetic, not measured industrial production",
            "Original target-vs-failure-mode disagreements are candidates for Stage 4 review, never corrected here",
            "UDI is an identifier, not evidence of a genuine individual-machine time series",
            "Observed target concentration across UDI ranges can make IID performance optimistic",
        ],
    }, digest


def difference_hash(img) -> int:
    """64-bit dHash; similarity is a review hint, not proof of image identity."""
    from PIL import ImageOps, Image
    transposed = ImageOps.exif_transpose(img)
    pixels = list(transposed.convert("L").resize((9, 8), Image.Resampling.LANCZOS).tobytes())
    result = 0
    for r in range(8):
        for c in range(8):
            result = (result << 1) | int(pixels[r * 9 + c] > pixels[r * 9 + c + 1])
    return result


def image_quality(path: Path) -> tuple[dict, str]:
    entries, digest = read_images(path, IMAGE_SHA)  # no cleanup, exclusions or split calls
    if len(entries) != 234:
        raise ValueError("Expected 234 genuine original source images")
    by_sha: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_sha[e["sha256"]].append(e)
    exact = [sorted([e["path"] for e in group]) for group in by_sha.values() if len(group) > 1]
    exact.sort()
    cross_class_exact = []
    for group in by_sha.values():
        if len({e["class"] for e in group}) > 1:
            cross_class_exact.append(sorted([e["path"] for e in group]))
    cross_class_exact.sort()

    # Perceptual candidate detection on exact original ZIP member bytes.
    # Fingerprint one representative of each exact-byte group. Every result
    # remains an UNRESOLVED visual-review candidate, never a relabel decision.
    dhashes: list[tuple[str, int, str]] = []
    from PIL import Image
    with ZipFile(path, "r") as z:
        for group in by_sha.values():
            example = group[0]
            with Image.open(io.BytesIO(z.read(example["path"]))) as im:
                im.load()
                p = difference_hash(im)
            dhashes.append((example["path"], p, example["class"]))
    near = []
    count = 0
    cross_class_near = 0
    for a, b in combinations(dhashes, 2):
        d = (a[1] ^ b[1]).bit_count()
        if d <= NEAR_HASH_DISTANCE:
            count += 1
            cross_class_near += (a[2] != b[2])
            if len(near) < REPORTED_NEAR_PAIRS_LIMIT:
                near.append({
                    "original_image_a": a[0],
                    "original_image_b": b[0],
                    "dhash_hamming_distance": d,
                    "folder_classes_differ": a[2] != b[2],
                })
    return {
        "source": IMAGE_URL,
        "original_zip_sha256": digest,
        "original_image_count": len(entries),
        "folder_label_counts": dict(sorted(Counter(x["class"] for x in entries).items())),
        "unreadable_original_images": 0,
        "original_exact_duplicate_groups": len(exact),
        "original_exact_duplicate_images_beyond_one_per_group": sum(len(g)-1 for g in exact),
        "original_exact_duplicate_groups_paths": exact,
        "original_exact_duplicates_with_conflicting_folder_classes": cross_class_exact,
        "original_images_below_300px_shortest_side": sum(x["min_side_under_300"] for x in entries),
        "original_images_below_200px_shortest_side": sum(x["min_side_under_200"] for x in entries),
        "original_image_extension_content_mismatches": [
            x["path"] for x in entries if x["extension_mismatch"]
        ],
        "heuristic_dhash_max_distance": NEAR_HASH_DISTANCE,
        "candidate_perceptual_similar_pairs_nonidentical_exact_byte_groups": count,
        "candidate_similar_pairs_cross_folder_classes": cross_class_near,
        "candidate_perceptual_similar_pairs_displayed": near,
        "candidate_pairs_output_truncated": count > len(near),
        "source_image_labels_rewritten": False,
        "source_image_files_removed": False,
        "image_licensing_per_photo_provenance_verified": False,
        "known_limitations": [
            "Exact duplicate pairs with differing folder labels are findings, not Stage 4 resolved labels",
            "dHash <= 5 is a heuristic; false positives and missed crops/near-duplicates are possible",
            "Original small images may not support reliable fine-grained defect recognition",
            "Source photo ownership, permitted use and machine-instance provenance remain unverified",
            "Different image categories/equipment lack source-proven shared IDs with SCANIA or AI4I",
        ],
    }, digest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage1", type=Path, required=True)
    p.add_argument("--scania-audit", type=Path, required=True)
    p.add_argument("--ai4i", type=Path, required=True)
    p.add_argument("--images", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite previously captured real Stage 2 evidence: {args.output}")
    stage1 = from_json(args.stage1)
    source_audit = validate_audit(args.scania_audit)
    ai_quality, ai_sha = ai4i_quality(args.ai4i)
    im_quality, im_sha = image_quality(args.images)
    check_stage1_originals(stage1, source_audit, ai_sha, im_sha)
    scan_quality = scania_quality(source_audit)
    report = {
        "status": "STAGE2_THREE_ORIGINAL_DATA_SOURCE_AUDIT_CREATED_REVIEW_REQUIRED",
        "only_three_approved_sources": [SCANIA_URL, AI4I_URL, IMAGE_URL],
        "stage1_inventory_sha256": sha256(args.stage1),
        "prior_original_scania_audit_sha256": sha256(args.scania_audit),
        "scania_component_x_v2": scan_quality,
        "ai4i_2020": ai_quality,
        "industrial_machinery_fault_images": im_quality,
        "rights_and_independent_publisher_checksums_fully_verified": False,
        "all_original_source_files_unchanged": True,
        "source_labels_modified": False,
        "missing_values_filled": False,
        "records_removed_or_created": False,
        "splits_created_or_modified": False,
        "features_engineered": False,
        "model_trained": False,
        "stage2_completed_or_signed_off": False,
        "remaining_stage2_review": [
            "Review actual per-source audit outputs and documented anomalies, without correcting data in Stage 2",
            "Mark limits of source provenance, independent publisher SHA verification, and Kaggle photo reuse permissions",
            "Review perceptual duplicate candidates as provisional; do not silently relabel or exclude images",
            "Record acceptance/risks for Stage 2, then move separately to Stage 3 Cleaning",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "scania_original_vehicles": scan_quality["total_vehicles"],
        "scania_original_readouts": scan_quality["total_source_readouts"],
        "scania_missing_sensor_cells": scan_quality["source_missing_sensor_cells"],
        "ai4i_source_rows": ai_quality["original_rows"],
        "ai4i_source_failure_label_counts": ai_quality["original_binary_target_counts"],
        "ai4i_source_label_disagreement_candidates": ai_quality["original_source_binary_vs_mode_disagreements"],
        "image_source_count": im_quality["original_image_count"],
        "image_exact_duplicate_groups": im_quality["original_exact_duplicate_groups"],
        "image_cross_class_exact_duplicate_groups": len(
            im_quality["original_exact_duplicates_with_conflicting_folder_classes"]),
        "image_perceptual_near_duplicate_review_candidates":
            im_quality["candidate_perceptual_similar_pairs_nonidentical_exact_byte_groups"],
        "kaggle_per_photo_rights_verified": False,
        "stage2_signed_off": False,
        "full_report_path": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
