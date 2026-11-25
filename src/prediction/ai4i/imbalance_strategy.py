
"""AI4I class imbalance strategy.

Step 5.1.1 - Task C.

Compute balanced class weights exclusively from
the original validated training partition.

No resampling, model training, prediction,
evaluation or new preprocessing.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from sklearn.utils.class_weight import compute_class_weight

from .feature_contract import (
    CONTRACT_VERSION,
    EXPECTED_SPLIT_COUNTS,
    PROJECT_ROOT,
    TARGET_COLUMN,
)

from .data_loader import (
    load_partition,
    validate_model_inputs,
)


# ============================================================
# 1. STRATEGY CONSTANTS
# ============================================================

STRATEGY_VERSION = "1.0.0"

DATASET_NAME = "AI4I 2020"

WEIGHT_SOURCE_PARTITION = "train"

CLASS_LABELS = (0, 1)

NEGATIVE_CLASS = 0

POSITIVE_CLASS = 1

WEIGHT_METHOD = "balanced"

STRATEGY_CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "ai4i_imbalance_strategy.json"
)

class ImbalanceStrategyError(ValueError):
    """Raised when imbalance strategy validation fails."""


# ============================================================
# 2. CLASS WEIGHT RESULT
# ============================================================

@dataclass(frozen=True)
class ClassWeightResult:
    """Immutable result of the training weight computation."""

    normal_count: int
    failure_count: int

    normal_weight: float
    failure_weight: float

    source_file: str
    source_sha256: str

    contract_version: str

    @property
    def total_count(self) -> int:

        return (
            self.normal_count
            + self.failure_count
        )

    @property
    def failure_rate(self) -> float:

        return (
            self.failure_count
            / self.total_count
        )

    @property
    def imbalance_ratio(self) -> float:

        return (
            self.normal_count
            / self.failure_count
        )

    @property
    def weight_ratio(self) -> float:

        return (
            self.failure_weight
            / self.normal_weight
        )

    @property
    def class_weights(self) -> dict[int, float]:

        return {
            NEGATIVE_CLASS: self.normal_weight,
            POSITIVE_CLASS: self.failure_weight,
        }

    @property
    def weighted_normal_count(self) -> float:

        return (
            self.normal_count
            * self.normal_weight
        )

    @property
    def weighted_failure_count(self) -> float:

        return (
            self.failure_count
            * self.failure_weight
        )

    def summary(self) -> dict:
        """Return machine-readable computation evidence."""

        return {
            "status": "AI4I_TRAIN_CLASS_WEIGHTS_COMPUTED",

            "strategy_version": STRATEGY_VERSION,

            "dataset": DATASET_NAME,

            "feature_contract_version": (
                self.contract_version
            ),

            "source_partition": WEIGHT_SOURCE_PARTITION,

            "source_file": self.source_file,

            "source_sha256": self.source_sha256,

            "method": WEIGHT_METHOD,

            "formula": "N / (K * N_c)",

            "total_training_rows": self.total_count,

            "class_counts": {
                "0": self.normal_count,
                "1": self.failure_count,
            },

            "failure_rate": self.failure_rate,

            "imbalance_ratio": self.imbalance_ratio,

            "class_weights": {
                "0": self.normal_weight,
                "1": self.failure_weight,
            },

            "weight_ratio": self.weight_ratio,

            "weighted_class_totals": {
                "0": self.weighted_normal_count,
                "1": self.weighted_failure_count,
            },

            "validation_labels_used_for_weights": False,

            "test_labels_used_for_weights": False,

            "resampling_performed": False,

            "new_preprocessing_performed": False,

            "model_training_performed": False,

            "model_prediction_performed": False,

            "model_evaluation_performed": False,

            "industrial_cost_ratio_estimated": False,
        }


# ============================================================
# 3. COMPUTATION VALIDATION
# ============================================================

def validate_class_weight_result(
    result: ClassWeightResult,
) -> None:
    """Verify mathematical and source consistency."""

    expected = EXPECTED_SPLIT_COUNTS["train"]

    if result.total_count != expected["total"]:

        raise ImbalanceStrategyError(
            "Unexpected training observation count."
        )

    if result.normal_count != expected["normal"]:

        raise ImbalanceStrategyError(
            "Unexpected normal class count."
        )

    if result.failure_count != expected["failure"]:

        raise ImbalanceStrategyError(
            "Unexpected failure class count."
        )

    if result.contract_version != CONTRACT_VERSION:

        raise ImbalanceStrategyError(
            "Feature contract version mismatch."
        )

    if (
        result.normal_count <= 0
        or result.failure_count <= 0
    ):

        raise ImbalanceStrategyError(
            "Both classes must be present."
        )

    weights = (
        result.normal_weight,
        result.failure_weight,
    )

    if not all(
        math.isfinite(weight) and weight > 0
        for weight in weights
    ):

        raise ImbalanceStrategyError(
            "Class weights must be finite and positive."
        )

    # Independent mathematical verification.
    expected_normal_weight = (
        result.total_count
        / (2 * result.normal_count)
    )

    expected_failure_weight = (
        result.total_count
        / (2 * result.failure_count)
    )

    if not math.isclose(
        result.normal_weight,
        expected_normal_weight,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):

        raise ImbalanceStrategyError(
            "Normal class weight formula mismatch."
        )

    if not math.isclose(
        result.failure_weight,
        expected_failure_weight,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):

        raise ImbalanceStrategyError(
            "Failure class weight formula mismatch."
        )

    if not math.isclose(
        result.weight_ratio,
        result.imbalance_ratio,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):

        raise ImbalanceStrategyError(
            "Class weight ratio mismatch."
        )

    expected_weighted_total = (
        result.total_count / 2
    )

    for weighted_total in (
        result.weighted_normal_count,
        result.weighted_failure_count,
    ):

        if not math.isclose(
            weighted_total,
            expected_weighted_total,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):

            raise ImbalanceStrategyError(
                "Weighted class totals are not balanced."
            )



# ============================================================
# STRATEGY CONFIGURATION VALIDATION
# ============================================================

def load_imbalance_config(
    path: Path = STRATEGY_CONFIG_PATH,
) -> dict:
    """Load and validate the declared imbalance strategy."""

    path = Path(path)

    try:

        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:

            config = json.load(file)

    except (OSError, ValueError) as exc:

        raise ImbalanceStrategyError(
            f"Unable to load imbalance configuration: {path}"
        ) from exc

    if not isinstance(config, dict):

        raise ImbalanceStrategyError(
            "Configuration must be a JSON object."
        )

    def require_value(
        section: dict,
        key: str,
        expected,
    ) -> None:
        """Reject missing or unexpected configuration values."""

        if not isinstance(section, dict):

            raise ImbalanceStrategyError(
                "Invalid configuration section."
            )

        if key not in section:

            raise ImbalanceStrategyError(
                f"Missing configuration key: {key}"
            )

        actual = section[key]

        if (
            type(actual) is not type(expected)
            or actual != expected
        ):

            raise ImbalanceStrategyError(
                f"Invalid configuration value for {key}: "
                f"expected {expected!r}, got {actual!r}"
            )

    def require_section(
        parent: dict,
        key: str,
    ) -> dict:

        section = parent.get(key)

        if not isinstance(section, dict):

            raise ImbalanceStrategyError(
                f"Missing or invalid section: {key}"
            )

        return section

    # 1. Configuration identity.

    for key, expected in {
        "strategy_version": STRATEGY_VERSION,
        "feature_contract_version": CONTRACT_VERSION,
        "dataset": DATASET_NAME,
        "project_step": "5.1.1",
        "task": "C - Class Imbalance Strategy",
    }.items():

        require_value(config, key, expected)

    # 2. Classification contract.

    classification = require_section(
        config,
        "classification_task",
    )

    for key, expected in {
        "type": "binary_classification",
        "target_column": TARGET_COLUMN,
        "negative_class": NEGATIVE_CLASS,
        "positive_class": POSITIVE_CLASS,
        "negative_class_meaning": "Normal operation",
        "positive_class_meaning": "Machine failure",
    }.items():

        require_value(
            classification,
            key,
            expected,
        )

    # 3. Train-only class weighting.

    weighting = require_section(
        config,
        "class_weighting",
    )

    for key, expected in {
        "enabled": True,
        "method": WEIGHT_METHOD,
        "formula": "N / (K * N_c)",
        "source_partition": WEIGHT_SOURCE_PARTITION,
        "compute_from_verified_training_labels": True,
        "validation_labels_allowed_for_weight_computation": False,
        "test_labels_allowed_for_weight_computation": False,
        "hardcoded_weights_allowed": False,
        "industrial_cost_ratio_estimated": False,
    }.items():

        require_value(
            weighting,
            key,
            expected,
        )

    # 4. Original training distribution.

    distribution = require_section(
        config,
        "expected_training_distribution",
    )

    for key, expected in (
        EXPECTED_SPLIT_COUNTS["train"].items()
    ):

        require_value(
            distribution,
            key,
            expected,
        )

    # 5. Approved baseline strategy.

    models = require_section(
        config,
        "model_strategy",
    )

    if set(models) != {
        "dummy_classifier",
        "logistic_regression",
        "random_forest",
    }:

        raise ImbalanceStrategyError(
            "Unexpected baseline model strategy."
        )

    dummy = require_section(
        models,
        "dummy_classifier",
    )

    require_value(
        dummy,
        "class_weighting_enabled",
        False,
    )

    require_value(
        dummy,
        "strategy",
        "prior",
    )

    for model_name in (
        "logistic_regression",
        "random_forest",
    ):

        model = require_section(
            models,
            model_name,
        )

        require_value(
            model,
            "class_weighting_enabled",
            True,
        )

        require_value(
            model,
            "weight_source",
            "verified_train_class_weights",
        )

        require_value(
            model,
            "additional_sample_weight_allowed",
            False,
        )

    require_value(
        models["random_forest"],
        "balanced_subsample_enabled",
        False,
    )

    # 6. Resampling restrictions.

    resampling = require_section(
        config,
        "resampling_policy",
    )

    for key in (
        "random_oversampling_allowed",
        "random_undersampling_allowed",
        "smote_allowed",
        "adasyn_allowed",
        "synthetic_observations_allowed",
        "observation_duplication_allowed",
        "observation_removal_allowed",
    ):

        require_value(
            resampling,
            key,
            False,
        )

    require_value(
        resampling,
        "original_class_distribution_must_be_preserved",
        True,
    )

    # 7. Validation and leakage prevention.

    validation = require_section(
        config,
        "validation_policy",
    )

    for key, expected in {
        "existing_train_validation_test_partitions_preserved": True,
        "new_partition_generation_allowed": False,
        "new_preprocessing_allowed": False,
        "stratified_cross_validation_enabled": False,
        "future_model_selection_partition": "validation",
        "future_threshold_selection_partition": "validation",
        "test_used_for_model_selection": False,
        "test_used_for_threshold_selection": False,
    }.items():

        require_value(
            validation,
            key,
            expected,
        )

    # 8. Evaluation guidance.

    evaluation = require_section(
        config,
        "evaluation_guidance",
    )

    for key, expected in {
        "primary_metric": "average_precision",
        "positive_class": POSITIVE_CLASS,
        "accuracy_as_primary_metric_allowed": False,
        "precision_recall_analysis_required": True,
        "recall_required": True,
        "precision_required": True,
        "confusion_matrix_required": True,
        "probability_calibration_assessment_required": True,
        "weighted_probabilities_assumed_calibrated": False,
        "evaluation_protocol_defined_in_task_e": True,
    }.items():

        require_value(
            evaluation,
            key,
            expected,
        )

    # 9. Current project restrictions.

    restrictions = require_section(
        config,
        "current_step_restrictions",
    )

    for key in (
        "model_training_allowed",
        "model_prediction_allowed",
        "model_evaluation_allowed",
        "hyperparameter_tuning_allowed",
        "threshold_optimization_allowed",
        "probability_calibration_allowed",
        "original_data_modification_allowed",
    ):

        require_value(
            restrictions,
            key,
            False,
        )

    return config


# ============================================================
# 4. TRAIN-ONLY CLASS WEIGHT COMPUTATION
# ============================================================

def compute_training_class_weights() -> ClassWeightResult:
    """Compute class weights from verified original train data.

    This function does not accept arbitrary labels or a
    partition argument. The source is always the approved
    training partition.
    """

    # Validate the approved strategy before loading data.
    load_imbalance_config()

    train = load_partition(
        WEIGHT_SOURCE_PARTITION
    )

    validate_model_inputs(train)

    if train.split != WEIGHT_SOURCE_PARTITION:

        raise ImbalanceStrategyError(
            "Class weights must use the train partition."
        )

    labels = train.y.to_numpy(copy=True)

    if set(np.unique(labels).tolist()) != set(CLASS_LABELS):

        raise ImbalanceStrategyError(
            "Expected exactly binary labels 0 and 1."
        )

    normal_count = int(
        np.count_nonzero(
            labels == NEGATIVE_CLASS
        )
    )

    failure_count = int(
        np.count_nonzero(
            labels == POSITIVE_CLASS
        )
    )

    weights = compute_class_weight(
        class_weight=WEIGHT_METHOD,
        classes=np.asarray(CLASS_LABELS),
        y=labels,
    )

    result = ClassWeightResult(
        normal_count=normal_count,
        failure_count=failure_count,

        normal_weight=float(weights[0]),
        failure_weight=float(weights[1]),

        source_file=train.source_file,
        source_sha256=train.source_sha256,

        contract_version=train.contract_version,
    )

    validate_class_weight_result(result)

    return result
