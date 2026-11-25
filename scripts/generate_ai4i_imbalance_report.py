
"""Generate the AI4I class imbalance strategy report.

Step 5.1.1 - Task C.

The report records actual computations, automated tests,
source integrity checks and methodological restrictions.

No model training, prediction, evaluation, resampling
or new preprocessing is performed.
"""

import json
import platform
import subprocess
import sys
import tempfile

from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from xml.etree import ElementTree


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(PROJECT_ROOT))


from src.prediction.ai4i.feature_contract import (
    CONTRACT_VERSION,
    sha256_file,
)

from src.prediction.ai4i.imbalance_strategy import (
    STRATEGY_VERSION,
    STRATEGY_CONFIG_PATH,
    compute_training_class_weights,
    load_imbalance_config,
    validate_class_weight_result,
)

from src.prediction.ai4i.validation import (
    validate_all_ai4i_data,
)


REPORT_VERSION = "1.0.0"

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "ai4i"
    / "imbalance_strategy_report.json"
)

TASK_B_REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "ai4i"
    / "model_input_validation.json"
)

EXPECTED_TASK_B_REPORT_SHA256 = (
    "f4028571361f9b528ffa39030c25bd9a15"
    "b12294ef4cb4be97ae7c43b07fe821"
)

STRATEGY_TEST_PATH = (
    "tests/prediction/test_ai4i_imbalance_strategy.py"
)

EXPECTED_STRATEGY_TEST_COUNT = 59

EXPECTED_TOTAL_TEST_COUNT = 79


class ReportGenerationError(RuntimeError):
    """Raised when report generation cannot be validated."""


# ============================================================
# 2. ENVIRONMENT AND REPOSITORY PROVENANCE
# ============================================================

def collect_environment() -> dict:

    return {
        "python_version": platform.python_version(),

        "platform": platform.system(),

        "architecture": platform.machine(),

        "package_versions": {
            package: version(package)
            for package in (
                "pandas",
                "numpy",
                "scikit-learn",
                "pytest",
            )
        },

        "uv_lock_sha256": sha256_file(
            PROJECT_ROOT / "uv.lock"
        ),

        "pyproject_sha256": sha256_file(
            PROJECT_ROOT / "pyproject.toml"
        ),
    }


def run_git(*arguments) -> str:

    completed = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    return completed.stdout.strip()


def collect_repository() -> dict:

    status = run_git(
        "status",
        "--porcelain",
        "--untracked-files=all",
    )

    return {
        "branch": run_git(
            "branch",
            "--show-current",
        ),

        "head_commit": run_git(
            "rev-parse",
            "HEAD",
        ),

        "working_tree_clean": not bool(status),

        "working_tree_status": status.splitlines(),

        "provenance_note": (
            "HEAD identifies the base commit. "
            "Local implementation files may not yet "
            "be committed. Their SHA-256 fingerprints "
            "are recorded separately."
        ),
    }


# ============================================================
# 3. IMPLEMENTATION FINGERPRINTS
# ============================================================

def collect_fingerprints() -> dict:

    paths = [
        PROJECT_ROOT / ".python-version",

        PROJECT_ROOT / "pyproject.toml",

        PROJECT_ROOT / "uv.lock",

        PROJECT_ROOT
        / "configs"
        / "ai4i_test_access_policy.json",

        STRATEGY_CONFIG_PATH,

        TASK_B_REPORT_PATH,

        PROJECT_ROOT
        / "scripts"
        / "generate_ai4i_validation_report.py",

        Path(__file__).resolve(),

        PROJECT_ROOT
        / "src"
        / "prediction"
        / "__init__.py",
    ]

    paths.extend(
        sorted(
            (
                PROJECT_ROOT
                / "src"
                / "prediction"
                / "ai4i"
            ).glob("*.py")
        )
    )

    paths.extend(
        sorted(
            (
                PROJECT_ROOT
                / "tests"
                / "prediction"
            ).rglob("*.py")
        )
    )

    return {
        path.relative_to(PROJECT_ROOT).as_posix(): {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }

        for path in paths
    }


# ============================================================
# 4. VERIFY PREVIOUS TASK B REPORT
# ============================================================

def verify_task_b_report() -> dict:

    actual_sha256 = sha256_file(
        TASK_B_REPORT_PATH
    )

    if actual_sha256 != EXPECTED_TASK_B_REPORT_SHA256:

        raise ReportGenerationError(
            "Task B report fingerprint mismatch."
        )

    with TASK_B_REPORT_PATH.open(
        "r",
        encoding="utf-8-sig",
    ) as file:

        report = json.load(file)

    if report.get("status") != (
        "AI4I_MODEL_INPUT_PIPELINE_TECHNICALLY_VALIDATED"
    ):

        raise ReportGenerationError(
            "Task B report is not technically validated."
        )

    approval = report["approval_status"]

    if approval["task_b_technical_validation"] is not True:

        raise ReportGenerationError(
            "Task B technical validation is missing."
        )

    if approval["step_5_1_2_training_authorized"] is not False:

        raise ReportGenerationError(
            "Unexpected training authorization."
        )

    return {
        "status": report["status"],

        "report_path": (
            TASK_B_REPORT_PATH
            .relative_to(PROJECT_ROOT)
            .as_posix()
        ),

        "sha256": actual_sha256,

        "original_report_preserved": True,

        "previous_test_count": (
            report["automated_tests"]["total"]
        ),

        "previous_passed_tests": (
            report["automated_tests"]["passed"]
        ),

        "formal_approval_status": approval,
    }


# ============================================================
# 5. AUTOMATED TEST EXECUTION
# ============================================================

def run_automated_tests(
    test_path: str,
    expected_count: int,
) -> dict:

    with tempfile.TemporaryDirectory() as directory:

        xml_path = (
            Path(directory)
            / "pytest_results.xml"
        )

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                test_path,
                "-q",
                f"--junitxml={xml_path}",
            ],

            cwd=PROJECT_ROOT,

            capture_output=True,

            text=True,

            check=False,
        )

        print(completed.stdout)

        if completed.returncode != 0:

            raise ReportGenerationError(
                "Automated tests failed:\n"
                + completed.stdout
                + completed.stderr
            )

        if not xml_path.is_file():

            raise ReportGenerationError(
                "Missing pytest XML evidence."
            )

        root = ElementTree.parse(
            xml_path
        ).getroot()

        if root.tag == "testsuite":

            suites = [root]

        else:

            suites = root.findall("testsuite")

        if not suites:

            raise ReportGenerationError(
                "No test suites found."
            )

        total = sum(
            int(suite.get("tests", "0"))
            for suite in suites
        )

        failed = sum(
            int(suite.get("failures", "0"))
            for suite in suites
        )

        errors = sum(
            int(suite.get("errors", "0"))
            for suite in suites
        )

        skipped = sum(
            int(suite.get("skipped", "0"))
            for suite in suites
        )

        duration = sum(
            float(suite.get("time", "0"))
            for suite in suites
        )

        passed = total - failed - errors - skipped

        if (
            total != expected_count
            or passed != expected_count
            or failed != 0
            or errors != 0
            or skipped != 0
        ):

            raise ReportGenerationError(
                "Unexpected automated test results."
            )

        return {
            "status": "PASS",

            "test_path": test_path,

            "expected_test_count": expected_count,

            "total": total,

            "passed": passed,

            "failed": failed,

            "errors": errors,

            "skipped": skipped,

            "duration_seconds": duration,

            "pytest_exit_code": completed.returncode,

            "evidence_source": "Actual pytest JUnit XML",
        }


# ============================================================
# 6. INDEPENDENT DATA AUDIT
# ============================================================

def run_data_audit() -> dict:

    audit = validate_all_ai4i_data()

    if audit["status"] != (
        "AI4I_MODEL_INPUT_DATA_VALIDATED"
    ):

        raise ReportGenerationError(
            "Independent data integrity audit failed."
        )

    expected_summary = {
        "eligible_rows": 9973,

        "feature_count": 8,

        "predictor_values_checked": 79784,

        "normal_count": 9643,

        "failure_count": 330,

        "quarantined_rows": 27,
    }

    for key, expected in expected_summary.items():

        if audit["summary"][key] != expected:

            raise ReportGenerationError(
                f"Unexpected data audit result: {key}"
            )

    cross_partition = audit[
        "cross_partition_validation"
    ]

    if cross_partition["status"] != "PASS":

        raise ReportGenerationError(
            "Partition independence validation failed."
        )

    if any(
        count != 0
        for count in cross_partition[
            "partition_overlap_counts"
        ].values()
    ):

        raise ReportGenerationError(
            "Unexpected partition overlap."
        )

    if cross_partition["quarantine_overlap_count"] != 0:

        raise ReportGenerationError(
            "Quarantined observations detected."
        )

    if (
        cross_partition["complete_original_source_coverage"]
        is not True
    ):

        raise ReportGenerationError(
            "Incomplete original source coverage."
        )

    return {
        "status": audit["status"],

        "summary": audit["summary"],

        "cross_partition_validation": cross_partition,

        "stage6_integrity": audit["stage6_integrity"],

        "test_used_for_integrity_audit_only": True,
    }


# ============================================================
# 7. REPORT GENERATION
# ============================================================

def generate_report() -> dict:

    if REPORT_PATH.exists():

        raise FileExistsError(
            f"Report already exists: {REPORT_PATH}"
        )

    print("[1/8] Collecting environment and provenance...")

    environment = collect_environment()

    repository = collect_repository()

    fingerprints_before = collect_fingerprints()

    print("[2/8] Verifying previous Task B report...")

    task_b = verify_task_b_report()

    print("[3/8] Validating imbalance configuration...")

    config = load_imbalance_config()

    print("[4/8] Running independent data integrity audit...")

    audit_before = run_data_audit()

    print("[5/8] Computing train-only class weights...")

    weights = compute_training_class_weights()

    validate_class_weight_result(weights)

    repeated_weights = compute_training_class_weights()

    if weights != repeated_weights:

        raise ReportGenerationError(
            "Class weight computation is not reproducible."
        )

    print("[6/8] Running imbalance strategy tests...")

    strategy_tests = run_automated_tests(
        STRATEGY_TEST_PATH,
        EXPECTED_STRATEGY_TEST_COUNT,
    )

    print("[7/8] Running complete prediction test suite...")

    all_tests = run_automated_tests(
        "tests/prediction/",
        EXPECTED_TOTAL_TEST_COUNT,
    )

    print("[8/8] Rechecking data and implementation integrity...")

    audit_after = run_data_audit()

    if audit_before != audit_after:

        raise ReportGenerationError(
            "Data audit results changed during execution."
        )

    fingerprints_after = collect_fingerprints()

    if fingerprints_before != fingerprints_after:

        raise ReportGenerationError(
            "Implementation fingerprints changed."
        )

    verify_task_b_report()

    if repository != collect_repository():

        raise ReportGenerationError(
            "Repository state changed during execution."
        )

    return {
        "report_version": REPORT_VERSION,

        "status": (
            "AI4I_IMBALANCE_STRATEGY_TECHNICALLY_VALIDATED"
        ),

        "generated_at_utc": (
            datetime.now(timezone.utc).isoformat()
        ),

        "project_step": "5.1.1",

        "task": "C - Class Imbalance Strategy",

        "dataset": "AI4I 2020",

        "strategy_version": STRATEGY_VERSION,

        "feature_contract_version": CONTRACT_VERSION,

        "environment": environment,

        "repository": repository,

        "previous_task_b_validation": task_b,

        "implementation_fingerprints": (
            fingerprints_after
        ),

        "validated_strategy_configuration": config,

        "independent_data_audit": audit_after,

        "training_class_weight_computation": (
            weights.summary()
        ),

        "class_weight_reproducibility": {
            "status": "PASS",

            "repeated_computation_identical": True,
        },

        "automated_tests": {
            "imbalance_strategy_tests": strategy_tests,

            "complete_prediction_suite": all_tests,

            "note": (
                "The complete prediction suite includes "
                "the imbalance strategy tests. "
                "The counts must not be added together."
            ),
        },

        "integrity_verification": {
            "status": "PASS",

            "implementation_fingerprints_unchanged": True,

            "task_b_report_unchanged": True,

            "data_audit_results_unchanged": True,

            "repository_state_unchanged": True,
        },

        "methodological_decisions": {
            "imbalance_handling": (
                "Train-only balanced class weighting"
            ),

            "dummy_classifier": (
                "Unweighted prior baseline"
            ),

            "logistic_regression": (
                "Verified training class weights"
            ),

            "random_forest": (
                "Verified training class weights"
            ),

            "cross_validation_enabled": False,

            "cross_validation_reason": (
                config["validation_policy"][
                    "cross_validation_reason"
                ]
            ),

            "future_model_selection_partition": (
                "validation"
            ),

            "future_threshold_selection_partition": (
                "validation"
            ),

            "future_primary_metric": (
                "average_precision"
            ),

            "weighted_probabilities_assumed_calibrated": (
                False
            ),
        },

        "scope_restrictions": {
            "model_training_performed": False,

            "model_prediction_performed": False,

            "model_evaluation_performed": False,

            "hyperparameter_tuning_performed": False,

            "threshold_optimization_performed": False,

            "probability_calibration_performed": False,

            "resampling_performed": False,

            "new_preprocessing_performed": False,

            "original_data_modified": False,

            "original_partitions_modified": False,

            "original_labels_modified": False,

            "validation_labels_used_for_weights": False,

            "test_labels_used_for_weights": False,

            "test_used_for_integrity_audit_only": True,

            "industrial_cost_ratio_estimated": False,

            "physical_test_isolation": False,

            "scania_modeling_performed": False,

            "image_modeling_performed": False,

            "rag_implementation_performed": False,
        },

        "limitations": [
            *config["limitations"],

            (
                "Configuration validation covers expected "
                "operational fields, but is not an exhaustive "
                "strict JSON schema validation."
            ),

            (
                "Restrictions are enforced at application "
                "level, not by operating system isolation."
            ),

            (
                "Technical validation does not constitute "
                "formal approval of the previous data stages."
            ),

            (
                "No predictive performance has been "
                "measured at this step."
            ),
        ],

        "approval_status": {
            "task_b_technical_validation": True,

            "task_c_technical_validation": True,

            "stage5_formal_signoff_granted": (
                task_b["formal_approval_status"][
                    "stage5_formal_signoff_granted"
                ]
            ),

            "stage6_formal_signoff_granted": (
                task_b["formal_approval_status"][
                    "stage6_formal_signoff_granted"
                ]
            ),

            "step_5_1_1_completed": False,

            "step_5_1_2_training_authorized": False,
        },
    }


# ============================================================
# 8. MAIN ENTRY POINT
# ============================================================

def main() -> None:

    report = generate_report()

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Exclusive creation prevents accidental overwrite.

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

    print("\n" + "=" * 60)

    print(report["status"])

    strategy_tests = report["automated_tests"][
        "imbalance_strategy_tests"
    ]

    all_tests = report["automated_tests"][
        "complete_prediction_suite"
    ]

    print(
        "Strategy tests:",
        strategy_tests["passed"],
        "/",
        strategy_tests["total"],
    )

    print(
        "Complete prediction tests:",
        all_tests["passed"],
        "/",
        all_tests["total"],
    )

    print(
        "Class weights:",
        report["training_class_weight_computation"][
            "class_weights"
        ],
    )

    print(
        "Model training performed:",
        report["scope_restrictions"][
            "model_training_performed"
        ],
    )

    print("Report:", REPORT_PATH)

    print(
        "Report SHA-256:",
        sha256_file(REPORT_PATH),
    )

    print("=" * 60)


if __name__ == "__main__":

    main()
