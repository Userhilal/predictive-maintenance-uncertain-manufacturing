"""Stage 1 ONLY: inventory existing original approved data files, without modifying them.

This verifies acquisition, not model readiness, source-label correctness, or
permissions to reuse individually sourced Kaggle photographs. It never
downloads, replaces, invents, copies, or cleans original data.
No synthetic fixtures, additional datasets, or fake provenance.

Run from repo root on Windows:
 py -3.11 src/preprocessing/audit_stage1_collection.py \
   --scania-data "C:\Users\hindh\Documents\2024-34-2\data" \
   --scania-audit data/processed/scania_audit.json \
   --ai4i data/raw/ai4i2020.csv \
   --images data/raw/industrial_fault_images.zip \
   --output data/processed/stage1_collection_inventory.json

By default SCANIA documents are expected in the sibling "documentation"
directory; override with --scania-docs if the originals are elsewhere.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path

from prepare_ai4i import SOURCE_SHA256 as AI4I_SHA256
from prepare_fault_images import SOURCE_SHA256 as IMAGE_SHA256
from prepare_scania import EXPECTED_FILES as SCANIA_FILES
from prepare_scania import validate_audit

SOURCE_SCANIA = "https://researchdata.se/en/catalogue/dataset/2024-34/2"
SOURCE_AI4I = "https://data.mendeley.com/datasets/5ww3zv87y7/1"
SOURCE_IMAGES = "https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data"
SCANIA_DOCUMENTATION = ("2024_IDA_challenge_v2.pdf", "Scania_component_X_PdM.pdf")
EXPECTED_IMAGE_COUNT = 234


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def collect_file(path: Path, expected_sha: str | None = None, kind: str = "file") -> dict:
    """Report only evidence actually found on disk, never guess a file exists."""
    result = {
        "filename": path.name,
        "exists": path.is_file(),
        "byte_size": None,
        "sha256": None,
        "hash_matches_previous_owner_audit": None,
        "file_structure_check": "NOT_RUN",
    }
    if not path.is_file():
        result["status"] = "MISSING"
        return result
    result["byte_size"] = path.stat().st_size
    result["sha256"] = sha256(path)
    if expected_sha is not None:
        result["hash_matches_previous_owner_audit"] = (
            result["sha256"].lower() == expected_sha.lower()
        )
        if not result["hash_matches_previous_owner_audit"]:
            result["status"] = "HASH_MISMATCH"
            return result
    if kind == "pdf":
        with path.open("rb") as stream:
            looks_pdf = stream.read(5) == b"%PDF-"
        result["file_structure_check"] = "PDF_HEADER_PRESENT" if looks_pdf else "NOT_A_PDF_HEADER"
        result["status"] = "PRESENT" if looks_pdf else "INVALID_FILE"
    elif kind == "ai4i":
        # Stage 1 structure sanity only; Stage 2 already owns complete auditing.
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream)
            header = next(reader, [])
        result["file_structure_check"] = "CSV_HEADER_14_FIELDS" if len(header) == 14 else "UNEXPECTED_CSV_HEADER"
        result["status"] = "PRESENT" if len(header) == 14 else "INVALID_FILE"
    elif kind == "images":
        try:
            with zipfile.ZipFile(path) as archive:
                files = [entry for entry in archive.infolist() if not entry.is_dir()]
                names = [entry.filename for entry in files]
                result["original_archive_members"] = len(files)
                result["archive_member_paths_unique"] = len(set(names)) == len(names)
                result["zip_crc_check"] = archive.testzip() is None
                safe_paths = all(
                    len(name.split("/")) == 3
                    and name.split("/")[0] == "Dataset"
                    and name.split("/")[1] in
                    {"Crack", "Misalignment", "Normal condition", "Surface defects", "Wear"}
                    and not any(p in ("", ".", "..") for p in name.split("/"))
                    and "\\" not in name
                    for name in names
                )
                result["source_image_member_count_matches_prior_audit"] = len(files) == EXPECTED_IMAGE_COUNT
                result["file_structure_check"] = (
                    "ARCHIVE_STRUCTURE_CONFIRMED" if (
                        result["archive_member_paths_unique"] and result["zip_crc_check"]
                        and safe_paths and len(files) == EXPECTED_IMAGE_COUNT
                    ) else "ARCHIVE_STRUCTURE_MISMATCH"
                )
                result["status"] = "PRESENT" if result["file_structure_check"] == "ARCHIVE_STRUCTURE_CONFIRMED" else "INVALID_FILE"
        except (zipfile.BadZipFile, OSError, RuntimeError, ValueError) as exc:
            result["status"] = "INVALID_FILE"
            result["file_structure_check"] = f"ZIP_ERROR_{type(exc).__name__}"
    else:
        result["status"] = "PRESENT"
    return result


def inspect(scania_data: Path, scania_docs: Path, audit_path: Path,
            ai4i: Path, images: Path, supporting_pdfs: list[Path]) -> dict:
    # Previous SCANIA audit must be the genuine owner-run original version 2.
    audit = validate_audit(audit_path)
    scania = {}
    for filename in SCANIA_FILES:
        scania[filename] = collect_file(
            scania_data / filename,
            expected_sha=audit["checksums"][filename]["sha256"],
        )
    official_docs = {
        name: collect_file(scania_docs / name, kind="pdf")
        for name in SCANIA_DOCUMENTATION
    }
    supporting = [collect_file(p, kind="pdf") for p in supporting_pdfs]
    ai4i_entry = collect_file(ai4i, expected_sha=AI4I_SHA256, kind="ai4i")
    images_entry = collect_file(images, expected_sha=IMAGE_SHA256, kind="images")

    scania_complete = all(x["status"] == "PRESENT" for x in scania.values())
    scania_docs_complete = all(x["status"] == "PRESENT" for x in official_docs.values())
    ai4i_complete = ai4i_entry["status"] == "PRESENT"
    images_complete = images_entry["status"] == "PRESENT"
    supporting_complete_if_supplied = all(x["status"] == "PRESENT" for x in supporting)

    all_three_acquired = scania_complete and ai4i_complete and images_complete
    packaged_source_docs_acquired = scania_docs_complete
    return {
        "status": (
            "THREE_ORIGINAL_DATASETS_AND_SCANIA_DOCUMENTS_LOCALLY_VERIFIED"
            if all_three_acquired and packaged_source_docs_acquired and supporting_complete_if_supplied
            else "STAGE1_ORIGINAL_COLLECTION_EVIDENCE_INCOMPLETE"
        ),
        "source_only_policy": "Original user-approved SCANIA v2, AI4I Mendeley V1, and original Kaggle fault images only",
        "scania": {
            "source": SOURCE_SCANIA,
            "source_version": "2024-34/2",
            "previous_owner_audit_status": audit["status"],
            "original_csv_count_expected": len(SCANIA_FILES),
            "original_csv_count_verified": sum(x["status"] == "PRESENT" for x in scania.values()),
            "original_csv_files": scania,
            "source_documentation_expected": list(SCANIA_DOCUMENTATION),
            "source_documentation": official_docs,
            "license_listed_by_original_provider": "CC BY 4.0",
            "publisher_sha256_independently_verified": False,
        },
        "ai4i": {
            "source": SOURCE_AI4I,
            "source_origin": "Mendeley repository v1; publisher describes its dataset as synthetic",
            "original_archive_extracted_csv": ai4i_entry,
            "license_listed_by_mendeley_record": "CC0 1.0",
            "publisher_sha256_independently_verified": False,
        },
        "industrial_fault_images": {
            "source": SOURCE_IMAGES,
            "original_archive": images_entry,
            "license_from_this_exact_dataset_independently_verified": False,
            "per_image_origin_and_reuse_rights_verified": False,
            "labels_and_duplicates_are_stage2_to_stage4_questions": True,
        },
        "supporting_pdf_documents": {
            "source_approval_separate_from_three_datasets": True,
            "user_supplied_paths_checked": len(supporting),
            "files": supporting,
            "additional_machine_specific_manuals_inventory_complete":
                bool(supporting) and supporting_complete_if_supplied,
            "warning": "Supporting manuals (e.g. pump PDFs) are independent documents; do not imply SCANIA/AI4I/Kaggle machine linkage.",
        },
        "acquisition": {
            "all_three_data_sources_original_files_present_and_matching_local_reference": all_three_acquired,
            "both_original_scania_documentation_pdfs_present": scania_docs_complete,
            "any_specified_supporting_pdfs_present": supporting_complete_if_supplied,
        },
        "stage1_collection_signoff": (
            "FILE_ACQUISITION_CHECKS_PASSED_RIGHTS_REVIEW_OPEN"
            if all_three_acquired and scania_docs_complete and supporting_complete_if_supplied
            else "AWAITING_MISSING_OR_CHANGED_ORIGINAL_FILES"
        ),
        "not_equivalent_to_independent_publisher_checksum_authentication": True,
        "no_new_dataset_or_synthetic_rows_added": True,
        "no_source_files_modified": True,
        "data_auditing_cleaning_label_verification_splitting_feature_engineering_run": False,
        "reminder": "Stage 1 collection can confirm bytes and inventory. It cannot claim unclear Kaggle per-photo rights or label acceptance; keep these gates open for later stages.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scania-data", required=True, type=Path)
    p.add_argument("--scania-docs", type=Path)
    p.add_argument("--scania-audit", required=True, type=Path)
    p.add_argument("--ai4i", type=Path, default=Path("data/raw/ai4i2020.csv"))
    p.add_argument("--images", type=Path, default=Path("data/raw/industrial_fault_images.zip"))
    p.add_argument("--supporting-pdf", action="append", type=Path, default=[])
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(f"Refusing to overwrite earlier collection evidence: {a.output}")
    docs_dir = a.scania_docs or (a.scania_data.parent / "documentation")
    report = inspect(a.scania_data, docs_dir, a.scania_audit,
                     a.ai4i, a.images, a.supporting_pdf)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Show only acquisition totals and blockers; full source hashes stay local.
    print(json.dumps({
        "status": report["status"],
        "scania_original_csv_verified": report["scania"]["original_csv_count_verified"],
        "scania_original_pdfs_verified": sum(
            v["status"] == "PRESENT" for v in report["scania"]["source_documentation"].values()
        ),
        "ai4i_original_csv_status": report["ai4i"]["original_archive_extracted_csv"]["status"],
        "fault_image_original_zip_status": report["industrial_fault_images"]["original_archive"]["status"],
        "supporting_manual_pdfs_checked": report["supporting_pdf_documents"]["user_supplied_paths_checked"],
        "stage1_collection_signoff": report["stage1_collection_signoff"],
        "fault_image_reuse_rights_verified": False,
        "full_inventory_file": str(a.output),
    }, indent=2))


if __name__ == "__main__":
    main()
