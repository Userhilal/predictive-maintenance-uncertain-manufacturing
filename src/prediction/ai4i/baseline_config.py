
"""Fixed AI4I baseline configuration.

Step 5.1.1 - Task D.

Only configuration validation and unfitted estimator construction
are authorized. No training, prediction or evaluation is performed.
"""

import inspect
import json
import platform

from copy import deepcopy
from pathlib import Path

import sklearn

from sklearn.base import BaseEstimator
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError

from .feature_contract import (
    PROJECT_ROOT,
    CONTRACT_VERSION,
    TARGET_COLUMN,
    FEATURE_COLUMNS,
    sha256_file,
)

from .access_policy import (
    load_access_policy,
    require_partition_access,
)

from .imbalance_strategy import (
    STRATEGY_VERSION,
    load_imbalance_config,
    compute_training_class_weights,
    validate_class_weight_result,
)


# ---------------------------------------------------------
# 1. Configuration constants
# ---------------------------------------------------------

CONFIGURATION_VERSION = "1.0.0"

DATASET_NAME = "AI4I 2020"

CURRENT_PROJECT_STEP = "5.1.1"

RANDOM_SEED = 42

EXPECTED_PYTHON_VERSION = "3.11.9"

EXPECTED_SKLEARN_VERSION = "1.9.1"

BASELINE_CONFIG_PATH = (
    PROJECT_ROOT
    / "configs"
    / "ai4i_baseline_models.json"
)

EXPECTED_BASELINE_CONFIG_SHA256 = (
    "e974bb972168347a436b8b9f1ff6f61735"
    "a650e753d04e9452a3679732a4786e"
)

MODEL_ORDER = (
    "dummy_classifier",
    "logistic_regression",
    "random_forest",
)

ESTIMATOR_CLASSES = {
    "dummy_classifier": DummyClassifier,
    "logistic_regression": LogisticRegression,
    "random_forest": RandomForestClassifier,
}

WEIGHTED_MODELS = (
    "logistic_regression",
    "random_forest",
)


class BaselineConfigurationError(ValueError):
    """Raised when the baseline configuration is invalid."""


# ---------------------------------------------------------
# 2. Expected fixed model parameters
# ---------------------------------------------------------

EXPECTED_PARAMETERS = {
    "dummy_classifier": {
        "strategy": "prior",
        "random_state": 42,
        "constant": None,
    },

    "logistic_regression": {
        "solver": "lbfgs",
        "C": 1.0,
        "l1_ratio": 0.0,
        "dual": False,
        "tol": 0.0001,
        "fit_intercept": True,
        "max_iter": 1000,
        "random_state": 42,
        "verbose": 0,
        "warm_start": False,
    },

    "random_forest": {
        "n_estimators": 200,
        "criterion": "gini",
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "min_weight_fraction_leaf": 0.0,
        "max_features": "sqrt",
        "max_leaf_nodes": None,
        "min_impurity_decrease": 0.0,
        "bootstrap": True,
        "oob_score": False,
        "n_jobs": 1,
        "random_state": 42,
        "verbose": 0,
        "warm_start": False,
        "ccp_alpha": 0.0,
        "max_samples": None,
        "monotonic_cst": None,
    },
}


EXPECTED_RESTRICTIONS = {
    "estimator_construction_allowed": True,
    "model_training_allowed": False,
    "model_prediction_allowed": False,
    "model_evaluation_allowed": False,
    "hyperparameter_tuning_allowed": False,
    "threshold_optimization_allowed": False,
    "probability_calibration_allowed": False,
    "trained_model_serialization_allowed": False,
    "original_data_modification_allowed": False,
    "additional_models_allowed": False,
    "xgboost_allowed": False,
    "scania_modeling_allowed": False,
    "image_modeling_allowed": False,
    "rag_implementation_allowed": False,
}


# ---------------------------------------------------------
# 3. Strict configuration validation helpers
# ---------------------------------------------------------

def require_value(
    mapping: dict,
    key: str,
    expected,
    context: str,
) -> None:

    if key not in mapping:
        raise BaselineConfigurationError(
            f"Missing configuration field: {context}.{key}"
        )

    actual = mapping[key]

    if type(actual) is not type(expected) or actual != expected:
        raise BaselineConfigurationError(
            f"Invalid {context}.{key}: "
            f"expected {expected!r}, got {actual!r}"
        )


def require_section(
    mapping: dict,
    key: str,
    context: str = "configuration",
) -> dict:

    section = mapping.get(key)

    if not isinstance(section, dict):
        raise BaselineConfigurationError(
            f"Invalid or missing section: {context}.{key}"
        )

    return section


def validate_expected_values(
    mapping: dict,
    expected_values: dict,
    context: str,
    exact_keys: bool = True,
) -> None:

    if exact_keys and set(mapping) != set(expected_values):
        missing = set(expected_values) - set(mapping)
        unexpected = set(mapping) - set(expected_values)

        raise BaselineConfigurationError(
            f"Invalid keys in {context}: "
            f"missing={sorted(missing)}, "
            f"unexpected={sorted(unexpected)}"
        )

    for key, expected in expected_values.items():
        require_value(mapping, key, expected, context)


def reject_duplicate_json_keys(pairs):

    result = {}

    for key, value in pairs:
        if key in result:
            raise BaselineConfigurationError(
                f"Duplicate JSON key: {key}"
            )

        result[key] = value

    return result


# ---------------------------------------------------------
# 4. Runtime environment verification
# ---------------------------------------------------------

def validate_runtime_environment() -> dict:

    python_version = platform.python_version()
    sklearn_version = sklearn.__version__

    if python_version != EXPECTED_PYTHON_VERSION:
        raise BaselineConfigurationError(
            f"Expected Python {EXPECTED_PYTHON_VERSION}, "
            f"got {python_version}"
        )

    if sklearn_version != EXPECTED_SKLEARN_VERSION:
        raise BaselineConfigurationError(
            f"Expected scikit-learn {EXPECTED_SKLEARN_VERSION}, "
            f"got {sklearn_version}"
        )

    lock_path = PROJECT_ROOT / "uv.lock"

    if not lock_path.is_file():
        raise BaselineConfigurationError(
            "Required uv.lock file is missing."
        )

    return {
        "status": "PASS",
        "python_version": python_version,
        "scikit_learn_version": sklearn_version,
        "dependency_lock_file": "uv.lock",
        "dependency_lock_sha256": sha256_file(lock_path),
    }


# ---------------------------------------------------------
# 5. Individual model validation
# ---------------------------------------------------------

def validate_model_configuration(
    model_name: str,
    model_config: dict,
) -> None:

    if model_name not in MODEL_ORDER:
        raise BaselineConfigurationError(
            f"Unauthorized model: {model_name}"
        )

    expected_metadata = {
        "dummy_classifier": {
            "enabled": True,
            "display_name": "Dummy Classifier",
            "estimator_class": "sklearn.dummy.DummyClassifier",
            "role": "unweighted_reference_baseline",
        },

        "logistic_regression": {
            "enabled": True,
            "display_name": "Logistic Regression",
            "estimator_class": (
                "sklearn.linear_model.LogisticRegression"
            ),
            "role": "weighted_linear_baseline",
        },

        "random_forest": {
            "enabled": True,
            "display_name": "Random Forest",
            "estimator_class": (
                "sklearn.ensemble.RandomForestClassifier"
            ),
            "role": "weighted_nonlinear_baseline",
        },
    }

    context = f"models.{model_name}"

    expected_keys = set(expected_metadata[model_name]) | {
        "parameters",
        "class_weight_policy",
    }

    if model_name == "random_forest":
        expected_keys.add("bootstrap_policy")

    if set(model_config) != expected_keys:
        raise BaselineConfigurationError(
            f"Unexpected or missing fields in {context}"
        )

    validate_expected_values(
        model_config,
        expected_metadata[model_name],
        context,
        exact_keys=False,
    )

    parameters = require_section(
        model_config,
        "parameters",
        context,
    )

    validate_expected_values(
        parameters,
        EXPECTED_PARAMETERS[model_name],
        f"{context}.parameters",
    )

    supported_parameters = set(
        inspect.signature(
            ESTIMATOR_CLASSES[model_name]
        ).parameters
    )

    unsupported_parameters = (
        set(parameters) - supported_parameters
    )

    if unsupported_parameters:
        raise BaselineConfigurationError(
            f"Unsupported parameters for {model_name}: "
            f"{sorted(unsupported_parameters)}"
        )

    weight_policy = require_section(
        model_config,
        "class_weight_policy",
        context,
    )

    if model_name == "dummy_classifier":

        expected_weight_policy = {
            "enabled": False,
            "source": None,
            "additional_sample_weight_allowed": False,
        }

    else:

        expected_weight_policy = {
            "enabled": True,
            "source": "verified_train_class_weights",
            "method": "balanced",
            "source_partition": "train",
            "hardcoded_weights_allowed": False,
            "additional_sample_weight_allowed": False,
        }

        if "class_weight" not in supported_parameters:
            raise BaselineConfigurationError(
                f"{model_name} does not support class_weight."
            )

    if model_name == "random_forest":
        expected_weight_policy[
            "balanced_subsample_enabled"
        ] = False

    validate_expected_values(
        weight_policy,
        expected_weight_policy,
        f"{context}.class_weight_policy",
    )

    if model_name == "random_forest":

        bootstrap_policy = require_section(
            model_config,
            "bootstrap_policy",
            context,
        )

        validate_expected_values(
            bootstrap_policy,
            {
                "internal_estimator_bootstrap_allowed": True,
                "external_dataset_resampling_allowed": False,
                "original_dataset_modification_allowed": False,
            },
            f"{context}.bootstrap_policy",
        )


# ---------------------------------------------------------
# 6. Complete baseline configuration validation
# ---------------------------------------------------------

def validate_baseline_configuration(config: dict) -> None:

    if not isinstance(config, dict):
        raise BaselineConfigurationError(
            "Baseline configuration must be a JSON object."
        )

    expected_metadata = {
        "configuration_version": CONFIGURATION_VERSION,
        "feature_contract_version": CONTRACT_VERSION,
        "imbalance_strategy_version": STRATEGY_VERSION,
        "dataset": DATASET_NAME,
        "project_step": CURRENT_PROJECT_STEP,
        "task": "D - Baseline Model Configuration",
        "configuration_status": (
            "INITIAL_FIXED_BASELINE_CONFIGURATION"
        ),
        "model_order": list(MODEL_ORDER),
    }

    expected_sections = {
        "classification_task",
        "environment",
        "data_policy",
        "models",
        "model_selection_policy",
        "evaluation_guidance",
        "current_step_restrictions",
        "limitations",
    }

    if set(config) != set(expected_metadata) | expected_sections:
        raise BaselineConfigurationError(
            "Unexpected or missing top-level configuration fields."
        )

    validate_expected_values(
        config,
        expected_metadata,
        "configuration",
        exact_keys=False,
    )

    validate_expected_values(
        require_section(config, "classification_task"),
        {
            "type": "binary_classification",
            "target_column": TARGET_COLUMN,
            "negative_class": 0,
            "positive_class": 1,
            "feature_count": len(FEATURE_COLUMNS),
        },
        "classification_task",
    )

    validate_expected_values(
        require_section(config, "environment"),
        {
            "python_version": EXPECTED_PYTHON_VERSION,
            "scikit_learn_version": EXPECTED_SKLEARN_VERSION,
            "dependency_lock_file": "uv.lock",
            "global_random_seed": RANDOM_SEED,
        },
        "environment",
    )

    validate_expected_values(
        require_section(config, "data_policy"),
        {
            "training_partition": "train",
            "model_selection_partition": "validation",
            "protected_partition": "test",
            "existing_feature_contract_required": True,
            "existing_partitions_preserved": True,
            "original_class_distribution_preserved": True,
            "additional_standardization_allowed": False,
            "new_preprocessing_allowed": False,
            "resampling_allowed": False,
            "test_access_for_configuration_allowed": False,
        },
        "data_policy",
    )

    models = require_section(config, "models")

    if set(models) != set(MODEL_ORDER):
        raise BaselineConfigurationError(
            "Exactly the three approved baseline models are required."
        )

    for model_name in MODEL_ORDER:

        model_config = require_section(
            models,
            model_name,
            "models",
        )

        validate_model_configuration(
            model_name,
            model_config,
        )

    validate_expected_values(
        require_section(config, "model_selection_policy"),
        {
            "initial_hyperparameters_fixed": True,
            "hyperparameters_optimized": False,
            "grid_search_allowed_at_current_step": False,
            "randomized_search_allowed_at_current_step": False,
            "cross_validation_enabled": False,
            "future_selection_partition": "validation",
            "test_used_for_model_selection": False,
            "test_used_for_hyperparameter_tuning": False,
        },
        "model_selection_policy",
    )

    validate_expected_values(
        require_section(config, "evaluation_guidance"),
        {
            "primary_metric": "average_precision",
            "positive_class": 1,
            "accuracy_as_primary_metric_allowed": False,
            "precision_recall_analysis_required": True,
            "probability_calibration_assessment_required": True,
            "weighted_probabilities_assumed_calibrated": False,
            "decision_threshold": None,
            "future_threshold_selection_partition": "validation",
            "evaluation_protocol_defined_in_task_e": True,
        },
        "evaluation_guidance",
    )

    validate_expected_values(
        require_section(config, "current_step_restrictions"),
        EXPECTED_RESTRICTIONS,
        "current_step_restrictions",
    )

    limitations = config.get("limitations")

    if (
        not isinstance(limitations, list)
        or not limitations
        or not all(
            isinstance(item, str) and item.strip()
            for item in limitations
        )
    ):
        raise BaselineConfigurationError(
            "Configuration limitations must be documented."
        )


# ---------------------------------------------------------
# 7. Read and verify the original JSON configuration
# ---------------------------------------------------------

def load_baseline_config(
    path: Path = BASELINE_CONFIG_PATH,
) -> dict:

    path = Path(path)

    if not path.is_file():
        raise BaselineConfigurationError(
            f"Configuration file not found: {path.name}"
        )

    try:

        original_sha256 = sha256_file(path)

        if original_sha256 != EXPECTED_BASELINE_CONFIG_SHA256:
            raise BaselineConfigurationError(
                "Baseline configuration SHA-256 mismatch."
            )

        with path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:

            config = json.load(
                file,
                object_pairs_hook=reject_duplicate_json_keys,
            )

    except (OSError, json.JSONDecodeError) as error:

        raise BaselineConfigurationError(
            "Unable to read baseline configuration."
        ) from error

    validate_baseline_configuration(config)

    if sha256_file(path) != original_sha256:
        raise BaselineConfigurationError(
            "Configuration changed during validation."
        )

    return config


# ---------------------------------------------------------
# 8. Verify that estimators remain unfitted
# ---------------------------------------------------------

def validate_unfitted_estimator(
    estimator: BaseEstimator,
) -> None:

    try:

        check_is_fitted(estimator)

    except NotFittedError:

        return

    raise BaselineConfigurationError(
        "A fitted estimator is not authorized in Step 5.1.1."
    )


# ---------------------------------------------------------
# 9. Construct approved baseline estimators
# ---------------------------------------------------------

def build_baseline_estimators() -> dict[str, BaseEstimator]:

    config = load_baseline_config()

    validate_runtime_environment()

    load_access_policy()

    load_imbalance_config()

    require_partition_access(
        "train",
        purpose="development_loading",
    )

    weight_result = compute_training_class_weights()

    validate_class_weight_result(weight_result)

    class_weights = weight_result.class_weights

    estimators = {}

    for model_name in MODEL_ORDER:

        model_config = config["models"][model_name]

        parameters = deepcopy(
            model_config["parameters"]
        )

        if model_name in WEIGHTED_MODELS:

            parameters["class_weight"] = dict(
                class_weights
            )

        estimator_class = ESTIMATOR_CLASSES[model_name]

        estimator = estimator_class(**parameters)

        actual_parameters = estimator.get_params(
            deep=False
        )

        for key, expected in parameters.items():

            require_value(
                actual_parameters,
                key,
                expected,
                model_name,
            )

        validate_unfitted_estimator(estimator)

        estimators[model_name] = estimator

    if tuple(estimators) != MODEL_ORDER:
        raise BaselineConfigurationError(
            "Unexpected baseline estimator order."
        )

    if sha256_file(BASELINE_CONFIG_PATH) != (
        EXPECTED_BASELINE_CONFIG_SHA256
    ):
        raise BaselineConfigurationError(
            "Configuration changed during construction."
        )

    return estimators


# ---------------------------------------------------------
# 10. Machine-readable construction summary
# ---------------------------------------------------------

def baseline_configuration_summary() -> dict:

    config = load_baseline_config()

    environment = validate_runtime_environment()

    estimators = build_baseline_estimators()

    model_summaries = {}

    for model_name, estimator in estimators.items():

        validate_unfitted_estimator(estimator)

        parameters = estimator.get_params(
            deep=False
        )

        configured_parameters = {
            key: parameters[key]
            for key in config["models"][model_name]["parameters"]
        }

        class_weight = parameters.get("class_weight")

        if class_weight is not None:

            class_weight = {
                str(key): value
                for key, value in class_weight.items()
            }

        model_summaries[model_name] = {
            "status": "UNFITTED_ESTIMATOR_CONSTRUCTED",
            "estimator_class": type(estimator).__name__,
            "role": config["models"][model_name]["role"],
            "configured_parameters": configured_parameters,
            "class_weight": class_weight,
            "class_weight_source": (
                "verified_train_class_weights"
                if model_name in WEIGHTED_MODELS
                else None
            ),
            "is_fitted": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "model_evaluation_performed": False,
        }

    return {
        "status": "AI4I_BASELINE_ESTIMATORS_CONSTRUCTED_UNFITTED",
        "configuration_version": CONFIGURATION_VERSION,
        "feature_contract_version": CONTRACT_VERSION,
        "imbalance_strategy_version": STRATEGY_VERSION,
        "dataset": DATASET_NAME,
        "project_step": CURRENT_PROJECT_STEP,
        "configuration_sha256": sha256_file(
            BASELINE_CONFIG_PATH
        ),
        "environment": environment,
        "feature_count": len(FEATURE_COLUMNS),
        "feature_columns": list(FEATURE_COLUMNS),
        "model_count": len(estimators),
        "model_order": list(estimators),
        "models": model_summaries,
        "all_estimators_unfitted": True,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "model_evaluation_performed": False,
        "hyperparameter_tuning_performed": False,
        "threshold_optimization_performed": False,
        "probability_calibration_performed": False,
        "resampling_performed": False,
        "new_preprocessing_performed": False,
        "test_partition_used_for_configuration": False,
        "decision_threshold": None,
        "step_5_1_2_training_authorized": False,
    }
