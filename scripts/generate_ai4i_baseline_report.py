
"""Generate the AI4I baseline configuration validation report.

Step 5.1.1 - Task D.

No model training, prediction, evaluation or original data modification.
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


# =========================================================
# 1. Project initialization
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.prediction.ai4i.feature_contract import (
    CONTRACT_VERSION,
    sha256_file,
)

from src.prediction.ai4i.imbalance_strategy import (
    STRATEGY_VERSION,
    compute_training_class_weights,
)

from src.prediction.ai4i.baseline_config import (
    CONFIGURATION_VERSION,
    MODEL_ORDER,
    BASELINE_CONFIG_PATH,
    load_baseline_config,
    baseline_configuration_summary,
    validate_runtime_environment,
)

from src.prediction.ai4i.validation import (
    validate_all_ai4i_data,
)


# =========================================================
# 2. Report configuration
# =========================================================

REPORT_VERSION = "1.0.0"

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "ai4i"
    / "baseline_configuration_report.json"
)

TASK_B_REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "ai4i"
    / "model_input_validation.json"
)

TASK_C_REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "ai4i"
    / "imbalance_strategy_report.json"
)

BASELINE_TEST_PATH = (
    PROJECT_ROOT
    / "tests"
    / "prediction"
    / "test_ai4i_baseline_config.py"
)

EXPECTED_BASELINE_TEST_COUNT = 88

EXPECTED_TOTAL_TEST_COUNT = 167

EXPECTED_BRANCH = "feat/ai4i-model-input-pipeline"


REFERENCE_FINGERPRINTS = {

    "configs/ai4i_baseline_models.json": (
        "e974bb972168347a436b8b9f1ff6f61735"
        "a650e753d04e9452a3679732a4786e"
    ),

    "src/prediction/ai4i/baseline_config.py": (
        "71403923176b112e45fd5ac0f9ed647a7"
        "5d954a4c27d89f2b9f6a9a420046300"
    ),

    "tests/prediction/test_ai4i_baseline_config.py": (
        "a993ff49a4a5c3711a9850f0701b726dd"
        "6689b60aac97a058768d4e0eff5e368"
    ),

    "reports/ai4i/model_input_validation.json": (
        "f4028571361f9b528ffa39030c25bd9a1"
        "5b12294ef4cb4be97ae7c43b07fe821"
    ),

    "reports/ai4i/imbalance_strategy_report.json": (
        "36be1e836df49662154077ebe381fd46c"
        "558a846fd91deb67aee9147e3982395"
    ),

    "uv.lock": (
        "1271fdf47be8beada4f58deb4e40ad9db"
        "96a1698549292b3856e87b4719bf3de"
    ),
}


class ReportGenerationError(RuntimeError):
    """Raised when report validation fails."""


def require(condition, message):

    if not condition:

        raise ReportGenerationError(message)


# =========================================================
# 3. Environment and repository provenance
# =========================================================

def collect_environment():

    runtime = validate_runtime_environment()

    return {
        **runtime,
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "packages": {
            name: version(name)
            for name in (
                "numpy",
                "pandas",
                "scikit-learn",
                "pytest",
            )
        },
        "pyproject_sha256": sha256_file(
            PROJECT_ROOT / "pyproject.toml"
        ),
    }


def run_git(*arguments):

    result = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )

    return result.stdout.strip()


def collect_repository():

    branch = run_git(
        "branch",
        "--show-current",
    )

    require(
        branch == EXPECTED_BRANCH,
        f"Unexpected Git branch: {branch}",
    )

    status = run_git(
        "status",
        "--porcelain",
        "--untracked-files=all",
    )

    return {
        "branch": branch,
        "head_commit": run_git("rev-parse", "HEAD"),
        "working_tree_clean": not bool(status),
        "working_tree_status": status.splitlines(),
        "provenance_note": (
            "The HEAD commit identifies the repository base. "
            "Uncommitted implementation files are identified "
            "by their individual SHA-256 fingerprints."
        ),
    }


# =========================================================
# 4. File integrity verification
# =========================================================

def verify_reference_fingerprints():

    verified = {}

    for relative_path, expected_hash in (
        REFERENCE_FINGERPRINTS.items()
    ):

        path = PROJECT_ROOT / relative_path

        require(
            path.is_file(),
            f"Required file missing: {relative_path}",
        )

        actual_hash = sha256_file(path)

        require(
            actual_hash == expected_hash,
            f"SHA-256 mismatch: {relative_path}",
        )

        verified[relative_path] = {
            "status": "PASS",
            "sha256": actual_hash,
            "size_bytes": path.stat().st_size,
        }

    return verified


def collect_implementation_fingerprints():

    paths = {
        PROJECT_ROOT / ".python-version",
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "uv.lock",
        PROJECT_ROOT / "src/prediction/__init__.py",
        TASK_B_REPORT_PATH,
        TASK_C_REPORT_PATH,
        Path(__file__).resolve(),
        PROJECT_ROOT
        / "scripts/generate_ai4i_validation_report.py",
        PROJECT_ROOT
        / "scripts/generate_ai4i_imbalance_report.py",
    }

    paths.update(
        (PROJECT_ROOT / "src/prediction/ai4i")
        .rglob("*.py")
    )

    paths.update(
        (PROJECT_ROOT / "tests/prediction")
        .rglob("*.py")
    )

    paths.update(
        (PROJECT_ROOT / "configs")
        .glob("ai4i_*.json")
    )

    fingerprints = {}

    for path in sorted(paths):

        require(
            path.is_file(),
            f"Implementation file missing: {path.name}",
        )

        relative_path = (
            path.relative_to(PROJECT_ROOT).as_posix()
        )

        fingerprints[relative_path] = {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }

    return fingerprints


# =========================================================
# 5. Verify previous task reports
# =========================================================

def read_json(path):

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:

        return json.load(file)


def verify_previous_reports():

    verify_reference_fingerprints()

    task_b = read_json(TASK_B_REPORT_PATH)

    task_c = read_json(TASK_C_REPORT_PATH)

    require(
        task_b["status"] ==
        "AI4I_MODEL_INPUT_PIPELINE_TECHNICALLY_VALIDATED",
        "Task B report status is invalid.",
    )

    require(
        task_c["status"] ==
        "AI4I_IMBALANCE_STRATEGY_TECHNICALLY_VALIDATED",
        "Task C report status is invalid.",
    )

    require(
        task_b["automated_tests"]["passed"] == 20,
        "Unexpected Task B test count.",
    )

    require(
        task_c["automated_tests"]
        ["imbalance_strategy_tests"]["passed"] == 59,
        "Unexpected Task C test count.",
    )

    require(
        task_c["automated_tests"]
        ["complete_prediction_suite"]["passed"] == 79,
        "Unexpected previous cumulative test count.",
    )

    for report in (task_b, task_c):

        approval = report["approval_status"]

        require(
            approval["step_5_1_1_completed"] is False,
            "Unexpected Step 5.1.1 completion status.",
        )

        require(
            approval["step_5_1_2_training_authorized"]
            is False,
            "Unexpected training authorization.",
        )

    approval_c = task_c["approval_status"]

    require(
        approval_c["task_b_technical_validation"] is True,
        "Task B technical validation missing.",
    )

    require(
        approval_c["task_c_technical_validation"] is True,
        "Task C technical validation missing.",
    )

    return {
        "status": "PASS",
        "task_b": {
            "status": task_b["status"],
            "sha256": sha256_file(TASK_B_REPORT_PATH),
            "passed_tests": 20,
            "original_report_preserved": True,
        },
        "task_c": {
            "status": task_c["status"],
            "sha256": sha256_file(TASK_C_REPORT_PATH),
            "passed_tests": 59,
            "cumulative_passed_tests": 79,
            "original_report_preserved": True,
        },
        "previous_approval_status": approval_c,
    }


# =========================================================
# 6. Execute automated tests and collect real results
# =========================================================

def run_automated_tests(test_path, expected_count):

    relative_path = (
        test_path.relative_to(PROJECT_ROOT).as_posix()
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        xml_path = Path(temp_dir) / "pytest_results.xml"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                relative_path,
                "-q",
                f"--junitxml={xml_path}",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr)

        require(
            result.returncode == 0,
            f"Automated tests failed: {relative_path}",
        )

        require(
            xml_path.is_file(),
            "JUnit XML test report was not generated.",
        )

        root = ElementTree.parse(xml_path).getroot()

        if root.tag == "testsuite":

            suites = [root]

        else:

            suites = root.findall("testsuite")

        require(
            bool(suites),
            "No test suites found in JUnit XML.",
        )

        total = sum(
            int(suite.get("tests", 0))
            for suite in suites
        )

        failures = sum(
            int(suite.get("failures", 0))
            for suite in suites
        )

        errors = sum(
            int(suite.get("errors", 0))
            for suite in suites
        )

        skipped = sum(
            int(suite.get("skipped", 0))
            for suite in suites
        )

        duration = sum(
            float(suite.get("time", 0))
            for suite in suites
        )

        passed = total - failures - errors - skipped

        require(
            total == expected_count,
            f"Expected {expected_count} tests, got {total}.",
        )

        require(
            passed == expected_count,
            "Not all required tests passed.",
        )

        return {
            "status": "PASS",
            "test_path": relative_path,
            "expected_test_count": expected_count,
            "total": total,
            "passed": passed,
            "failed": failures,
            "errors": errors,
            "skipped": skipped,
            "duration_seconds": duration,
            "pytest_exit_code": result.returncode,
            "evidence_source": "Executed pytest JUnit XML",
        }


# =========================================================
# 7. Read-only source data audit
# =========================================================

def run_data_audit():

    audit = validate_all_ai4i_data()

    require(
        audit["status"] ==
        "AI4I_MODEL_INPUT_DATA_VALIDATED",
        "Source data audit failed.",
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

        require(
            audit["summary"][key] == expected,
            f"Unexpected data audit value: {key}",
        )

    cross_partition = audit[
        "cross_partition_validation"
    ]

    require(
        cross_partition["status"] == "PASS",
        "Cross-partition validation failed.",
    )

    require(
        all(
            count == 0
            for count in cross_partition[
                "partition_overlap_counts"
            ].values()
        ),
        "Partition overlap detected.",
    )

    require(
        cross_partition["quarantine_overlap_count"] == 0,
        "Quarantine overlap detected.",
    )

    require(
        cross_partition["complete_original_source_coverage"]
        is True,
        "Original source coverage is incomplete.",
    )

    for key in (
        "model_training_performed",
        "model_evaluation_performed",
        "resampling_performed",
        "new_preprocessing_performed",
    ):

        require(
            audit[key] is False,
            f"Unauthorized audit operation: {key}",
        )

    require(
        audit["original_stage6_files_preserved"] is True,
        "Original Stage 6 files were not preserved.",
    )

    require(
        audit["test_used_for_integrity_audit_only"] is True,
        "Unexpected test partition usage.",
    )

    return {
        "status": audit["status"],
        "summary": audit["summary"],
        "stage6_integrity": audit["stage6_integrity"],
        "cross_partition_validation": cross_partition,
        "test_used_for_integrity_audit_only": True,
        "original_stage6_files_preserved": True,
    }


# =========================================================
# 8. Validate baseline construction evidence
# =========================================================

def verify_baseline_construction():

    config = load_baseline_config()

    summary = baseline_configuration_summary()

    weights = compute_training_class_weights()

    require(
        summary["status"] ==
        "AI4I_BASELINE_ESTIMATORS_CONSTRUCTED_UNFITTED",
        "Unexpected baseline construction status.",
    )

    require(
        summary["model_count"] == 3,
        "Unexpected model count.",
    )

    require(
        summary["model_order"] == list(MODEL_ORDER),
        "Unexpected model order.",
    )

    require(
        summary["feature_count"] == 8,
        "Unexpected feature count.",
    )

    require(
        summary["all_estimators_unfitted"] is True,
        "At least one estimator is fitted.",
    )

    require(
        summary["decision_threshold"] is None,
        "A decision threshold was prematurely selected.",
    )

    require(
        summary["models"]["dummy_classifier"]
        ["class_weight"] is None,
        "Dummy Classifier must remain unweighted.",
    )

    expected_weights = {
        str(key): value
        for key, value in weights.class_weights.items()
    }

    for name in (
        "logistic_regression",
        "random_forest",
    ):

        require(
            summary["models"][name]["class_weight"]
            == expected_weights,
            f"Unexpected class weights: {name}",
        )

        require(
            summary["models"][name]["class_weight_source"]
            == "verified_train_class_weights",
            f"Unexpected weight source: {name}",
        )

    forbidden_flags = (
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
    )

    for flag in forbidden_flags:

        require(
            summary[flag] is False,
            f"Unauthorized baseline operation: {flag}",
        )

    for model in summary["models"].values():

        require(
            model["is_fitted"] is False,
            "Fitted estimator detected.",
        )

        for flag in (
            "model_training_performed",
            "model_prediction_performed",
            "model_evaluation_performed",
        ):

            require(
                model[flag] is False,
                f"Unauthorized model operation: {flag}",
            )

    return {
        "status": "PASS",
        "configuration": config,
        "construction_summary": summary,
        "training_class_weights": weights.summary(),
    }


# =========================================================
# 9. Generate complete validation report
# =========================================================

def generate_report():

    require(
        not REPORT_PATH.exists(),
        "Report already exists. Refusing to overwrite it.",
    )

    print("[1/8] Verifying environment and repository...")

    environment = collect_environment()

    repository_before = collect_repository()

    fingerprints_before = (
        collect_implementation_fingerprints()
    )

    reference_before = verify_reference_fingerprints()

    print("[2/8] Verifying previous task reports...")

    previous_reports = verify_previous_reports()

    print("[3/8] Running initial read-only data audit...")

    audit_before = run_data_audit()

    print("[4/8] Verifying unfitted baseline estimators...")

    baseline_before = verify_baseline_construction()

    print("[5/8] Executing 88 baseline configuration tests...")

    baseline_tests = run_automated_tests(
        BASELINE_TEST_PATH,
        EXPECTED_BASELINE_TEST_COUNT,
    )

    print("[6/8] Executing complete prediction test suite...")

    complete_tests = run_automated_tests(
        PROJECT_ROOT / "tests/prediction",
        EXPECTED_TOTAL_TEST_COUNT,
    )

    print("[7/8] Rechecking data and model configuration...")

    audit_after = run_data_audit()

    baseline_after = verify_baseline_construction()

    require(
        audit_before == audit_after,
        "Source data audit results changed.",
    )

    require(
        baseline_before == baseline_after,
        "Baseline construction is not reproducible.",
    )

    print("[8/8] Verifying final file integrity...")

    fingerprints_after = (
        collect_implementation_fingerprints()
    )

    reference_after = verify_reference_fingerprints()

    require(
        fingerprints_before == fingerprints_after,
        "Implementation files changed during validation.",
    )

    require(
        reference_before == reference_after,
        "Reference fingerprints changed.",
    )

    require(
        previous_reports == verify_previous_reports(),
        "Previous task reports changed.",
    )

    require(
        repository_before == collect_repository(),
        "Repository state changed during validation.",
    )

    previous_approval = previous_reports[
        "previous_approval_status"
    ]

    return {
        "report_version": REPORT_VERSION,
        "status": (
            "AI4I_BASELINE_CONFIGURATION_"
            "TECHNICALLY_VALIDATED"
        ),
        "generated_at_utc": (
            datetime.now(timezone.utc).isoformat()
        ),
        "project": (
            "Predictive Maintenance in an "
            "Uncertain Manufacturing Process"
        ),
        "project_step": "5.1.1",
        "task": "D - Baseline Model Configuration",
        "dataset": "AI4I 2020",
        "configuration_version": CONFIGURATION_VERSION,
        "feature_contract_version": CONTRACT_VERSION,
        "imbalance_strategy_version": STRATEGY_VERSION,
        "environment": environment,
        "repository": repository_before,
        "previous_task_validation": previous_reports,
        "reference_fingerprints": reference_before,
        "implementation_fingerprints": fingerprints_before,
        "independent_data_audit": audit_before,
        "baseline_configuration": baseline_before,
        "automated_tests": {
            "baseline_configuration_tests": baseline_tests,
            "complete_prediction_suite": complete_tests,
            "note": (
                "The complete suite includes the baseline "
                "tests. The two counts are not additive."
            ),
        },
        "integrity_verification": {
            "status": "PASS",
            "reference_fingerprints_unchanged": True,
            "implementation_fingerprints_unchanged": True,
            "previous_reports_unchanged": True,
            "data_audit_results_unchanged": True,
            "baseline_construction_reproducible": True,
            "repository_state_unchanged_before_report_write": True,
        },
        "methodological_decisions": {
            "classification_type": "binary_classification",
            "positive_class": 1,
            "baseline_models": list(MODEL_ORDER),
            "dummy_classifier_weighted": False,
            "logistic_regression_weighted": True,
            "random_forest_weighted": True,
            "class_weight_source": "verified_train_labels",
            "initial_hyperparameters_fixed": True,
            "hyperparameters_optimized": False,
            "random_seed": 42,
            "cross_validation_enabled": False,
            "future_model_selection_partition": "validation",
            "future_threshold_selection_partition": "validation",
            "primary_metric": "average_precision",
            "decision_threshold": None,
            "weighted_probabilities_assumed_calibrated": False,
            "evaluation_protocol_pending_task_e": True,
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
            "original_data_modification_performed": False,
            "partition_regeneration_performed": False,
            "test_used_for_model_selection": False,
            "test_used_for_integrity_audit_only": True,
            "trained_model_serialization_performed": False,
            "scania_modeling_performed": False,
            "image_modeling_performed": False,
            "rag_implementation_performed": False,
        },
        "limitations": [
            *baseline_before["configuration"]["limitations"],
            (
                "Automated configuration tests do not "
                "establish predictive performance."
            ),
            (
                "Unfitted estimators retain their standard "
                "scikit-learn fit methods. Restrictions are "
                "enforced at the current pipeline level."
            ),
            (
                "Test partition protection is application-level, "
                "not physical file isolation."
            ),
            (
                "The SCANIA temporal modeling and LSTM "
                "pipeline remain separate from AI4I."
            ),
            (
                "Technical validation is not formal "
                "supervisor approval."
            ),
        ],
        "approval_status": {
            "task_b_technical_validation": True,
            "task_c_technical_validation": True,
            "task_d_technical_validation": True,
            "stage5_formal_signoff_granted": (
                previous_approval[
                    "stage5_formal_signoff_granted"
                ]
            ),
            "stage6_formal_signoff_granted": (
                previous_approval[
                    "stage6_formal_signoff_granted"
                ]
            ),
            "step_5_1_1_completed": False,
            "step_5_1_2_training_authorized": False,
        },
    }


# =========================================================
# 10. Main execution
# =========================================================

def main():

    report = generate_report()

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized_report = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )

    with REPORT_PATH.open(
        "x",
        encoding="utf-8",
    ) as file:

        file.write(serialized_report + "\n")

    print("=" * 65)

    print("STATUS:", report["status"])

    print(
        "BASELINE TESTS:",
        report["automated_tests"]
        ["baseline_configuration_tests"]["passed"],
        "/",
        EXPECTED_BASELINE_TEST_COUNT,
    )

    print(
        "COMPLETE TEST SUITE:",
        report["automated_tests"]
        ["complete_prediction_suite"]["passed"],
        "/",
        EXPECTED_TOTAL_TEST_COUNT,
    )

    print("BASELINE ESTIMATORS: 3")
    print("ALL ESTIMATORS UNFITTED: True")
    print("MODEL TRAINING PERFORMED: False")
    print("MODEL EVALUATION PERFORMED: False")

    print(
        "REPORT:",
        REPORT_PATH.relative_to(PROJECT_ROOT),
    )

    print(
        "REPORT SHA-256:",
        sha256_file(REPORT_PATH),
    )

    print("=" * 65)


if __name__ == "__main__":
    main()
