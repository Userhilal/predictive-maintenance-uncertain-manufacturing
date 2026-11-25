
"""Automated verification of the AI4I imbalance strategy.

Step 5.1.1 - Task C.

Positive tests use the original validated AI4I data.
Negative configuration tests use temporary JSON copies.

No synthetic observations, resampling, model training,
prediction, evaluation or original data modification.
"""

import json
import math

from dataclasses import replace

import pytest

from src.prediction.ai4i import imbalance_strategy as strategy

from src.prediction.ai4i.feature_contract import (
    CONTRACT_VERSION,
    EXPECTED_SPLIT_COUNTS,
    sha256_file,
)

from src.prediction.ai4i.imbalance_strategy import (
    STRATEGY_CONFIG_PATH,
    ImbalanceStrategyError,
    compute_training_class_weights,
    load_imbalance_config,
    validate_class_weight_result,
)


# ============================================================
# 1. FIXTURES
# ============================================================

@pytest.fixture
def valid_config():
    """Return a fresh copy of the validated configuration."""

    return load_imbalance_config()


@pytest.fixture(scope="module")
def weight_result():
    """Compute weights from the original verified train data."""

    return compute_training_class_weights()


def write_temporary_config(tmp_path, config):
    """Write a temporary configuration without editing originals."""

    path = tmp_path / "imbalance_config.json"

    path.write_text(
        json.dumps(config, indent=2),
        encoding="utf-8",
    )

    return path


# ============================================================
# 2. POSITIVE CONFIGURATION TESTS
# ============================================================

def test_valid_configuration(valid_config):

    assert valid_config["strategy_version"] == "1.0.0"

    assert (
        valid_config["feature_contract_version"]
        == CONTRACT_VERSION
    )

    assert valid_config["project_step"] == "5.1.1"

    assert (
        valid_config["class_weighting"]["source_partition"]
        == "train"
    )


def test_original_training_distribution(weight_result):

    expected = EXPECTED_SPLIT_COUNTS["train"]

    assert weight_result.total_count == expected["total"]

    assert weight_result.normal_count == expected["normal"]

    assert weight_result.failure_count == expected["failure"]


def test_balanced_class_weight_formula(weight_result):

    n = weight_result.total_count

    expected_normal = (
        n / (2 * weight_result.normal_count)
    )

    expected_failure = (
        n / (2 * weight_result.failure_count)
    )

    assert weight_result.normal_weight == pytest.approx(
        expected_normal,
        rel=1e-12,
    )

    assert weight_result.failure_weight == pytest.approx(
        expected_failure,
        rel=1e-12,
    )


def test_class_weight_dictionary(weight_result):

    weights = weight_result.class_weights

    assert set(weights) == {0, 1}

    assert all(
        type(key) is int
        for key in weights
    )

    assert all(
        math.isfinite(value) and value > 0
        for value in weights.values()
    )

    assert weights[1] > weights[0]


def test_weighted_class_totals(weight_result):

    expected = weight_result.total_count / 2

    assert (
        weight_result.weighted_normal_count
        == pytest.approx(expected, rel=1e-12)
    )

    assert (
        weight_result.weighted_failure_count
        == pytest.approx(expected, rel=1e-12)
    )


def test_weight_ratio_matches_imbalance(weight_result):

    assert weight_result.weight_ratio == pytest.approx(
        weight_result.imbalance_ratio,
        rel=1e-12,
    )


def test_class_weight_reproducibility():

    first = compute_training_class_weights()

    second = compute_training_class_weights()

    assert first == second


def test_train_only_weight_computation(monkeypatch):
    """Observe the actual partition requested by the module."""

    original_loader = strategy.load_partition

    requested_partitions = []

    def guarded_loader(split, *args, **kwargs):

        requested_partitions.append(split)

        assert split == "train", (
            f"Forbidden partition requested: {split}"
        )

        return original_loader(
            split,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        strategy,
        "load_partition",
        guarded_loader,
    )

    result = strategy.compute_training_class_weights()

    assert requested_partitions == ["train"]

    assert result.source_file == "ai4i_train_features.csv"


def test_original_configuration_unchanged():

    before = sha256_file(STRATEGY_CONFIG_PATH)

    load_imbalance_config()

    compute_training_class_weights()

    after = sha256_file(STRATEGY_CONFIG_PATH)

    assert before == after


def test_summary_scope_restrictions(weight_result):

    summary = weight_result.summary()

    assert summary["source_partition"] == "train"

    for key in (
        "validation_labels_used_for_weights",
        "test_labels_used_for_weights",
        "resampling_performed",
        "new_preprocessing_performed",
        "model_training_performed",
        "model_prediction_performed",
        "model_evaluation_performed",
        "industrial_cost_ratio_estimated",
    ):

        assert summary[key] is False


# ============================================================
# 3. NEGATIVE CONFIGURATION TESTS
# ============================================================

@pytest.mark.parametrize(
    "section,key,invalid_value",
    [
        (
            "class_weighting",
            "source_partition",
            "validation",
        ),
        (
            "class_weighting",
            "source_partition",
            "test",
        ),
        (
            "class_weighting",
            "validation_labels_allowed_for_weight_computation",
            True,
        ),
        (
            "class_weighting",
            "test_labels_allowed_for_weight_computation",
            True,
        ),
        (
            "class_weighting",
            "hardcoded_weights_allowed",
            True,
        ),
        (
            "class_weighting",
            "method",
            "unsupported_method",
        ),
        (
            "resampling_policy",
            "smote_allowed",
            True,
        ),
        (
            "resampling_policy",
            "adasyn_allowed",
            True,
        ),
        (
            "resampling_policy",
            "random_oversampling_allowed",
            True,
        ),
        (
            "resampling_policy",
            "random_undersampling_allowed",
            True,
        ),
        (
            "resampling_policy",
            "synthetic_observations_allowed",
            True,
        ),
        (
            "resampling_policy",
            "observation_duplication_allowed",
            True,
        ),
        (
            "resampling_policy",
            "observation_removal_allowed",
            True,
        ),
        (
            "validation_policy",
            "stratified_cross_validation_enabled",
            True,
        ),
        (
            "validation_policy",
            "new_preprocessing_allowed",
            True,
        ),
        (
            "validation_policy",
            "new_partition_generation_allowed",
            True,
        ),
        (
            "validation_policy",
            "test_used_for_model_selection",
            True,
        ),
        (
            "validation_policy",
            "test_used_for_threshold_selection",
            True,
        ),
        (
            "evaluation_guidance",
            "primary_metric",
            "accuracy",
        ),
        (
            "current_step_restrictions",
            "model_training_allowed",
            True,
        ),
        (
            "current_step_restrictions",
            "model_prediction_allowed",
            True,
        ),
        (
            "current_step_restrictions",
            "model_evaluation_allowed",
            True,
        ),
        (
            "current_step_restrictions",
            "hyperparameter_tuning_allowed",
            True,
        ),
        (
            "current_step_restrictions",
            "threshold_optimization_allowed",
            True,
        ),
        (
            "current_step_restrictions",
            "probability_calibration_allowed",
            True,
        ),
        (
            "current_step_restrictions",
            "original_data_modification_allowed",
            True,
        ),
        (
            "classification_task",
            "positive_class",
            True,
        ),
        (
            "resampling_policy",
            "smote_allowed",
            0,
        ),
        (
            "expected_training_distribution",
            "failure",
            232,
        ),
    ],
)
def test_invalid_configuration_rejected(
    tmp_path,
    valid_config,
    section,
    key,
    invalid_value,
):

    valid_config[section][key] = invalid_value

    path = write_temporary_config(
        tmp_path,
        valid_config,
    )

    with pytest.raises(
        ImbalanceStrategyError,
        match=key,
    ):

        load_imbalance_config(path)


def test_missing_required_key_rejected(
    tmp_path,
    valid_config,
):

    del valid_config["class_weighting"]["source_partition"]

    path = write_temporary_config(
        tmp_path,
        valid_config,
    )

    with pytest.raises(
        ImbalanceStrategyError,
        match="source_partition",
    ):

        load_imbalance_config(path)


def test_missing_required_section_rejected(
    tmp_path,
    valid_config,
):

    del valid_config["resampling_policy"]

    path = write_temporary_config(
        tmp_path,
        valid_config,
    )

    with pytest.raises(
        ImbalanceStrategyError,
        match="resampling_policy",
    ):

        load_imbalance_config(path)


def test_malformed_json_rejected(tmp_path):

    path = tmp_path / "malformed.json"

    path.write_text(
        '{"strategy_version": ',
        encoding="utf-8",
    )

    with pytest.raises(ImbalanceStrategyError):

        load_imbalance_config(path)


def test_missing_configuration_file_rejected(tmp_path):

    path = tmp_path / "missing.json"

    with pytest.raises(ImbalanceStrategyError):

        load_imbalance_config(path)


def test_unapproved_model_rejected(
    tmp_path,
    valid_config,
):

    valid_config["model_strategy"]["xgboost"] = {
        "class_weighting_enabled": True,
    }

    path = write_temporary_config(
        tmp_path,
        valid_config,
    )

    with pytest.raises(
        ImbalanceStrategyError,
        match="baseline model strategy",
    ):

        load_imbalance_config(path)


@pytest.mark.parametrize(
    "model,key,invalid_value",
    [
        (
            "dummy_classifier",
            "class_weighting_enabled",
            True,
        ),
        (
            "dummy_classifier",
            "strategy",
            "uniform",
        ),
        (
            "logistic_regression",
            "class_weighting_enabled",
            False,
        ),
        (
            "logistic_regression",
            "additional_sample_weight_allowed",
            True,
        ),
        (
            "random_forest",
            "additional_sample_weight_allowed",
            True,
        ),
        (
            "random_forest",
            "balanced_subsample_enabled",
            True,
        ),
    ],
)
def test_invalid_model_strategy_rejected(
    tmp_path,
    valid_config,
    model,
    key,
    invalid_value,
):

    valid_config["model_strategy"][model][key] = (
        invalid_value
    )

    path = write_temporary_config(
        tmp_path,
        valid_config,
    )

    with pytest.raises(
        ImbalanceStrategyError,
        match=key,
    ):

        load_imbalance_config(path)


# ============================================================
# 4. NEGATIVE WEIGHT RESULT TESTS
# ============================================================

@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("normal_count", 6749),
        ("failure_count", 230),
        ("normal_weight", 0.0),
        ("failure_weight", -1.0),
        ("failure_weight", float("nan")),
        ("failure_weight", float("inf")),
        ("failure_weight", 1.0),
        ("contract_version", "invalid"),
    ],
)
def test_invalid_weight_result_rejected(
    weight_result,
    field,
    invalid_value,
):
    """Corrupt only an in-memory result, not source observations."""

    invalid_result = replace(
        weight_result,
        **{field: invalid_value},
    )

    with pytest.raises(ImbalanceStrategyError):

        validate_class_weight_result(invalid_result)


# ============================================================
# 5. FAIL-BEFORE-DATA-ACCESS TEST
# ============================================================

def test_invalid_config_blocks_data_loading(
    tmp_path,
    valid_config,
    monkeypatch,
):

    valid_config["resampling_policy"]["smote_allowed"] = True

    path = write_temporary_config(
        tmp_path,
        valid_config,
    )

    original_config_loader = strategy.load_imbalance_config

    requested_partitions = []

    def invalid_config_loader():

        return original_config_loader(path)

    def forbidden_data_loader(*args, **kwargs):

        requested_partitions.append(args)

        pytest.fail(
            "Data loading must not occur with invalid config."
        )

    monkeypatch.setattr(
        strategy,
        "load_imbalance_config",
        invalid_config_loader,
    )

    monkeypatch.setattr(
        strategy,
        "load_partition",
        forbidden_data_loader,
    )

    with pytest.raises(
        ImbalanceStrategyError,
        match="smote_allowed",
    ):

        strategy.compute_training_class_weights()

    assert requested_partitions == []
