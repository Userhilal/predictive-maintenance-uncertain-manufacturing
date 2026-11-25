
"""AI4I data validation for Step 5.1.1.

Read-only validation of the original Stage 5 and Stage 6 outputs.

No preprocessing, resampling, source data modification,
partition regeneration or model training.
"""

import csv
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .feature_contract import (
    PROJECT_ROOT,
    STAGE6_DIR,
    SOURCE_CONTRACT_PATH,
    EXPECTED_CONTRACT_SHA256,
    EXPECTED_STAGE6_REPORT_SHA256,
    SPLITS,
    SPLIT_FILES,
    ID_COLUMN,
    TARGET_COLUMN,
    TYPE_FEATURES,
    FEATURE_COLUMNS,
    EXPECTED_CSV_COLUMNS,
    EXPECTED_SPLIT_COUNTS,
    EXPECTED_TOTAL_ROWS,
    EXPECTED_QUARANTINED_ROWS,
    ALLOWED_TARGET_VALUES,
    sha256_file,
    load_source_contract,
    validate_csv_columns,
    validate_feature_columns,
)


# ============================================================
# 1. REFERENCE PATHS AND CONSTANTS
# ============================================================

STAGE5_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stage5_eligible_splits"
)

RAW_AI4I_PATH = (
    PROJECT_ROOT / "data" / "raw" / "ai4i2020.csv"
)

EXPECTED_STAGE5_REPORT_SHA256 = (
    "9bb0db903ee0490cd543ea592ef477381"
    "9af58ad57016e6dea3ca7cc86894cda"
)

STAGE5_ASSIGNMENT_FILES = {
    split: f"ai4i_{split}_eligible_udi_assignments.csv"
    for split in SPLITS
}

QUARANTINE_FILE = "ai4i_quarantined_27_source_udis.csv"

STAGE5_ASSIGNMENT_COLUMNS = (
    "UDI",
    "original_machine_failure",
    "original_product_type",
)

QUARANTINE_COLUMNS = (
    "UDI",
    "original_machine_failure",
    "source_any_failure_mode_positive",
    "source_disagreement_type",
)

EXPECTED_PRODUCT_TYPE_COUNTS = {
    "train": {"H": 699, "L": 4189, "M": 2093},
    "validation": {"H": 150, "L": 898, "M": 449},
    "test": {"H": 149, "L": 897, "M": 449},
}


# ============================================================
# 2. CUSTOM VALIDATION EXCEPTION
# ============================================================

class DataValidationError(ValueError):
    """Raised when AI4I input data fails validation."""


# ============================================================
# 3. FILE INTEGRITY VALIDATION
# ============================================================

def verify_file_integrity(
    path: Path,
    expected_sha256: str,
) -> str:
    """Verify that a file exists and matches its expected hash."""

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    actual_sha256 = sha256_file(path)

    if actual_sha256 != expected_sha256:
        raise DataValidationError(
            f"SHA-256 mismatch for {path.name}. "
            f"Expected: {expected_sha256}. "
            f"Actual: {actual_sha256}."
        )

    return actual_sha256


def load_verified_stage6_report(
    stage6_dir: Path = STAGE6_DIR,
) -> dict:
    """Load the original Stage 6 report after hash verification."""

    report_path = (
        Path(stage6_dir) / "stage6_feature_report.json"
    )

    verify_file_integrity(
        report_path,
        EXPECTED_STAGE6_REPORT_SHA256,
    )

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    return report


def verify_stage6_integrity(
    stage6_dir: Path = STAGE6_DIR,
) -> dict:
    """Verify the report, contract and three feature CSV files."""

    stage6_dir = Path(stage6_dir)

    report = load_verified_stage6_report(stage6_dir)

    expected_hashes = report["output_file_sha256"]

    contract_name = SOURCE_CONTRACT_PATH.name

    required_files = {
        *SPLIT_FILES.values(),
        contract_name,
    }

    if set(expected_hashes) != required_files:
        raise DataValidationError(
            "Unexpected Stage 6 output file manifest."
        )

    if expected_hashes[contract_name] != EXPECTED_CONTRACT_SHA256:
        raise DataValidationError(
            "Feature contract fingerprint mismatch."
        )

    verified_files = {}

    for filename in sorted(required_files):

        file_path = stage6_dir / filename

        actual_hash = verify_file_integrity(
            file_path,
            expected_hashes[filename],
        )

        verified_files[filename] = {
            "status": "PASS",
            "sha256": actual_hash,
            "size_bytes": file_path.stat().st_size,
        }

    contract = load_source_contract(
        stage6_dir / contract_name
    )

    return {
        "status": "STAGE6_FILE_INTEGRITY_VERIFIED",
        "stage6_report_sha256": EXPECTED_STAGE6_REPORT_SHA256,
        "original_contract_status": contract["status"],
        "verified_output_file_count": len(verified_files),
        "verified_files": verified_files,
    }


# ============================================================
# 4. INDIVIDUAL PARTITION VALIDATION
# ============================================================

def validate_partition(
    frame: pd.DataFrame,
    split: str,
) -> dict:
    """Validate one original AI4I partition without modifying it."""

    if split not in EXPECTED_SPLIT_COUNTS:
        raise DataValidationError(
            f"Unknown partition: {split}"
        )

    expected = EXPECTED_SPLIT_COUNTS[split]

    # 1. Exact CSV schema.
    validate_csv_columns(frame.columns)

    # 2. Expected row count.
    if len(frame) != expected["total"]:
        raise DataValidationError(
            f"{split}: expected {expected['total']} rows, "
            f"received {len(frame)}."
        )

    # 3. Missing values.
    missing_count = int(frame.isna().sum().sum())

    if missing_count != 0:
        raise DataValidationError(
            f"{split}: {missing_count} missing values detected."
        )

    # 4. Separate predictors and metadata.
    X = frame.loc[:, list(FEATURE_COLUMNS)]
    y = frame[TARGET_COLUMN]
    udi = frame[ID_COLUMN]

    validate_feature_columns(X.columns)

    # 5. Numeric predictor types.
    non_numeric = [
        column
        for column in FEATURE_COLUMNS
        if not pd.api.types.is_numeric_dtype(X[column])
        or pd.api.types.is_bool_dtype(X[column])
        or pd.api.types.is_complex_dtype(X[column])
    ]

    if non_numeric:
        raise DataValidationError(
            f"{split}: invalid predictor types: {non_numeric}"
        )

    # 6. Finite predictor values.
    feature_values = X.to_numpy(dtype=np.float64)

    if not np.isfinite(feature_values).all():
        raise DataValidationError(
            f"{split}: non-finite predictor values detected."
        )

    # 7. One-hot encoding.
    one_hot = X.loc[:, list(TYPE_FEATURES)]

    if not one_hot.isin([0, 1]).all().all():
        raise DataValidationError(
            f"{split}: one-hot values must be 0 or 1."
        )

    if not one_hot.sum(axis=1).eq(1).all():
        raise DataValidationError(
            f"{split}: each row must have exactly "
            "one active product type."
        )

    # 8. Binary target.
    if not pd.api.types.is_integer_dtype(y):
        raise DataValidationError(
            f"{split}: target must have an integer dtype."
        )

    if not y.isin(ALLOWED_TARGET_VALUES).all():
        raise DataValidationError(
            f"{split}: invalid target values."
        )

    # 9. Original identifiers.
    if not pd.api.types.is_integer_dtype(udi):
        raise DataValidationError(
            f"{split}: UDI must have an integer dtype."
        )

    if not udi.between(1, 10000).all():
        raise DataValidationError(
            f"{split}: UDI outside original source range."
        )

    duplicate_udi_count = int(udi.duplicated().sum())

    if duplicate_udi_count != 0:
        raise DataValidationError(
            f"{split}: {duplicate_udi_count} duplicate UDIs."
        )

    # 10. Original class distribution.
    normal_count = int(y.eq(0).sum())
    failure_count = int(y.eq(1).sum())

    if (
        normal_count != expected["normal"]
        or failure_count != expected["failure"]
    ):
        raise DataValidationError(
            f"{split}: class distribution mismatch. "
            f"Normal={normal_count}, Failure={failure_count}."
        )

    return {
        "status": "PASS",
        "partition": split,
        "row_count": int(len(frame)),
        "feature_count": int(X.shape[1]),
        "predictor_values_checked": int(X.size),
        "feature_columns": list(X.columns),
        "feature_dtypes": {
            column: str(X[column].dtype)
            for column in FEATURE_COLUMNS
        },
        "target_dtype": str(y.dtype),
        "udi_dtype": str(udi.dtype),
        "missing_value_count": missing_count,
        "non_finite_predictor_count": int(
            (~np.isfinite(feature_values)).sum()
        ),
        "one_hot_valid": True,
        "binary_target_valid": True,
        "duplicate_udi_count": duplicate_udi_count,
        "class_counts": {
            "0": normal_count,
            "1": failure_count,
        },
        "failure_rate": failure_count / len(frame),
        "original_data_modified": False,
    }


# ============================================================
# 5. READ AND VALIDATE ORIGINAL PARTITION
# ============================================================

def read_and_validate_partition(
    split: str,
    stage6_dir: Path = STAGE6_DIR,
) -> tuple[pd.DataFrame, dict]:
    """Read and validate a verified original Stage 6 CSV."""

    if split not in SPLIT_FILES:
        raise DataValidationError(
            f"Unknown partition: {split}"
        )

    stage6_dir = Path(stage6_dir)

    report = load_verified_stage6_report(stage6_dir)

    filename = SPLIT_FILES[split]
    path = stage6_dir / filename

    fingerprint = verify_file_integrity(
        path,
        report["output_file_sha256"][filename],
    )

    # Validate raw CSV structure before Pandas parsing.
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.reader(file, strict=True)
        header = next(reader, [])

        validate_csv_columns(header)

        for line_number, row in enumerate(reader, start=2):

            if len(row) != len(EXPECTED_CSV_COLUMNS):
                raise DataValidationError(
                    f"{split}: invalid field count "
                    f"at CSV record {line_number}."
                )

    frame = pd.read_csv(
        path,
        encoding="utf-8-sig",
        on_bad_lines="error",
        skip_blank_lines=False,
        low_memory=False,
    )

    result = validate_partition(frame, split)

    verify_file_integrity(path, fingerprint)

    result["source_file"] = filename
    result["source_sha256"] = fingerprint

    return frame, result


# ============================================================
# 6. ORIGINAL READ-ONLY REVIEWERS
# ============================================================

def run_original_reviewer(
    script_name: str,
    arguments: list[str],
) -> dict:
    """Execute an existing read-only preprocessing reviewer."""

    allowed_reviewers = {
        "review_stage5_splits.py",
        "review_stage6_ai4i_features.py",
    }

    if script_name not in allowed_reviewers:
        raise DataValidationError(
            f"Reviewer not allowed: {script_name}"
        )

    script_path = (
        PROJECT_ROOT
        / "src"
        / "preprocessing"
        / script_name
    )

    if not script_path.is_file():
        raise FileNotFoundError(
            f"Original reviewer not found: {script_path}"
        )

    command = [
        sys.executable,
        str(script_path),
        *arguments,
    ]

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if completed.returncode != 0:
        raise DataValidationError(
            f"Original reviewer failed: {script_name}\n"
            f"{completed.stdout}\n"
            f"{completed.stderr}"
        )

    try:
        result = json.loads(completed.stdout)

    except json.JSONDecodeError as error:
        raise DataValidationError(
            f"Invalid JSON returned by {script_name}."
        ) from error

    return result


def verify_stage5_provenance(
    stage5_dir: Path = STAGE5_DIR,
) -> dict:
    """Verify original Stage 5 assignments using its reviewer."""

    stage5_dir = Path(stage5_dir).resolve()

    report_path = stage5_dir / "stage5_split_report.json"

    verify_file_integrity(
        report_path,
        EXPECTED_STAGE5_REPORT_SHA256,
    )

    result = run_original_reviewer(
        "review_stage5_splits.py",
        [
            "--input-dir",
            str(stage5_dir),
        ],
    )

    expected_status = (
        "STAGE5_ACTUAL_SOURCE_SPLIT_MANIFESTS_REVIEWED_READ_ONLY"
    )

    if result.get("status") != expected_status:
        raise DataValidationError(
            "Unexpected Stage 5 reviewer status."
        )

    if (
        result.get("original_stage5_report_sha256")
        != EXPECTED_STAGE5_REPORT_SHA256
    ):
        raise DataValidationError(
            "Stage 5 reviewer report fingerprint mismatch."
        )

    required_checks = (
        "all_seven_original_assignment_csv_sha256_verified",
        "ai4i_exact_seeded_class_type_assignment_reconstructed",
        "ai4i_all_10000_original_udi_references_accounted",
    )

    for check in required_checks:

        if result.get(check) is not True:
            raise DataValidationError(
                f"Stage 5 provenance check failed: {check}"
            )

    if result.get("ai4i_eligible_original_udi_count") != 9973:
        raise DataValidationError(
            "Stage 5 eligible population mismatch."
        )

    if result.get("ai4i_quarantined_original_udis") != 27:
        raise DataValidationError(
            "Stage 5 quarantine population mismatch."
        )

    if result.get("original_source_files_or_labels_modified") is not False:
        raise DataValidationError(
            "Stage 5 source preservation check failed."
        )

    return result


def verify_stage6_provenance(
    raw_ai4i_path: Path = RAW_AI4I_PATH,
    stage5_dir: Path = STAGE5_DIR,
    stage6_dir: Path = STAGE6_DIR,
) -> dict:
    """Verify original feature values and train-only normalization."""

    raw_ai4i_path = Path(raw_ai4i_path).resolve()
    stage5_dir = Path(stage5_dir).resolve()
    stage6_dir = Path(stage6_dir).resolve()

    verify_file_integrity(
        stage6_dir / "stage6_feature_report.json",
        EXPECTED_STAGE6_REPORT_SHA256,
    )

    result = run_original_reviewer(
        "review_stage6_ai4i_features.py",
        [
            "--ai4i",
            str(raw_ai4i_path),
            "--stage5-dir",
            str(stage5_dir),
            "--stage6-dir",
            str(stage6_dir),
        ],
    )

    expected_status = (
        "STAGE6_ACTUAL_TRAIN_ONLY_FEATURES_VERIFIED_READ_ONLY"
    )

    if result.get("status") != expected_status:
        raise DataValidationError(
            "Unexpected Stage 6 reviewer status."
        )

    if (
        result.get("original_stage6_report_sha256")
        != EXPECTED_STAGE6_REPORT_SHA256
    ):
        raise DataValidationError(
            "Stage 6 reviewer report fingerprint mismatch."
        )

    if (
        result.get("prior_stage5_owner_verified_report_sha256")
        != EXPECTED_STAGE5_REPORT_SHA256
    ):
        raise DataValidationError(
            "Stage 6 reviewer Stage 5 fingerprint mismatch."
        )

    required_checks = (
        "actual_original_ai4i_source_sha256_verified",
        "all_four_stage6_output_file_sha256_verified",
        "all_9973_original_source_udi_memberships_and_targets_verified",
        "all_27_original_disputed_udis_excluded_and_quarantined",
        "numeric_train_only_fitted_means_standard_deviations_and_ranges_recomputed",
        "all_8_predictor_values_recomputed_from_original_source",
    )

    for check in required_checks:

        if result.get(check) is not True:
            raise DataValidationError(
                f"Stage 6 provenance check failed: {check}"
            )

    if result.get("individual_predictor_values_verified") != 79784:
        raise DataValidationError(
            "Stage 6 predictor verification count mismatch."
        )

    if result.get("source_data_or_original_labels_modified_by_review") is not False:
        raise DataValidationError(
            "Stage 6 source preservation check failed."
        )

    return result


# ============================================================
# 7. STAGE 5 ASSIGNMENT VALIDATION
# ============================================================

def read_stage5_assignment(
    split: str,
    stage5_dir: Path = STAGE5_DIR,
) -> pd.DataFrame:
    """Read original AI4I assignment metadata."""

    if split not in STAGE5_ASSIGNMENT_FILES:
        raise DataValidationError(
            f"Unknown partition: {split}"
        )

    path = (
        Path(stage5_dir)
        / STAGE5_ASSIGNMENT_FILES[split]
    )

    frame = pd.read_csv(path)

    if tuple(frame.columns) != STAGE5_ASSIGNMENT_COLUMNS:
        raise DataValidationError(
            f"{split}: invalid Stage 5 assignment schema."
        )

    if frame.isna().any().any():
        raise DataValidationError(
            f"{split}: missing Stage 5 assignment values."
        )

    if len(frame) != EXPECTED_SPLIT_COUNTS[split]["total"]:
        raise DataValidationError(
            f"{split}: Stage 5 assignment count mismatch."
        )

    if not pd.api.types.is_integer_dtype(frame["UDI"]):
        raise DataValidationError(
            f"{split}: invalid Stage 5 UDI dtype."
        )

    if frame["UDI"].duplicated().any():
        raise DataValidationError(
            f"{split}: duplicate Stage 5 UDIs."
        )

    if not frame["UDI"].between(1, 10000).all():
        raise DataValidationError(
            f"{split}: Stage 5 UDI outside source range."
        )

    if not pd.api.types.is_integer_dtype(
        frame["original_machine_failure"]
    ):
        raise DataValidationError(
            f"{split}: invalid Stage 5 target dtype."
        )

    if not frame["original_machine_failure"].isin([0, 1]).all():
        raise DataValidationError(
            f"{split}: invalid Stage 5 targets."
        )

    if not frame["original_product_type"].isin(
        ["H", "L", "M"]
    ).all():
        raise DataValidationError(
            f"{split}: invalid Stage 5 product types."
        )

    return frame


def verify_partition_assignment(
    frame: pd.DataFrame,
    assignment: pd.DataFrame,
    split: str,
) -> dict:
    """Compare Stage 6 rows with their original Stage 5 metadata."""

    validate_partition(frame, split)

    stage6_udis = set(frame[ID_COLUMN])
    stage5_udis = set(assignment["UDI"])

    if stage6_udis != stage5_udis:
        raise DataValidationError(
            f"{split}: Stage 5/Stage 6 UDI membership mismatch."
        )

    # Align metadata by original UDI, not CSV row position.
    stage6_indexed = frame.set_index(ID_COLUMN).sort_index()

    stage5_indexed = (
        assignment.set_index("UDI").sort_index()
    )

    # Compare original targets.
    if not np.array_equal(
        stage6_indexed[TARGET_COLUMN].to_numpy(),
        stage5_indexed["original_machine_failure"].to_numpy(),
    ):
        raise DataValidationError(
            f"{split}: original target mismatch."
        )

    # Recover product type from the approved one-hot columns.
    recovered_types = (
        stage6_indexed.loc[:, list(TYPE_FEATURES)]
        .idxmax(axis=1)
        .map({
            "type_H": "H",
            "type_L": "L",
            "type_M": "M",
        })
    )

    if not np.array_equal(
        recovered_types.to_numpy(),
        stage5_indexed["original_product_type"].to_numpy(),
    ):
        raise DataValidationError(
            f"{split}: original product type mismatch."
        )

    actual_type_counts = {
        category: int(recovered_types.eq(category).sum())
        for category in ("H", "L", "M")
    }

    if actual_type_counts != EXPECTED_PRODUCT_TYPE_COUNTS[split]:
        raise DataValidationError(
            f"{split}: product type distribution mismatch."
        )

    return {
        "status": "PASS",
        "partition": split,
        "udi_membership_matches_stage5": True,
        "original_targets_preserved": True,
        "original_product_types_preserved": True,
        "matched_udi_count": len(stage6_udis),
        "product_type_counts": actual_type_counts,
    }


# ============================================================
# 8. QUARANTINE VALIDATION
# ============================================================

def read_quarantined_udis(
    stage5_dir: Path = STAGE5_DIR,
) -> set[int]:
    """Read the original 27 disputed source identifiers."""

    path = Path(stage5_dir) / QUARANTINE_FILE

    frame = pd.read_csv(path)

    if tuple(frame.columns) != QUARANTINE_COLUMNS:
        raise DataValidationError(
            "Unexpected quarantine CSV schema."
        )

    if len(frame) != EXPECTED_QUARANTINED_ROWS:
        raise DataValidationError(
            "Quarantine row count mismatch."
        )

    if frame["UDI"].isna().any():
        raise DataValidationError(
            "Missing quarantine UDIs."
        )

    if not pd.api.types.is_integer_dtype(frame["UDI"]):
        raise DataValidationError(
            "Invalid quarantine UDI dtype."
        )

    if frame["UDI"].duplicated().any():
        raise DataValidationError(
            "Duplicate quarantine UDIs."
        )

    if not frame["UDI"].between(1, 10000).all():
        raise DataValidationError(
            "Quarantine UDI outside original source range."
        )

    return set(int(value) for value in frame["UDI"])


# ============================================================
# 9. CROSS-PARTITION VALIDATION
# ============================================================

def validate_cross_partition_membership(
    partitions: dict[str, pd.DataFrame],
    quarantined_udis: set[int],
) -> dict:
    """Verify disjoint partitions and complete source coverage."""

    if set(partitions) != set(SPLITS):
        raise DataValidationError(
            "Expected exactly train, validation and test."
        )

    if len(quarantined_udis) != EXPECTED_QUARANTINED_ROWS:
        raise DataValidationError(
            "Unexpected quarantine population."
        )

    partition_udis = {}

    for split in SPLITS:

        validate_partition(partitions[split], split)

        partition_udis[split] = set(
            int(value)
            for value in partitions[split][ID_COLUMN]
        )

    # Check all pairwise intersections.
    overlap_counts = {}

    for first, second in combinations(SPLITS, 2):

        overlap = (
            partition_udis[first]
            & partition_udis[second]
        )

        key = f"{first}_{second}"

        overlap_counts[key] = len(overlap)

        if overlap:
            raise DataValidationError(
                f"UDI overlap between {first} and {second}: "
                f"{len(overlap)} identifiers."
            )

    # Union of all eligible partitions.
    eligible_udis = set().union(
        *partition_udis.values()
    )

    if len(eligible_udis) != EXPECTED_TOTAL_ROWS:
        raise DataValidationError(
            "Global eligible UDI count mismatch."
        )

    # Check quarantine exclusion.
    quarantine_overlap = (
        eligible_udis & quarantined_udis
    )

    if quarantine_overlap:
        raise DataValidationError(
            "Quarantined UDIs detected in eligible partitions."
        )

    # Verify exact original source coverage.
    all_accounted_udis = (
        eligible_udis | quarantined_udis
    )

    expected_source_udis = set(range(1, 10001))

    if all_accounted_udis != expected_source_udis:
        raise DataValidationError(
            "Incomplete or unexpected original UDI coverage."
        )

    return {
        "status": "PASS",
        "partition_overlap_counts": overlap_counts,
        "eligible_unique_udi_count": len(eligible_udis),
        "quarantined_unique_udi_count": len(quarantined_udis),
        "quarantine_overlap_count": len(quarantine_overlap),
        "all_original_udis_accounted": len(all_accounted_udis),
        "complete_original_source_coverage": True,
    }


# ============================================================
# 10. COMPLETE AI4I DATA VALIDATION
# ============================================================

def validate_all_ai4i_data(
    stage5_dir: Path = STAGE5_DIR,
    stage6_dir: Path = STAGE6_DIR,
    raw_ai4i_path: Path = RAW_AI4I_PATH,
) -> dict:
    """Execute the complete read-only AI4I input audit.

    Test data is inspected only for integrity and provenance.
    No model fitting, selection, calibration or evaluation.
    """

    # 1. Verify original files and provenance.
    stage6_integrity = verify_stage6_integrity(stage6_dir)

    stage5_review = verify_stage5_provenance(stage5_dir)

    stage6_review = verify_stage6_provenance(
        raw_ai4i_path=raw_ai4i_path,
        stage5_dir=stage5_dir,
        stage6_dir=stage6_dir,
    )

    # 2. Validate each original partition.
    partitions = {}
    partition_results = {}
    assignment_results = {}

    for split in SPLITS:

        frame, result = read_and_validate_partition(
            split,
            stage6_dir,
        )

        assignment = read_stage5_assignment(
            split,
            stage5_dir,
        )

        assignment_result = verify_partition_assignment(
            frame,
            assignment,
            split,
        )

        partitions[split] = frame
        partition_results[split] = result
        assignment_results[split] = assignment_result

    # 3. Read original quarantine metadata.
    quarantined_udis = read_quarantined_udis(
        stage5_dir
    )

    # 4. Validate global partition membership.
    cross_partition_result = (
        validate_cross_partition_membership(
            partitions,
            quarantined_udis,
        )
    )

    # 5. Compute actual aggregate counts.
    total_rows = sum(
        result["row_count"]
        for result in partition_results.values()
    )

    total_predictor_values = sum(
        result["predictor_values_checked"]
        for result in partition_results.values()
    )

    total_normal = sum(
        result["class_counts"]["0"]
        for result in partition_results.values()
    )

    total_failure = sum(
        result["class_counts"]["1"]
        for result in partition_results.values()
    )

    if total_rows != EXPECTED_TOTAL_ROWS:
        raise DataValidationError(
            "Unexpected total eligible row count."
        )

    if total_predictor_values != 79784:
        raise DataValidationError(
            "Unexpected total predictor value count."
        )

    if total_normal != 9643 or total_failure != 330:
        raise DataValidationError(
            "Unexpected global target distribution."
        )

    # 6. Recheck integrity after the audit.
    final_stage6_integrity = verify_stage6_integrity(
        stage6_dir
    )

    if final_stage6_integrity != stage6_integrity:
        raise DataValidationError(
            "Stage 6 files changed during validation."
        )

    verify_stage5_provenance(stage5_dir)

    # 7. Return actual audit results, not the data itself.
    return {
        "status": "AI4I_MODEL_INPUT_DATA_VALIDATED",
        "scope": "STEP_5_1_1_READ_ONLY_DATA_AUDIT",
        "dataset": "AI4I 2020",
        "stage6_integrity": stage6_integrity,
        "stage5_original_reviewer": stage5_review,
        "stage6_original_reviewer": stage6_review,
        "partitions": partition_results,
        "stage5_stage6_alignment": assignment_results,
        "cross_partition_validation": cross_partition_result,
        "summary": {
            "eligible_rows": total_rows,
            "feature_count": len(FEATURE_COLUMNS),
            "predictor_values_checked": total_predictor_values,
            "normal_count": total_normal,
            "failure_count": total_failure,
            "quarantined_rows": len(quarantined_udis),
            "failure_rate": total_failure / total_rows,
        },
        "original_stage6_files_preserved": True,
        "test_used_for_integrity_audit_only": True,
        "model_training_performed": False,
        "model_evaluation_performed": False,
        "resampling_performed": False,
        "new_preprocessing_performed": False,
    }
