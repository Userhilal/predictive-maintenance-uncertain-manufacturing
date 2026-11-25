
"""Test development access protection using original AI4I data.

No synthetic observations or source data modification.
"""

import builtins
import io
import os
from pathlib import Path

import pytest

from src.prediction.ai4i.access_policy import (
    AccessPolicyError,
    TestSetAccessError as ProtectedTestAccessError,
    require_partition_access,
)

from src.prediction.ai4i.data_loader import (
    load_partition,
    load_development_data,
)


# Files that must not be opened by the development loader.
PROTECTED_FILES = {
    "ai4i_test_features.csv",
    "ai4i_test_eligible_udi_assignments.csv",
    "ai4i2020.csv",
    "scania_official_train_vehicle_targets.csv",
    "scania_official_validation_vehicle_targets.csv",
    "scania_official_test_vehicle_targets.csv",
}


@pytest.fixture
def protected_file_guard(monkeypatch):
    """Reject attempts to open protected source files."""

    original_builtin_open = builtins.open
    original_io_open = io.open
    original_os_open = os.open

    attempted_accesses = []

    def check_path(file):

        if isinstance(file, (str, bytes, os.PathLike)):

            filename = Path(os.fsdecode(file)).name.lower()

            if filename in PROTECTED_FILES:

                attempted_accesses.append(filename)

                raise AssertionError(
                    f"Protected file access detected: {filename}"
                )

    def guarded_builtin_open(file, *args, **kwargs):

        check_path(file)

        return original_builtin_open(
            file, *args, **kwargs
        )

    def guarded_io_open(file, *args, **kwargs):

        check_path(file)

        return original_io_open(
            file, *args, **kwargs
        )

    def guarded_os_open(file, *args, **kwargs):

        check_path(file)

        return original_os_open(
            file, *args, **kwargs
        )

    monkeypatch.setattr(
        builtins,
        "open",
        guarded_builtin_open,
    )

    monkeypatch.setattr(
        io,
        "open",
        guarded_io_open,
    )

    monkeypatch.setattr(
        os,
        "open",
        guarded_os_open,
    )

    yield attempted_accesses


def test_train_loader_does_not_read_test(
    protected_file_guard,
):
    """Train loading must not open protected source files."""

    train = load_partition("train")

    assert train.X.shape == (6981, 8)
    assert train.y.shape == (6981,)
    assert train.udi.shape == (6981,)

    assert protected_file_guard == []


def test_validation_loader_does_not_read_test(
    protected_file_guard,
):
    """Validation loading must not open protected source files."""

    validation = load_partition("validation")

    assert validation.X.shape == (1497, 8)
    assert validation.y.shape == (1497,)
    assert validation.udi.shape == (1497,)

    assert protected_file_guard == []


def test_development_loader_does_not_read_test(
    protected_file_guard,
):
    """Combined development loading must not read test files."""

    data = load_development_data()

    assert data.train.X.shape == (6981, 8)
    assert data.validation.X.shape == (1497, 8)

    assert not hasattr(data, "test")

    assert not (
        set(data.train.udi)
        & set(data.validation.udi)
    )

    assert protected_file_guard == []


def test_direct_test_access_is_rejected(
    protected_file_guard,
):
    """Direct test requests must fail before opening source data."""

    with pytest.raises(ProtectedTestAccessError):

        load_partition("test")

    assert protected_file_guard == []


def test_premature_final_evaluation_is_rejected(
    protected_file_guard,
):
    """Final evaluation is not authorized at Step 5.1.1."""

    with pytest.raises(AccessPolicyError):

        require_partition_access(
            "test",
            purpose="final_evaluation",
        )

    assert protected_file_guard == []


def test_integrity_audit_permission():
    """Read-only integrity audit permission remains available."""

    require_partition_access(
        "test",
        purpose="integrity_audit",
    )


def test_protected_file_guard_detects_access(
    protected_file_guard,
):
    """Verify that the guard itself detects forbidden attempts."""

    with pytest.raises(
        AssertionError,
        match="Protected file access detected",
    ):

        Path("ai4i_test_features.csv").open("rb")

    assert protected_file_guard == [
        "ai4i_test_features.csv"
    ]
