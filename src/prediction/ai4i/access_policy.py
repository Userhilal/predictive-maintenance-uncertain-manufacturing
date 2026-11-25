
"""AI4I partition access policy for Step 5.1.1.

Application-level protection of the original test partition.

No model training, evaluation or source data modification.
"""

import json
from pathlib import Path

from .feature_contract import (
    PROJECT_ROOT,
    CONTRACT_VERSION,
    SPLITS,
)


# ============================================================
# 1. POLICY CONSTANTS
# ============================================================

POLICY_VERSION = "1.0.0"

CURRENT_PROJECT_STEP = "5.1.1"

POLICY_PATH = (
    PROJECT_ROOT
    / "configs"
    / "ai4i_test_access_policy.json"
)

DEVELOPMENT_SPLITS = (
    "train",
    "validation",
)

PROTECTED_SPLIT = "test"

ALLOWED_PURPOSES = (
    "development_loading",
    "integrity_audit",
)

RESTRICTED_TEST_OPERATIONS = (
    "development_loading_allowed",
    "training_allowed",
    "cross_validation_allowed",
    "hyperparameter_tuning_allowed",
    "model_selection_allowed",
    "feature_selection_allowed",
    "threshold_selection_allowed",
    "probability_calibration_allowed",
    "final_evaluation_allowed_at_current_step",
)

RESTRICTED_CURRENT_STEP_OPERATIONS = (
    "model_training_allowed",
    "model_evaluation_allowed",
    "new_preprocessing_allowed",
    "resampling_allowed",
    "partition_regeneration_allowed",
    "original_data_modification_allowed",
)


# ============================================================
# 2. CUSTOM EXCEPTIONS
# ============================================================

class AccessPolicyError(ValueError):
    """Raised when the access policy is invalid."""


class TestSetAccessError(PermissionError):
    """Raised when protected test data access is requested."""


# ============================================================
# 3. LOAD AND VALIDATE ACCESS POLICY
# ============================================================

def load_access_policy(
    path: Path = POLICY_PATH,
) -> dict:
    """Load and verify the Step 5.1.1 access policy."""

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Access policy not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        policy = json.load(file)

    if policy.get("policy_version") != POLICY_VERSION:
        raise AccessPolicyError(
            "Unexpected access policy version."
        )

    if policy.get("dataset") != "AI4I 2020":
        raise AccessPolicyError(
            "Unexpected dataset."
        )

    if (
        policy.get("feature_contract_version")
        != CONTRACT_VERSION
    ):
        raise AccessPolicyError(
            "Feature contract version mismatch."
        )

    if (
        policy.get("current_project_step")
        != CURRENT_PROJECT_STEP
    ):
        raise AccessPolicyError(
            "Unexpected project step."
        )

    if tuple(
        policy.get("development_partitions", [])
    ) != DEVELOPMENT_SPLITS:
        raise AccessPolicyError(
            "Development partition policy mismatch."
        )

    if policy.get("protected_partition") != PROTECTED_SPLIT:
        raise AccessPolicyError(
            "Protected partition mismatch."
        )

    # Verify that all forbidden test operations remain disabled.
    test_access = policy.get("test_access", {})

    for operation in RESTRICTED_TEST_OPERATIONS:

        if test_access.get(operation) is not False:
            raise AccessPolicyError(
                f"Forbidden test operation enabled: {operation}"
            )

    if (
        test_access.get(
            "read_only_integrity_audit_allowed"
        ) is not True
    ):
        raise AccessPolicyError(
            "Read-only audit policy mismatch."
        )

    # Verify that Step 5.1.1 restrictions remain active.
    restrictions = policy.get(
        "current_step_restrictions",
        {},
    )

    for operation in RESTRICTED_CURRENT_STEP_OPERATIONS:

        if restrictions.get(operation) is not False:
            raise AccessPolicyError(
                f"Forbidden Step 5.1.1 operation: {operation}"
            )

    if (
        policy.get(
            "original_test_file_must_remain_unchanged"
        ) is not True
    ):
        raise AccessPolicyError(
            "Original test preservation policy mismatch."
        )

    if policy.get("physical_file_isolation") is not False:
        raise AccessPolicyError(
            "Physical isolation claim is unsupported."
        )

    return policy


# ============================================================
# 4. PARTITION ACCESS CONTROL
# ============================================================

def require_partition_access(
    split: str,
    purpose: str = "development_loading",
    policy_path: Path = POLICY_PATH,
) -> None:
    """Reject partition access outside the approved purpose."""

    if split not in SPLITS:
        raise AccessPolicyError(
            f"Unknown partition: {split}"
        )

    if purpose not in ALLOWED_PURPOSES:
        raise AccessPolicyError(
            f"Access purpose not allowed at Step 5.1.1: "
            f"{purpose}"
        )

    # Verify the policy before granting access.
    load_access_policy(policy_path)

    # Read-only integrity audits may inspect original partitions.
    if purpose == "integrity_audit":
        return

    # Development loading must never expose the test partition.
    if split == PROTECTED_SPLIT:
        raise TestSetAccessError(
            "Test data is locked during model development. "
            "Only train and validation are allowed."
        )

    if split not in DEVELOPMENT_SPLITS:
        raise AccessPolicyError(
            f"Partition not available for development: {split}"
        )


# ============================================================
# 5. POLICY SUMMARY
# ============================================================

def access_policy_summary(
    path: Path = POLICY_PATH,
) -> dict:
    """Return the verified access policy status."""

    policy = load_access_policy(path)

    return {
        "status": "AI4I_TEST_ACCESS_POLICY_VALIDATED",
        "policy_version": policy["policy_version"],
        "feature_contract_version": CONTRACT_VERSION,
        "current_project_step": CURRENT_PROJECT_STEP,
        "development_partitions": list(DEVELOPMENT_SPLITS),
        "protected_partition": PROTECTED_SPLIT,
        "test_development_access_allowed": False,
        "test_integrity_audit_allowed": True,
        "test_final_evaluation_allowed": False,
        "model_training_allowed": False,
        "physical_file_isolation": False,
        "enforcement_scope": policy["enforcement_scope"],
    }
