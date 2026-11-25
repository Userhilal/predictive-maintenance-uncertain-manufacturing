
"""AI4I development data loader for Step 5.1.1.

Load verified original Stage 6 development features.

Train and validation only.

The complete source audit remains independent in validation.py.
The development loader does not read the original test CSV,
test assignment CSV or complete raw AI4I dataset.

No preprocessing, resampling, model fitting or evaluation.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .feature_contract import (
    CONTRACT_VERSION,
    STAGE6_DIR,
    SOURCE_CONTRACT_PATH,
    EXPECTED_CONTRACT_SHA256,
    FEATURE_COLUMNS,
    ID_COLUMN,
    TARGET_COLUMN,
    EXPECTED_FEATURE_COUNT,
    EXPECTED_SPLIT_COUNTS,
    load_source_contract,
    validate_feature_columns,
)

from .validation import (
    STAGE5_DIR,
    EXPECTED_STAGE5_REPORT_SHA256,
    STAGE5_ASSIGNMENT_FILES,
    QUARANTINE_FILE,
    verify_file_integrity,
    load_verified_stage6_report,
    read_and_validate_partition,
    read_stage5_assignment,
    read_quarantined_udis,
    verify_partition_assignment,
    validate_partition,
)

from .access_policy import (
    POLICY_PATH,
    POLICY_VERSION,
    DEVELOPMENT_SPLITS,
    TestSetAccessError,
    load_access_policy,
    require_partition_access,
)


# ============================================================
# 1. CUSTOM EXCEPTION
# ============================================================

class DataLoaderError(ValueError):
    """Raised when development data loading fails."""


# ============================================================
# 2. MODEL INPUT DATA STRUCTURES
# ============================================================

@dataclass(frozen=True)
class PartitionData:
    """Validated inputs and metadata for one partition."""

    split: str
    X: pd.DataFrame
    y: pd.Series
    udi: pd.Series
    source_file: str
    source_sha256: str
    contract_version: str

    @property
    def row_count(self) -> int:
        return len(self.X)

    @property
    def feature_count(self) -> int:
        return self.X.shape[1]

    def summary(self) -> dict:
        """Return aggregate metadata without exposing row values."""

        return {
            "partition": self.split,
            "X_shape": list(self.X.shape),
            "y_shape": list(self.y.shape),
            "udi_shape": list(self.udi.shape),
            "row_count": self.row_count,
            "feature_count": self.feature_count,
            "feature_columns": list(self.X.columns),
            "class_counts": {
                "0": int(self.y.eq(0).sum()),
                "1": int(self.y.eq(1).sum()),
            },
            "source_file": self.source_file,
            "source_sha256": self.source_sha256,
            "contract_version": self.contract_version,
        }


@dataclass(frozen=True)
class DevelopmentData:
    """Train and validation inputs for future model development."""

    train: PartitionData
    validation: PartitionData

    def summary(self) -> dict:
        """Return development metadata only."""

        return {
            "status": "AI4I_DEVELOPMENT_DATA_LOADED",
            "contract_version": CONTRACT_VERSION,
            "access_policy_version": POLICY_VERSION,
            "train": self.train.summary(),
            "validation": self.validation.summary(),
            "test_exposed": False,
            "test_partition_files_read": False,
            "complete_source_audit_executed_by_loader": False,
            "model_training_performed": False,
            "model_evaluation_performed": False,
            "new_preprocessing_performed": False,
            "resampling_performed": False,
        }


# ============================================================
# 3. VERIFIED STAGE 5 REPORT
# ============================================================

def load_verified_stage5_report(
    stage5_dir: Path = STAGE5_DIR,
) -> dict:
    """Load the original Stage 5 report after hash verification."""

    report_path = (
        Path(stage5_dir) / "stage5_split_report.json"
    )

    verify_file_integrity(
        report_path,
        EXPECTED_STAGE5_REPORT_SHA256,
    )

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    expected_status = (
        "STAGE5_SOURCE_RESPECTING_TABULAR_SPLIT_"
        "MANIFESTS_CREATED_REVIEW_REQUIRED"
    )

    if report.get("status") != expected_status:
        raise DataLoaderError(
            "Unexpected original Stage 5 report status."
        )

    manifest = report.get("assignment_manifest_sha256")

    if not isinstance(manifest, dict):
        raise DataLoaderError(
            "Stage 5 assignment fingerprint manifest missing."
        )

    required_files = {
        STAGE5_ASSIGNMENT_FILES["train"],
        STAGE5_ASSIGNMENT_FILES["validation"],
        QUARANTINE_FILE,
    }

    if not required_files.issubset(manifest):
        raise DataLoaderError(
            "Required development fingerprints are missing."
        )

    verify_file_integrity(
        report_path,
        EXPECTED_STAGE5_REPORT_SHA256,
    )

    return report


# ============================================================
# 4. DEVELOPMENT-ONLY SOURCE VERIFICATION
# ============================================================

def verify_development_sources(
    stage5_dir: Path = STAGE5_DIR,
    stage6_dir: Path = STAGE6_DIR,
    policy_path: Path = POLICY_PATH,
) -> dict:
    """Verify development sources without reading test files."""

    stage5_dir = Path(stage5_dir)
    stage6_dir = Path(stage6_dir)

    # 1. Verify the access policy.
    load_access_policy(policy_path)

    # 2. Verify the original reports.
    stage5_report = load_verified_stage5_report(stage5_dir)

    stage6_report = load_verified_stage6_report(stage6_dir)

    # 3. Verify the Stage 5 / Stage 6 provenance link.
    if (
        stage6_report.get(
            "prior_stage5_report_sha256"
        )
        != EXPECTED_STAGE5_REPORT_SHA256
    ):
        raise DataLoaderError(
            "Stage 5 / Stage 6 provenance mismatch."
        )

    # 4. Verify the original feature contract.
    contract_path = stage6_dir / SOURCE_CONTRACT_PATH.name

    contract_hash = verify_file_integrity(
        contract_path,
        EXPECTED_CONTRACT_SHA256,
    )

    contract = load_source_contract(contract_path)

    # Verify the original feature contract provenance.
    if (
        contract.get("stage5_owner_verified_report_sha256")
        != EXPECTED_STAGE5_REPORT_SHA256
    ):
        raise DataLoaderError(
            "Stage 5 / feature contract provenance mismatch."
        )

    if (
        stage6_report["output_file_sha256"].get(
            SOURCE_CONTRACT_PATH.name
        )
        != contract_hash
    ):
        raise DataLoaderError(
            "Stage 6 contract manifest mismatch."
        )

    # 5. Verify only development assignment files.
    assignment_hashes = {}

    manifest = stage5_report["assignment_manifest_sha256"]

    for split in DEVELOPMENT_SPLITS:

        require_partition_access(
            split,
            purpose="development_loading",
            policy_path=policy_path,
        )

        filename = STAGE5_ASSIGNMENT_FILES[split]

        assignment_hashes[split] = verify_file_integrity(
            stage5_dir / filename,
            manifest[filename],
        )

    # 6. Verify the original quarantine file.
    quarantine_hash = verify_file_integrity(
        stage5_dir / QUARANTINE_FILE,
        manifest[QUARANTINE_FILE],
    )

    return {
        "status": "AI4I_DEVELOPMENT_SOURCES_VERIFIED",
        "stage5_report_sha256": EXPECTED_STAGE5_REPORT_SHA256,
        "feature_contract_sha256": contract_hash,
        "original_contract_status": contract["status"],
        "assignment_sha256": assignment_hashes,
        "quarantine_sha256": quarantine_hash,
        "verified_development_partitions": list(
            DEVELOPMENT_SPLITS
        ),
        "test_partition_files_read": False,
    }


# ============================================================
# 5. MODEL INPUT VALIDATION
# ============================================================

def validate_model_inputs(
    partition: PartitionData,
) -> None:
    """Validate predictors, targets and metadata separation."""

    if partition.split not in DEVELOPMENT_SPLITS:
        raise DataLoaderError(
            f"Invalid development partition: {partition.split}"
        )

    expected = EXPECTED_SPLIT_COUNTS[partition.split]

    X = partition.X
    y = partition.y
    udi = partition.udi

    # Exact approved predictor names and order.
    validate_feature_columns(X.columns)

    if X.shape != (
        expected["total"],
        EXPECTED_FEATURE_COUNT,
    ):
        raise DataLoaderError(
            f"{partition.split}: unexpected X dimensions."
        )

    if len(y) != len(X) or len(udi) != len(X):
        raise DataLoaderError(
            "Inconsistent input lengths."
        )

    if not X.index.equals(y.index):
        raise DataLoaderError(
            "X/y index mismatch."
        )

    if not X.index.equals(udi.index):
        raise DataLoaderError(
            "X/UDI index mismatch."
        )

    if ID_COLUMN in X.columns or TARGET_COLUMN in X.columns:
        raise DataLoaderError(
            "Identifier or target leakage detected."
        )

    if y.name != TARGET_COLUMN:
        raise DataLoaderError(
            "Unexpected target column name."
        )

    if udi.name != ID_COLUMN:
        raise DataLoaderError(
            "Unexpected identifier column name."
        )

    # Reconstruct the original schema in memory only.
    # Reuse the validated partition checks without fitting
    # or modifying any feature values.
    reconstructed = pd.concat(
        [udi, X, y],
        axis=1,
    )

    validate_partition(
        reconstructed,
        partition.split,
    )


# ============================================================
# 6. INTERNAL DEVELOPMENT PARTITION LOADER
# ============================================================

def _load_verified_development_partition(
    split: str,
    stage6_dir: Path,
    stage5_dir: Path,
    policy_path: Path,
    source_verification: dict,
) -> PartitionData:
    """Load one approved development partition."""

    # Enforce the centralized policy before reading data.
    require_partition_access(
        split,
        purpose="development_loading",
        policy_path=policy_path,
    )

    # Verify and read only the requested Stage 6 CSV.
    frame, validation_result = read_and_validate_partition(
        split,
        stage6_dir,
    )

    # Verify original Stage 5 assignment fingerprint.
    assignment_path = (
        Path(stage5_dir)
        / STAGE5_ASSIGNMENT_FILES[split]
    )

    expected_assignment_hash = (
        source_verification["assignment_sha256"][split]
    )

    verify_file_integrity(
        assignment_path,
        expected_assignment_hash,
    )

    assignment = read_stage5_assignment(
        split,
        stage5_dir,
    )

    verify_file_integrity(
        assignment_path,
        expected_assignment_hash,
    )

    # Verify original UDI, target and product type.
    verify_partition_assignment(
        frame,
        assignment,
        split,
    )

    # Verify quarantine exclusion.
    quarantine_path = Path(stage5_dir) / QUARANTINE_FILE

    expected_quarantine_hash = (
        source_verification["quarantine_sha256"]
    )

    verify_file_integrity(
        quarantine_path,
        expected_quarantine_hash,
    )

    quarantined_udis = read_quarantined_udis(
        stage5_dir
    )

    verify_file_integrity(
        quarantine_path,
        expected_quarantine_hash,
    )

    if set(frame[ID_COLUMN]) & quarantined_udis:
        raise DataLoaderError(
            f"{split}: quarantined UDIs detected."
        )

    # Separate predictors, target and identifier.
    X = frame.loc[:, list(FEATURE_COLUMNS)].copy(deep=True)

    y = frame.loc[:, TARGET_COLUMN].copy(deep=True)

    udi = frame.loc[:, ID_COLUMN].copy(deep=True)

    partition = PartitionData(
        split=split,
        X=X,
        y=y,
        udi=udi,
        source_file=validation_result["source_file"],
        source_sha256=validation_result["source_sha256"],
        contract_version=CONTRACT_VERSION,
    )

    validate_model_inputs(partition)

    return partition


# ============================================================
# 7. PUBLIC SINGLE PARTITION LOADER
# ============================================================

def load_partition(
    split: str,
    stage6_dir: Path = STAGE6_DIR,
    stage5_dir: Path = STAGE5_DIR,
    policy_path: Path = POLICY_PATH,
) -> PartitionData:
    """Load train or validation without reading test files."""

    # Deny unauthorized access before reading source data.
    require_partition_access(
        split,
        purpose="development_loading",
        policy_path=policy_path,
    )

    source_verification = verify_development_sources(
        stage5_dir=stage5_dir,
        stage6_dir=stage6_dir,
        policy_path=policy_path,
    )

    return _load_verified_development_partition(
        split=split,
        stage6_dir=stage6_dir,
        stage5_dir=stage5_dir,
        policy_path=policy_path,
        source_verification=source_verification,
    )


# ============================================================
# 8. PUBLIC DEVELOPMENT DATA LOADER
# ============================================================

def load_development_data(
    stage6_dir: Path = STAGE6_DIR,
    stage5_dir: Path = STAGE5_DIR,
    policy_path: Path = POLICY_PATH,
) -> DevelopmentData:
    """Load only train and validation development inputs."""

    # Verify the policy and development source fingerprints.
    source_verification = verify_development_sources(
        stage5_dir=stage5_dir,
        stage6_dir=stage6_dir,
        policy_path=policy_path,
    )

    train = _load_verified_development_partition(
        split="train",
        stage6_dir=stage6_dir,
        stage5_dir=stage5_dir,
        policy_path=policy_path,
        source_verification=source_verification,
    )

    validation = _load_verified_development_partition(
        split="validation",
        stage6_dir=stage6_dir,
        stage5_dir=stage5_dir,
        policy_path=policy_path,
        source_verification=source_verification,
    )

    # Verify development partition separation.
    if set(train.udi) & set(validation.udi):
        raise DataLoaderError(
            "Train and validation contain overlapping UDIs."
        )

    if tuple(train.X.columns) != tuple(validation.X.columns):
        raise DataLoaderError(
            "Development feature schemas differ."
        )

    # Recheck development source integrity after loading.
    final_verification = verify_development_sources(
        stage5_dir=stage5_dir,
        stage6_dir=stage6_dir,
        policy_path=policy_path,
    )

    if final_verification != source_verification:
        raise DataLoaderError(
            "Development sources changed during loading."
        )

    return DevelopmentData(
        train=train,
        validation=validation,
    )
