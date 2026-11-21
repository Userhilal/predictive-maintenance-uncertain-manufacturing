# Stage 6 — Actual AI4I train-only feature-engineering execution (2026-11-21)

**Status: ACTUAL STAGE 6 ORIGINAL-SOURCE AI4I FEATURE GENERATION EXECUTED SUCCESSFULLY; FULL OUTPUT SOURCE/TRANSFORM INTEGRITY REVIEW OPEN.**

The owner merged original Stage 6 implementation PR #49 and executed `src/preprocessing/engineer_stage6_ai4i_features.py` on the actual unchanged, originally published synthetic AI4I 2020 CSV, using the already verified eligible Stage 5 assignment metadata and exact Stage 4 original label eligibility policy. No new source datasets, synthetic observations, fault images, independent pump PDFs, model or feature-training from holdouts were added.

**This is actual owner-local output, not a simulated source execution.** The original Stage 6 report and feature data are local, Git-ignored files that have not been read back for independent post-execution acceptance yet.

## Actual Stage 6 terminal JSON

```json
{
  "status": "STAGE6_AI4I_TRAIN_ONLY_FEATURES_CREATED_REVIEW_REQUIRED",
  "actual_prior_stage5_report_sha256": "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda",
  "ai4i_train_only_fit_rows": 6981,
  "ai4i_eligible_original_rows": 9973,
  "ai4i_disputed_source_udis_excluded": 27,
  "ai4i_derived_feature_count": 8,
  "ai4i_feature_names": [
    "type_H",
    "type_L",
    "type_M",
    "air_temperature_K_train_z",
    "process_temperature_K_train_z",
    "rotational_speed_rpm_train_z",
    "torque_Nm_train_z",
    "tool_wear_min_train_z"
  ],
  "ai4i_partition_rows": {
    "train": 6981,
    "validation": 1497,
    "test": 1495
  },
  "ai4i_target_counts_by_partition": {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49}
  },
  "scania_supervised_feature_matrix_created": false,
  "supervised_image_features_created": false,
  "source_files_or_labels_changed": false,
  "stage6_signed_off": false,
  "full_report": "data\\processed\\stage6_ai4i_features\\stage6_feature_report.json"
}
```

## Initial evidence reconciliation

- **Exact original prior Stage 5 report:** `9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda` — matches the actual owner-verified Stage 5 source partition and quarantine evidence.
- **6,981** original eligible training UDIs used to fit numeric transformations; **9,973** original eligible UDI records across all three unchanged Stage 5 source cohorts.
- Five original numerical source predictors normalized with intended training-only statistics, plus three original Type one-hot indicators = **eight derived predictor fields**. Original global failure target and UDI are *metadata*, and Product ID/five failure-mode flags are forbidden input predictors.
- Exactly **27** originally published binary target/mode-disagreement UDIs remain excluded from every supervised AI4I cohort. Preserved source target distribution remains train **6750/231**, validation **1447/50**, test **1446/49** (negative/positive).
- **SCANIA** original 33,641 vehicle source cohorts are unchanged, and no common supervised feature/target contract has been invented across its original censored training endpoints and five-class validation/test task.
- Original Kaggle **234-photo archive** remains blocked for approved supervised image feature learning and image-model training/evaluation pending actual visual labels and per-photo use rights. No photo bytes were copied, redistributed or sent to an API.
- No modified original source files, new dataset, cross-source machine identity joins or ML model training.

**Limit:** These observations are from the producer's terminal summary. Independent verification of actual feature CSV SHA-256 fingerprints and the correct numeric train-fit parameters remains open, so **Stage 6 has NOT been technically signed off yet**.

## Required read-only post-execution verification

`src/preprocessing/review_stage6_ai4i_features.py` reads only:

1. The **unchanged original** AI4I 2020 CSV from `data/raw/ai4i2020.csv` (SHA-256 checked against the original publisher-synthetic file fingerprint).
2. The **existing Stage 5** source assignment report and seven original-derived manifests (verified by the previously merged read-only Stage 5 code, including exact seeded UDI/source-Type partitioning).
3. The **already generated Stage 6** `stage6_feature_report.json`, three feature CSVs, and `ai4i_train_only_feature_contract.json`.

The verifier must:

- Compare **all four Stage 6 output SHA-256** values against the original Stage 6 local report, report the complete local Stage 6 report fingerprint, and reject unexpected extra/missing required output entries.
- Compare each of the **9,973 derived feature CSV source UDI rows and their original binary labels** against the same original UDI and Stage 5 source assignment **in the exact original partition order**. None of the 27 disputed original source UDIs may occur in any derived feature set.
- **Independently recalculate five numerical training-only means, population standard deviations, min/max values** from the **6,981 original training UDI rows** in the original SHA-approved AI4I CSV, and compare with the feature contract. Verify no feature is missing/constant or nonfinite.
- **Independently recompute all eight derived feature values in all 9,973 rows** against raw original sensor/process measurement bytes and those recomputed **training-only** statistics, and require the three one-hot outputs to match the original Type source category. Validation/test statistics are **never fitted**.
- Reject if any source UDI/target/failure-mode flag appears in the approved predictor header, or if report/contract claims forbidden original-source writes, model training, image features, SCANIA unified supervised task, photo rights or label approval.
- Be **read-only**. No re-engineering, file rewriting, source ZIP reading, new dataset, model fitting or source transfer.

**Run only after merging the read-only verifier PR**, from the existing Windows PowerShell repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/review_stage6_ai4i_features.py --ai4i "data/raw/ai4i2020.csv" --stage5-dir "data/processed/stage5_eligible_splits" --stage6-dir "data/processed/stage6_ai4i_features"
```

**Do NOT rerun** `engineer_stage6_ai4i_features.py` to fix or replace the existing source-derived feature artifacts; the producer is deliberately write-once. Send the actual read-only verifier terminal JSON for the final Stage 6 technical review.

### Stage 6 exit status

- [x] Owner executed genuine AI4I 2020 feature engineering using 6,981 train fit rows, 9,973 eligible UDI rows, 8 approved predictors and no original source modifications.
- [x] All 27 original AI4I disputed label UDIs excluded from source-derived AI4I feature cohorts, as reported by the original actual source-run code.
- [x] No SCANIA cross-task supervised feature matrix or original Kaggle supervised image features created; photo label/rights issue #43 remains open.
- [ ] Recompute actual source-only five numeric train-fit statistics against original 6,981 AI4I source rows and compare the existing saved feature contract.
- [ ] Recompute all eight predictor values for all 9,973 eligible original UDI rows in the three unchanged Stage 5 cohorts; verify their exact source UDI/target alignment and SHA-256.
- [ ] Record **risk-qualified Stage 6 AI4I-only feature engineering technical sign-off**, not fully supervised multimodal dataset readiness. **Stage 7 final data validation has not begun.**

**Current stage:** Stage 6 producer EXECUTED, final source-value read-only review REQUIRED. This source is the **original published synthetic AI4I** and should never be called real measured manufacturing history.
