
"""Generate the AI4I model input validation report.

Project: Predictive Maintenance in an Uncertain
Manufacturing Process.

Step 5.1.1 - Task B.

Collect actual validation results, environment metadata,
source fingerprints and automated test results.

No model training, prediction, evaluation, resampling
or modification of original data.
"""

import json
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.prediction.ai4i.feature_contract import (
    CONTRACT_VERSION,
    FEATURE_COLUMNS,
    EXPECTED_TOTAL_ROWS,
    EXPECTED_QUARANTINED_ROWS,
    sha256_file,
)

from src.prediction.ai4i.validation import (
    validate_all_ai4i_data,
)

from src.prediction.ai4i.access_policy import (
    POLICY_PATH,
    access_policy_summary,
)

from src.prediction.ai4i.data_loader import (
    load_development_data,
    verify_development_sources,
)


# ============================================================
# 2. REPORT CONFIGURATION
# ============================================================

REPORT_VERSION = "1.0.0"

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "ai4i"
    / "model_input_validation.json"
)

EXPECTED_TEST_COUNT = 20

TEST_FILES = (
    "tests/prediction/test_ai4i_test_protection.py",
    "tests/prediction/test_ai4i_pipeline_integration.py",
)


class ReportGenerationError(RuntimeError):
    """Raised when report validation cannot be completed."""


# ============================================================
# 3. COMMAND EXECUTION
# ============================================================

def run_command(command: list[str]) -> dict:
    """Execute a command and capture its actual output."""

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    return {
        "command": command,
        "return_code": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def require_success(result: dict) -> None:
    """Reject failed verification commands."""

    if result["return_code"] != 0:

        raise ReportGenerationError(
            f"Command failed: {result['command']}\n"
            f"{result['stdout']}\n"
            f"{result['stderr']}"
        )


# ============================================================
# 4. ENVIRONMENT VERIFICATION
# ============================================================

def collect_environment() -> dict:
    """Collect actual runtime and dependency information."""

    lock_check = run_command(
        ["uv", "lock", "--check"]
    )

    require_success(lock_check)

    dependency_check = run_command(
        ["uv", "pip", "check"]
    )

    require_success(dependency_check)

    uv_version = run_command(
        ["uv", "--version"]
    )

    require_success(uv_version)

    packages = {
        name: version(name)
        for name in (
            "pandas",
            "numpy",
            "scikit-learn",
            "pytest",
        )
    }

    return {
        "python_version": platform.python_version(),
        "python_implementation": (
            platform.python_implementation()
        ),
        "operating_system": platform.system(),
        "architecture": platform.machine(),
        "uv_version": uv_version["stdout"],
        "package_versions": packages,
        "uv_lock_check": lock_check,
        "dependency_check": dependency_check,
        "pyproject_sha256": sha256_file(
            PROJECT_ROOT / "pyproject.toml"
        ),
        "uv_lock_sha256": sha256_file(
            PROJECT_ROOT / "uv.lock"
        ),
        "python_version_file_sha256": sha256_file(
            PROJECT_ROOT / ".python-version"
        ),
    }


# ============================================================
# 5. REPOSITORY PROVENANCE
# ============================================================

def collect_repository_metadata() -> dict:
    """Record repository state without changing Git."""

    branch = run_command(
        ["git", "branch", "--show-current"]
    )

    commit = run_command(
        ["git", "rev-parse", "HEAD"]
    )

    status = run_command(
        ["git", "status", "--short"]
    )

    for result in (branch, commit, status):
        require_success(result)

    return {
        "branch": branch["stdout"],
        "head_commit": commit["stdout"],
        "working_tree_clean": (
            status["stdout"] == ""
        ),
        "git_status_short": status["stdout"].splitlines(),
        "git_state_captured_before_report_creation": True,
    }


# ============================================================
# 6. IMPLEMENTATION FINGERPRINTS
# ============================================================

def collect_implementation_fingerprints() -> dict:
    """Record the exact implementation used by this report."""

    files = [
        "src/prediction/__init__.py",
        "src/prediction/ai4i/__init__.py",
        "src/prediction/ai4i/feature_contract.py",
        "src/prediction/ai4i/validation.py",
        "src/prediction/ai4i/access_policy.py",
        "src/prediction/ai4i/data_loader.py",
        "configs/ai4i_test_access_policy.json",
        "scripts/generate_ai4i_validation_report.py",
        *TEST_FILES,
    ]

    return {
        filename: sha256_file(
            PROJECT_ROOT / filename
        )
        for filename in files
    }


# ============================================================
# 7. ACTUAL AUTOMATED TEST EXECUTION
# ============================================================

def run_pipeline_tests() -> dict:
    """Run the actual Task B tests and parse JUnit results."""

    with tempfile.TemporaryDirectory(
        prefix="ai4i_validation_"
    ) as temporary_directory:

        junit_path = (
            Path(temporary_directory)
            / "pytest_results.xml"
        )

        command = [
            sys.executable,
            "-m",
            "pytest",
            *TEST_FILES,
            "-q",
            "--junitxml",
            str(junit_path),
        ]

        result = run_command(command)

        require_success(result)

        if not junit_path.is_file():
            raise ReportGenerationError(
                "Pytest JUnit report was not generated."
            )

        root = ET.parse(junit_path).getroot()

        if root.tag == "testsuite":
            suites = [root]
        else:
            suites = root.findall("testsuite")

        if not suites:
            raise ReportGenerationError(
                "No test suites found in JUnit report."
            )

        totals = {
            key: sum(
                int(suite.get(key, "0"))
                for suite in suites
            )
            for key in (
                "tests",
                "failures",
                "errors",
                "skipped",
            )
        }

        passed = (
            totals["tests"]
            - totals["failures"]
            - totals["errors"]
            - totals["skipped"]
        )

        test_cases = []

        for case in root.iter("testcase"):

            if case.find("failure") is not None:
                case_status = "FAILED"

            elif case.find("error") is not None:
                case_status = "ERROR"

            elif case.find("skipped") is not None:
                case_status = "SKIPPED"

            else:
                case_status = "PASSED"

            test_cases.append({
                "class_name": case.get("classname"),
                "test_name": case.get("name"),
                "status": case_status,
                "duration_seconds": float(
                    case.get("time", "0")
                ),
            })

        if totals["tests"] != EXPECTED_TEST_COUNT:

            raise ReportGenerationError(
                "Unexpected Task B test count: "
                f"{totals['tests']}"
            )

        if passed != EXPECTED_TEST_COUNT:

            raise ReportGenerationError(
                "Not all Task B tests passed."
            )

        if len(test_cases) != totals["tests"]:

            raise ReportGenerationError(
                "Inconsistent JUnit test case count."
            )

        return {
            "status": "PASS",
            "total": totals["tests"],
            "passed": passed,
            "failed": totals["failures"],
            "errors": totals["errors"],
            "skipped": totals["skipped"],
            "duration_seconds": sum(
                float(suite.get("time", "0"))
                for suite in suites
            ),
            "test_cases": test_cases,
            "pytest_stdout": result["stdout"],
            "pytest_stderr": result["stderr"],
            "return_code": result["return_code"],
        }


# ============================================================
# 8. COMPLETE REPORT GENERATION
# ============================================================

def generate_report() -> dict:
    """Generate a report from actual verification results."""

    print("[1/7] Collecting environment information...")

    environment = collect_environment()

    print("[2/7] Collecting repository provenance...")

    repository = collect_repository_metadata()

    implementation_before = (
        collect_implementation_fingerprints()
    )

    print("[3/7] Running independent data integrity audit...")

    audit = validate_all_ai4i_data()

    if (
        audit.get("status")
        != "AI4I_MODEL_INPUT_DATA_VALIDATED"
    ):
        raise ReportGenerationError(
            "Original data audit did not succeed."
        )

    print("[4/7] Verifying access policy and sources...")

    policy = access_policy_summary()

    sources = verify_development_sources()

    print("[5/7] Loading development inputs...")

    development = load_development_data()

    development_summary = development.summary()

    print("[6/7] Running automated pipeline tests...")

    tests = run_pipeline_tests()

    print("[7/7] Rechecking implementation and data integrity...")

    implementation_after = (
        collect_implementation_fingerprints()
    )

    if implementation_before != implementation_after:

        raise ReportGenerationError(
            "Implementation changed during verification."
        )

    final_audit = validate_all_ai4i_data()

    if final_audit != audit:

        raise ReportGenerationError(
            "Data audit results changed during verification."
        )

    if (
        audit["summary"]["eligible_rows"]
        != EXPECTED_TOTAL_ROWS
    ):
        raise ReportGenerationError(
            "Unexpected eligible observation count."
        )

    if (
        audit["summary"]["quarantined_rows"]
        != EXPECTED_QUARANTINED_ROWS
    ):
        raise ReportGenerationError(
            "Unexpected quarantine count."
        )

    return {
        "report_version": REPORT_VERSION,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "status": (
            "AI4I_MODEL_INPUT_PIPELINE_TECHNICALLY_VALIDATED"
        ),

        "project": (
            "Predictive Maintenance in an "
            "Uncertain Manufacturing Process"
        ),

        "project_step": "5.1.1",
        "task": "B - Model Input Pipeline",

        "dataset": {
            "name": "AI4I 2020",
            "scope": (
                "Internal classification on the original "
                "published synthetic benchmark"
            ),
            "future_time_prediction_validated": False,
            "real_industrial_generalization_validated": False,
        },

        "feature_contract": {
            "version": CONTRACT_VERSION,
            "feature_count": len(FEATURE_COLUMNS),
            "approved_features": list(FEATURE_COLUMNS),
        },

        "environment": environment,

        "repository": repository,

        "implementation_sha256": implementation_after,

        "independent_data_audit": audit,

        "development_source_verification": sources,

        "access_policy": policy,

        "development_data": development_summary,

        "automated_tests": tests,

        "integrity_rechecked_after_tests": True,

        "scope_restrictions": {
            "model_training_performed": False,
            "model_prediction_performed": False,
            "model_evaluation_performed": False,
            "hyperparameter_tuning_performed": False,
            "resampling_performed": False,
            "new_preprocessing_performed": False,
            "original_data_modified": False,
            "original_partitions_modified": False,
            "original_labels_modified": False,
            "test_used_for_integrity_audit_only": True,
            "test_available_to_development_loader": False,
            "physical_test_isolation": False,
            "scania_modeling_performed": False,
            "image_modeling_performed": False,
            "rag_implementation_performed": False,
        },

        "approval_status": {
            "task_b_technical_validation": True,
            "stage5_formal_signoff_granted": False,
            "stage6_formal_signoff_granted": False,
            "step_5_1_1_completed": False,
            "step_5_1_2_training_authorized": False,
        },

        "limitations": [
            (
                "AI4I is a published synthetic benchmark, "
                "not longitudinal industrial failure data."
            ),
            (
                "Test protection is application-level "
                "and does not provide physical isolation."
            ),
            (
                "Integrity audits inspect original test "
                "data without model evaluation."
            ),
            (
                "Technical validation does not replace "
                "formal Stage 5 and Stage 6 approval."
            ),
            (
                "Baseline models and evaluation protocol "
                "remain to be defined in later tasks."
            ),
        ],
    }


# ============================================================
# 9. REPORT EXPORT
# ============================================================

def write_report(report: dict) -> Path:
    """Write a new report without overwriting an existing one."""

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with REPORT_PATH.open(
        "x",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

        file.write("\n")

    return REPORT_PATH


# ============================================================
# 10. ENTRY POINT
# ============================================================

def main() -> None:

    if REPORT_PATH.exists():

        raise FileExistsError(
            f"Report already exists: {REPORT_PATH}. "
            "Archive it before generating another report."
        )

    report = generate_report()

    output = write_report(report)

    print("\n" + "=" * 60)

    print(report["status"])

    print(
        "Tests:",
        report["automated_tests"]["passed"],
        "/",
        report["automated_tests"]["total"],
    )

    print(
        "Eligible rows:",
        report["independent_data_audit"]
        ["summary"]["eligible_rows"],
    )

    print(
        "Predictor values checked:",
        report["independent_data_audit"]
        ["summary"]["predictor_values_checked"],
    )

    print("Model training performed: False")

    print("Report:", output)

    print("Report SHA-256:", sha256_file(output))

    print("=" * 60)


if __name__ == "__main__":
    main()
