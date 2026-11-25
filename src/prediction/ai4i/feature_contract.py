
"""AI4I model input contract for Step 5.1.1.

Preserves the original Stage 6 feature contract.
No preprocessing, model fitting or data modification.
"""

import hashlib
import json
from pathlib import Path


# 1. Contract identification
CONTRACT_VERSION = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parents[3]

STAGE6_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "stage6_ai4i_features"
)

SOURCE_CONTRACT_PATH = (
    STAGE6_DIR / "ai4i_train_only_feature_contract.json"
)

EXPECTED_CONTRACT_SHA256 = (
    "679b2922a5ac9fcc0c55d263201cfb775"
    "5c9bca83b5aaa78d89d8a2a3bf0bbba"
)

EXPECTED_STAGE6_REPORT_SHA256 = (
    "0250e7063eaae1f551a843cde3f963ba9"
    "5f16f08cb261bd40b592783c58a3973"
)


# 2. Metadata columns
ID_COLUMN = "source_udi_not_a_feature"

TARGET_COLUMN = (
    "original_machine_failure_target_not_a_feature"
)


# 3. Approved categorical features
TYPE_FEATURES = (
    "type_H",
    "type_L",
    "type_M",
)


# 4. Approved numerical features
NUMERIC_FEATURES = (
    "air_temperature_K_train_z",
    "process_temperature_K_train_z",
    "rotational_speed_rpm_train_z",
    "torque_Nm_train_z",
    "tool_wear_min_train_z",
)


# 5. Exact feature order
FEATURE_COLUMNS = TYPE_FEATURES + NUMERIC_FEATURES

EXPECTED_FEATURE_COUNT = 8

EXPECTED_CSV_COLUMNS = (
    ID_COLUMN,
    *FEATURE_COLUMNS,
    TARGET_COLUMN,
)


# 6. Forbidden predictors
FORBIDDEN_FEATURES = frozenset({
    "UDI",
    "Product ID",
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
    "partition",
    "split",
    ID_COLUMN,
    TARGET_COLUMN,
})


# 7. Original partitions
SPLITS = ("train", "validation", "test")

SPLIT_FILES = {
    "train": "ai4i_train_features.csv",
    "validation": "ai4i_validation_features.csv",
    "test": "ai4i_test_features.csv",
}

EXPECTED_SPLIT_COUNTS = {
    "train": {
        "total": 6981,
        "normal": 6750,
        "failure": 231,
    },
    "validation": {
        "total": 1497,
        "normal": 1447,
        "failure": 50,
    },
    "test": {
        "total": 1495,
        "normal": 1446,
        "failure": 49,
    },
}

EXPECTED_TOTAL_ROWS = 9973
EXPECTED_QUARANTINED_ROWS = 27

ALLOWED_TARGET_VALUES = (0, 1)


# 8. Contract-specific exception
class FeatureContractError(ValueError):
    """Raised when the approved contract is violated."""


# 9. File fingerprint
def sha256_file(path: Path) -> str:
    """Compute a SHA-256 fingerprint without modifying a file."""

    digest = hashlib.sha256()

    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


# 10. Validate predictor names and order
def validate_feature_columns(columns) -> None:
    """Reject missing, unexpected or reordered predictors."""

    actual = tuple(columns)

    forbidden = set(actual) & FORBIDDEN_FEATURES

    if forbidden:
        raise FeatureContractError(
            f"Forbidden predictors detected: {sorted(forbidden)}"
        )

    if len(actual) != EXPECTED_FEATURE_COUNT:
        raise FeatureContractError(
            f"Expected {EXPECTED_FEATURE_COUNT} predictors, "
            f"received {len(actual)}."
        )

    if actual != FEATURE_COLUMNS:
        raise FeatureContractError(
            "Feature names or order do not match "
            "the approved Stage 6 contract."
        )


# 11. Validate complete CSV schema
def validate_csv_columns(columns) -> None:
    """Require the exact original ten-column CSV schema."""

    if tuple(columns) != EXPECTED_CSV_COLUMNS:
        raise FeatureContractError(
            "CSV schema does not match the approved "
            "Stage 6 column names and order."
        )


# 12. Load and verify the original contract
def load_source_contract(
    path: Path = SOURCE_CONTRACT_PATH,
) -> dict:
    """Read and verify the unchanged Stage 6 JSON contract."""

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Original feature contract not found: {path}"
        )

    if sha256_file(path) != EXPECTED_CONTRACT_SHA256:
        raise FeatureContractError(
            "Original feature contract SHA-256 mismatch."
        )

    with path.open("r", encoding="utf-8") as file:
        contract = json.load(file)

    validate_feature_columns(
        contract["approved_feature_columns_in_order"]
    )

    if contract["identifier_metadata_only"] != ID_COLUMN:
        raise FeatureContractError("Identifier mismatch.")

    if contract["prediction_target_metadata_only"] != TARGET_COLUMN:
        raise FeatureContractError("Target mismatch.")

    if contract["train_only_fit_original_udi_count"] != 6981:
        raise FeatureContractError("Training population mismatch.")

    if tuple(contract["type_one_hot_categories"]) != ("H", "L", "M"):
        raise FeatureContractError("One-hot categories mismatch.")

    return contract
