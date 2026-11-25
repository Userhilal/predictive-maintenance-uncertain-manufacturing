
"""Automated verification of the AI4I baseline configuration.

Step 5.1.1 - Task D.

No model training, prediction, evaluation or data modification.
"""

import json
from copy import deepcopy

import pytest

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

from src.prediction.ai4i import baseline_config as bc
from src.prediction.ai4i import imbalance_strategy as strategy

from src.prediction.ai4i.feature_contract import (
    FEATURE_COLUMNS,
    sha256_file,
)


# =========================================================
# 1. Fixtures
# =========================================================

@pytest.fixture
def valid_config():
    return bc.load_baseline_config()


@pytest.fixture
def models():
    return bc.build_baseline_estimators()


# =========================================================
# 2. Positive configuration tests
# =========================================================

def test_configuration_fingerprint():

    assert sha256_file(bc.BASELINE_CONFIG_PATH) == (
        bc.EXPECTED_BASELINE_CONFIG_SHA256
    )


def test_configuration_is_valid(valid_config):

    bc.validate_baseline_configuration(valid_config)


def test_runtime_environment():

    result = bc.validate_runtime_environment()

    assert result["status"] == "PASS"
    assert result["python_version"] == "3.11.9"
    assert result["scikit_learn_version"] == "1.9.1"


def test_model_order(valid_config):

    assert valid_config["model_order"] == [
        "dummy_classifier",
        "logistic_regression",
        "random_forest",
    ]


def test_feature_contract_preserved(valid_config):

    task = valid_config["classification_task"]

    assert task["feature_count"] == len(FEATURE_COLUMNS)
    assert len(FEATURE_COLUMNS) == 8

    assert task["positive_class"] == 1
    assert task["negative_class"] == 0


def test_initial_parameters_are_fixed(valid_config):

    for name in bc.MODEL_ORDER:

        assert (
            valid_config["models"][name]["parameters"]
            == bc.EXPECTED_PARAMETERS[name]
        )


# =========================================================
# 3. Estimator construction tests
# =========================================================

def test_exact_estimator_classes(models):

    assert type(models["dummy_classifier"]) is (
        DummyClassifier
    )

    assert type(models["logistic_regression"]) is (
        LogisticRegression
    )

    assert type(models["random_forest"]) is (
        RandomForestClassifier
    )


def test_estimator_order(models):

    assert tuple(models) == bc.MODEL_ORDER


@pytest.mark.parametrize("name", bc.MODEL_ORDER)
def test_estimator_is_unfitted(models, name):

    with pytest.raises(NotFittedError):

        check_is_fitted(models[name])


@pytest.mark.parametrize("name", bc.MODEL_ORDER)
def test_estimator_parameters(models, name):

    actual = models[name].get_params(deep=False)

    expected = bc.EXPECTED_PARAMETERS[name]

    for key, value in expected.items():

        assert actual[key] == value
        assert type(actual[key]) is type(value)


def test_dummy_has_no_class_weight(models):

    params = models["dummy_classifier"].get_params()

    assert "class_weight" not in params


@pytest.mark.parametrize("name", bc.WEIGHTED_MODELS)
def test_verified_training_weights(models, name):

    expected = (
        strategy.compute_training_class_weights()
        .class_weights
    )

    actual = models[name].get_params()["class_weight"]

    assert actual == expected

    assert set(actual) == {0, 1}


def test_weight_dictionaries_are_independent(models):

    lr_weights = models[
        "logistic_regression"
    ].get_params()["class_weight"]

    rf_weights = models[
        "random_forest"
    ].get_params()["class_weight"]

    assert lr_weights == rf_weights

    assert lr_weights is not rf_weights


def test_repeated_construction_is_reproducible():

    first = bc.build_baseline_estimators()
    second = bc.build_baseline_estimators()

    for name in bc.MODEL_ORDER:

        assert first[name] is not second[name]

        assert (
            first[name].get_params(deep=False)
            == second[name].get_params(deep=False)
        )


# =========================================================
# 4. Negative metadata and policy tests
# =========================================================

@pytest.mark.parametrize(
    "key, invalid_value",
    [
        ("configuration_version", "2.0.0"),
        ("feature_contract_version", "2.0.0"),
        ("imbalance_strategy_version", "2.0.0"),
        ("dataset", "SCANIA"),
        ("project_step", "5.1.2"),
        ("configuration_status", "TRAINED"),
    ],
)
def test_invalid_metadata_rejected(
    valid_config,
    key,
    invalid_value,
):

    config = deepcopy(valid_config)

    config[key] = invalid_value

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


@pytest.mark.parametrize(
    "section, key, invalid_value",
    [
        ("classification_task", "feature_count", 9),
        ("classification_task", "positive_class", 0),
        ("classification_task", "target_column", "TWF"),
        ("environment", "global_random_seed", 99),
        ("data_policy", "training_partition", "test"),
        ("data_policy", "model_selection_partition", "test"),
        ("data_policy", "resampling_allowed", True),
        ("data_policy", "new_preprocessing_allowed", True),
        (
            "data_policy",
            "additional_standardization_allowed",
            True,
        ),
        (
            "data_policy",
            "test_access_for_configuration_allowed",
            True,
        ),
        (
            "model_selection_policy",
            "cross_validation_enabled",
            True,
        ),
        (
            "model_selection_policy",
            "grid_search_allowed_at_current_step",
            True,
        ),
        (
            "model_selection_policy",
            "test_used_for_model_selection",
            True,
        ),
        (
            "model_selection_policy",
            "test_used_for_hyperparameter_tuning",
            True,
        ),
        ("evaluation_guidance", "primary_metric", "accuracy"),
        ("evaluation_guidance", "decision_threshold", 0.5),
        (
            "evaluation_guidance",
            "weighted_probabilities_assumed_calibrated",
            True,
        ),
        (
            "evaluation_guidance",
            "future_threshold_selection_partition",
            "test",
        ),
    ],
)
def test_invalid_policy_rejected(
    valid_config,
    section,
    key,
    invalid_value,
):

    config = deepcopy(valid_config)

    config[section][key] = invalid_value

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


@pytest.mark.parametrize(
    "restriction",
    [
        key
        for key, value in bc.EXPECTED_RESTRICTIONS.items()
        if value is False
    ],
)
def test_forbidden_operation_rejected(
    valid_config,
    restriction,
):

    config = deepcopy(valid_config)

    config["current_step_restrictions"][
        restriction
    ] = True

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


# =========================================================
# 5. Negative model configuration tests
# =========================================================

@pytest.mark.parametrize(
    "name, parameter, invalid_value",
    [
        ("dummy_classifier", "strategy", "uniform"),
        ("dummy_classifier", "random_state", 7),
        ("logistic_regression", "C", 10.0),
        ("logistic_regression", "solver", "liblinear"),
        ("logistic_regression", "max_iter", 10),
        ("logistic_regression", "l1_ratio", 0.5),
        ("random_forest", "n_estimators", 500),
        ("random_forest", "max_depth", None),
        ("random_forest", "min_samples_leaf", 1),
        ("random_forest", "random_state", 7),
        ("random_forest", "n_jobs", -1),
        ("random_forest", "bootstrap", False),
    ],
)
def test_modified_hyperparameter_rejected(
    valid_config,
    name,
    parameter,
    invalid_value,
):

    config = deepcopy(valid_config)

    config["models"][name]["parameters"][
        parameter
    ] = invalid_value

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


@pytest.mark.parametrize(
    "unauthorized_model",
    ["xgboost", "lstm", "svm"],
)
def test_additional_model_rejected(
    valid_config,
    unauthorized_model,
):

    config = deepcopy(valid_config)

    config["models"][unauthorized_model] = {}

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


def test_missing_model_rejected(valid_config):

    config = deepcopy(valid_config)

    del config["models"]["random_forest"]

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


def test_unexpected_parameter_rejected(valid_config):

    config = deepcopy(valid_config)

    config["models"]["random_forest"]["parameters"][
        "unexpected_parameter"
    ] = 100

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


def test_hardcoded_class_weights_rejected(valid_config):

    config = deepcopy(valid_config)

    config["models"]["logistic_regression"]["parameters"][
        "class_weight"
    ] = {0: 1.0, 1: 30.0}

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


@pytest.mark.parametrize("name", bc.WEIGHTED_MODELS)
def test_test_weight_source_rejected(valid_config, name):

    config = deepcopy(valid_config)

    config["models"][name]["class_weight_policy"][
        "source_partition"
    ] = "test"

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


def test_balanced_subsample_rejected(valid_config):

    config = deepcopy(valid_config)

    config["models"]["random_forest"]["class_weight_policy"][
        "balanced_subsample_enabled"
    ] = True

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


def test_external_resampling_rejected(valid_config):

    config = deepcopy(valid_config)

    config["models"]["random_forest"]["bootstrap_policy"][
        "external_dataset_resampling_allowed"
    ] = True

    with pytest.raises(bc.BaselineConfigurationError):

        bc.validate_baseline_configuration(config)


# =========================================================
# 6. Configuration file integrity tests
# =========================================================

def test_missing_configuration_file_rejected(tmp_path):

    path = tmp_path / "missing.json"

    with pytest.raises(bc.BaselineConfigurationError):

        bc.load_baseline_config(path)


def test_modified_configuration_file_rejected(
    valid_config,
    tmp_path,
):

    config = deepcopy(valid_config)

    config["models"]["random_forest"]["parameters"][
        "n_estimators"
    ] = 500

    path = tmp_path / "modified_config.json"

    path.write_text(
        json.dumps(config),
        encoding="utf-8",
    )

    with pytest.raises(
        bc.BaselineConfigurationError,
        match="SHA-256 mismatch",
    ):

        bc.load_baseline_config(path)


def test_duplicate_json_keys_rejected():

    with pytest.raises(bc.BaselineConfigurationError):

        json.loads(
            '{"dataset": "AI4I 2020", "dataset": "SCANIA"}',
            object_pairs_hook=bc.reject_duplicate_json_keys,
        )


def test_configuration_file_preserved():

    before = sha256_file(bc.BASELINE_CONFIG_PATH)

    bc.build_baseline_estimators()

    after = sha256_file(bc.BASELINE_CONFIG_PATH)

    assert before == after


# =========================================================
# 7. No training or prediction execution
# =========================================================

def test_construction_never_calls_training_or_prediction(
    monkeypatch,
):

    def forbidden_operation(*args, **kwargs):

        pytest.fail(
            "Training or prediction called during "
            "baseline configuration."
        )

    for estimator_class in bc.ESTIMATOR_CLASSES.values():

        for method in (
            "fit",
            "predict",
            "predict_proba",
            "score",
            "decision_function",
        ):

            if hasattr(estimator_class, method):

                monkeypatch.setattr(
                    estimator_class,
                    method,
                    forbidden_operation,
                )

    models = bc.build_baseline_estimators()

    assert len(models) == 3

    summary = bc.baseline_configuration_summary()

    assert summary["all_estimators_unfitted"] is True


def test_invalid_configuration_blocks_weight_computation(
    monkeypatch,
):

    def invalid_configuration():

        raise bc.BaselineConfigurationError(
            "Invalid configuration."
        )

    def forbidden_weight_computation():

        pytest.fail(
            "Weight computation called after invalid config."
        )

    monkeypatch.setattr(
        bc,
        "load_baseline_config",
        invalid_configuration,
    )

    monkeypatch.setattr(
        bc,
        "compute_training_class_weights",
        forbidden_weight_computation,
    )

    with pytest.raises(bc.BaselineConfigurationError):

        bc.build_baseline_estimators()


def test_weight_computation_requests_only_train(
    monkeypatch,
):

    original_loader = strategy.load_partition

    requested_partitions = []

    def guarded_loader(split, *args, **kwargs):

        requested_partitions.append(split)

        assert split == "train"

        return original_loader(split, *args, **kwargs)

    monkeypatch.setattr(
        strategy,
        "load_partition",
        guarded_loader,
    )

    bc.build_baseline_estimators()

    assert requested_partitions == ["train"]


# =========================================================
# 8. Machine-readable summary tests
# =========================================================

def test_summary_status():

    summary = bc.baseline_configuration_summary()

    assert summary["status"] == (
        "AI4I_BASELINE_ESTIMATORS_CONSTRUCTED_UNFITTED"
    )

    assert summary["model_count"] == 3

    assert summary["feature_count"] == 8

    assert summary["all_estimators_unfitted"] is True

    assert summary["decision_threshold"] is None


def test_summary_scope_restrictions():

    summary = bc.baseline_configuration_summary()

    forbidden_flags = [
        "model_training_performed",
        "model_prediction_performed",
        "model_evaluation_performed",
        "hyperparameter_tuning_performed",
        "threshold_optimization_performed",
        "probability_calibration_performed",
        "resampling_performed",
        "new_preprocessing_performed",
        "test_partition_used_for_configuration",
        "step_5_1_2_training_authorized",
    ]

    for flag in forbidden_flags:

        assert summary[flag] is False


def test_summary_is_json_serializable():

    summary = bc.baseline_configuration_summary()

    serialized = json.dumps(
        summary,
        allow_nan=False,
    )

    restored = json.loads(serialized)

    assert restored == summary
