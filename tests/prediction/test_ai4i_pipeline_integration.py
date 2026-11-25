
"""Integration tests for the AI4I model input pipeline.

Step 5.1.1 only.

Tests use actual validated AI4I development data.
No synthetic observations, model fitting or evaluation.
Original source files must remain unchanged.
"""

import shutil

import pandas as pd
import pytest

from src.prediction.ai4i.feature_contract import (
    CONTRACT_VERSION,
    STAGE6_DIR,
    SOURCE_CONTRACT_PATH,
    FEATURE_COLUMNS,
    FORBIDDEN_FEATURES,
    ID_COLUMN,
    TARGET_COLUMN,
    SPLIT_FILES,
    sha256_file,
)

from src.prediction.ai4i.validation import (
    STAGE5_DIR,
    STAGE5_ASSIGNMENT_FILES,
    QUARANTINE_FILE,
)

from src.prediction.ai4i.access_policy import (
    POLICY_PATH,
    TestSetAccessError as ProtectedTestAccessError,
)

from src.prediction.ai4i.data_loader import (
    load_partition,
    load_development_data,
    validate_model_inputs,
)


# ============================================================
# 1. SHARED DEVELOPMENT DATA
# ============================================================

@pytest.fixture(scope="module")
def development_data():
    """Load actual verified development partitions."""

    return load_development_data()


# ============================================================
# 2. EXACT FEATURE CONTRACT
# ============================================================

@pytest.mark.parametrize(
    "split",
    ["train", "validation"],
)
def test_exact_feature_contract(
    development_data,
    split,
):
    """Verify exact approved predictors and column order."""

    partition = getattr(
        development_data,
        split,
    )

    assert tuple(partition.X.columns) == FEATURE_COLUMNS

    assert partition.X.shape[1] == 8

    assert partition.contract_version == CONTRACT_VERSION

    assert not (
        set(partition.X.columns)
        & FORBIDDEN_FEATURES
    )


# ============================================================
# 3. TARGET AND IDENTIFIER SEPARATION
# ============================================================

@pytest.mark.parametrize(
    "split",
    ["train", "validation"],
)
def test_target_and_identifier_separation(
    development_data,
    split,
):
    """Ensure targets and identifiers are not predictors."""

    partition = getattr(
        development_data,
        split,
    )

    assert ID_COLUMN not in partition.X.columns
    assert TARGET_COLUMN not in partition.X.columns

    assert partition.y.name == TARGET_COLUMN
    assert partition.udi.name == ID_COLUMN

    assert partition.X.index.equals(
        partition.y.index
    )

    assert partition.X.index.equals(
        partition.udi.index
    )

    validate_model_inputs(partition)


# ============================================================
# 4. ORIGINAL FEATURE VALUES PRESERVED
# ============================================================

@pytest.mark.parametrize(
    "split",
    ["train", "validation"],
)
def test_original_feature_values_preserved(
    development_data,
    split,
):
    """Compare loaded inputs with original Stage 6 values."""

    partition = getattr(
        development_data,
        split,
    )

    source_path = (
        STAGE6_DIR / SPLIT_FILES[split]
    )

    original = pd.read_csv(
        source_path,
        encoding="utf-8-sig",
        on_bad_lines="error",
        skip_blank_lines=False,
        low_memory=False,
    )

    pd.testing.assert_frame_equal(
        partition.X,
        original.loc[:, list(FEATURE_COLUMNS)],
        check_exact=True,
        check_dtype=True,
    )

    pd.testing.assert_series_equal(
        partition.y,
        original[TARGET_COLUMN],
        check_exact=True,
        check_dtype=True,
    )

    pd.testing.assert_series_equal(
        partition.udi,
        original[ID_COLUMN],
        check_exact=True,
        check_dtype=True,
    )


# ============================================================
# 5. DEVELOPMENT PARTITION INDEPENDENCE
# ============================================================

def test_development_partition_independence(
    development_data,
):
    """Verify unique and disjoint development identifiers."""

    train = development_data.train
    validation = development_data.validation

    train_udis = set(train.udi)
    validation_udis = set(validation.udi)

    assert len(train_udis) == 6981
    assert len(validation_udis) == 1497

    assert not train_udis.intersection(
        validation_udis
    )

    assert len(
        train_udis.union(validation_udis)
    ) == 8478


# ============================================================
# 6. ORIGINAL CLASS DISTRIBUTIONS
# ============================================================

def test_original_class_distributions(
    development_data,
):
    """Ensure original class imbalance is preserved."""

    train = development_data.train
    validation = development_data.validation

    assert train.y.value_counts().to_dict() == {
        0: 6750,
        1: 231,
    }

    assert validation.y.value_counts().to_dict() == {
        0: 1447,
        1: 50,
    }


# ============================================================
# 7. DETERMINISTIC DATA LOADING
# ============================================================

def test_reproducible_development_loading(
    development_data,
):
    """Repeated loading must return identical data."""

    repeated = load_development_data()

    for split in ("train", "validation"):

        first = getattr(
            development_data,
            split,
        )

        second = getattr(
            repeated,
            split,
        )

        pd.testing.assert_frame_equal(
            first.X,
            second.X,
            check_exact=True,
        )

        pd.testing.assert_series_equal(
            first.y,
            second.y,
            check_exact=True,
        )

        pd.testing.assert_series_equal(
            first.udi,
            second.udi,
            check_exact=True,
        )

        assert (
            first.source_sha256
            == second.source_sha256
        )

    assert (
        development_data.summary()
        == repeated.summary()
    )


# ============================================================
# 8. IN-MEMORY COPY INDEPENDENCE
# ============================================================

def test_independent_loaded_copies():
    """Separate loads must not share mutable input objects."""

    first = load_partition("train")
    second = load_partition("train")

    assert first.X is not second.X
    assert first.y is not second.y
    assert first.udi is not second.udi

    pd.testing.assert_frame_equal(
        first.X,
        second.X,
        check_exact=True,
    )

    pd.testing.assert_series_equal(
        first.y,
        second.y,
        check_exact=True,
    )

    pd.testing.assert_series_equal(
        first.udi,
        second.udi,
        check_exact=True,
    )


# ============================================================
# 9. ORIGINAL DEVELOPMENT FILES PRESERVED
# ============================================================

def test_original_development_files_unchanged():
    """Compare source fingerprints before and after loading."""

    source_files = [
        POLICY_PATH,
        STAGE5_DIR / "stage5_split_report.json",
        STAGE5_DIR / STAGE5_ASSIGNMENT_FILES["train"],
        STAGE5_DIR / STAGE5_ASSIGNMENT_FILES["validation"],
        STAGE5_DIR / QUARANTINE_FILE,
        STAGE6_DIR / "stage6_feature_report.json",
        SOURCE_CONTRACT_PATH,
        STAGE6_DIR / SPLIT_FILES["train"],
        STAGE6_DIR / SPLIT_FILES["validation"],
    ]

    before = {
        path: sha256_file(path)
        for path in source_files
    }

    load_development_data()

    after = {
        path: sha256_file(path)
        for path in source_files
    }

    assert before == after


# ============================================================
# 10. DEVELOPMENT LOADING WITHOUT TEST FILES
# ============================================================

def test_loading_without_test_files(tmp_path):
    """Load actual development copies without test CSVs."""

    stage5_copy = tmp_path / "stage5"
    stage6_copy = tmp_path / "stage6"

    stage5_copy.mkdir()
    stage6_copy.mkdir()

    # Copy only actual required development files.
    stage5_files = [
        "stage5_split_report.json",
        STAGE5_ASSIGNMENT_FILES["train"],
        STAGE5_ASSIGNMENT_FILES["validation"],
        QUARANTINE_FILE,
    ]

    stage6_files = [
        "stage6_feature_report.json",
        SOURCE_CONTRACT_PATH.name,
        SPLIT_FILES["train"],
        SPLIT_FILES["validation"],
    ]

    for filename in stage5_files:

        shutil.copy2(
            STAGE5_DIR / filename,
            stage5_copy / filename,
        )

    for filename in stage6_files:

        shutil.copy2(
            STAGE6_DIR / filename,
            stage6_copy / filename,
        )

    policy_copy = tmp_path / POLICY_PATH.name

    shutil.copy2(
        POLICY_PATH,
        policy_copy,
    )

    # Confirm protected test CSVs are absent.
    assert not (
        stage5_copy
        / STAGE5_ASSIGNMENT_FILES["test"]
    ).exists()

    assert not (
        stage6_copy
        / SPLIT_FILES["test"]
    ).exists()

    # Load using only the isolated development copies.
    data = load_development_data(
        stage5_dir=stage5_copy,
        stage6_dir=stage6_copy,
        policy_path=policy_copy,
    )

    assert data.train.X.shape == (6981, 8)
    assert data.validation.X.shape == (1497, 8)

    assert not hasattr(data, "test")

    # Confirm test access remains explicitly forbidden.
    with pytest.raises(ProtectedTestAccessError):

        load_partition(
            "test",
            stage5_dir=stage5_copy,
            stage6_dir=stage6_copy,
            policy_path=policy_copy,
        )


# ============================================================
# 11. CURRENT PROJECT SCOPE
# ============================================================

def test_current_step_restrictions(
    development_data,
):
    """Verify declared Step 5.1.1 pipeline scope."""

    summary = development_data.summary()

    assert summary["test_exposed"] is False

    assert (
        summary["test_partition_files_read"]
        is False
    )

    assert (
        summary["complete_source_audit_executed_by_loader"]
        is False
    )

    assert summary["model_training_performed"] is False

    assert summary["model_evaluation_performed"] is False

    assert summary["new_preprocessing_performed"] is False

    assert summary["resampling_performed"] is False
