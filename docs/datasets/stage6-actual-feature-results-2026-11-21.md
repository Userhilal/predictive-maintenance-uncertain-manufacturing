# Stage 6 — Actual AI4I train-only feature-engineering execution (2026-11-21)

**FINAL TECHNICAL DISPOSITION (2026-11-21): STAGE 6 ELIGIBLE ORIGINAL-AI4I TRAIN-ONLY FEATURE ENGINEERING COMPLETE AFTER ACTUAL OWNER-RUN NUMERIC AND SHA-256 REVIEW, SUBJECT TO EXPLICIT SCANIA TASK AND IMAGE RIGHTS/LABEL RESTRICTIONS.** The original local Stage 6 producer report correctly retains its prior `stage6_signed_off=false` flag; this subsequent accepted technical review is recorded in GitHub documentation, not by overwriting the original evidence.

The owner merged original Stage 6 implementation PR #49 and executed `src/preprocessing/engineer_stage6_ai4i_features.py` on the actual unchanged, originally published synthetic AI4I 2020 CSV, using the already verified eligible Stage 5 assignment metadata and exact Stage 4 original label eligibility policy. No new source datasets, synthetic observations, fault images, independent pump PDFs, model or feature-training from holdouts were added.

**This is actual owner-local output, not a simulated source execution.** The original Stage 6 report and feature data remain local and Git-ignored; they were subsequently read back by the owner-run original-source verification script and accepted in the final review recorded below.

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

**Post-execution review result:** The owner subsequently ran the merged **read-only** `review_stage6_ai4i_features.py` against the unchanged original AI4I source, previously signed-off Stage 5 output and all existing Stage 6 artifacts. The reviewer passed every source UDI, target, one-hot, train-only statistical parameter and numeric feature check; see the final actual owner-run review and qualified sign-off below. This is an owner-local reproducibility check, not an external ground-truth audit.

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

**Do NOT rerun** `engineer_stage6_ai4i_features.py` or overwrite existing original-source-derived outputs. The owner has already executed the read-only reviewer successfully; its complete actual JSON and final qualified decision appear below.

### Stage 6 exit status

- [x] Owner executed genuine AI4I 2020 feature engineering using 6,981 train fit rows, 9,973 eligible UDI rows, 8 approved predictors and no original source modifications.
- [x] All 27 original AI4I disputed label UDIs excluded from source-derived AI4I feature cohorts, as reported by the original actual source-run code.
- [x] No SCANIA cross-task supervised feature matrix or original Kaggle supervised image features created; photo label/rights issue #43 remains open.
- [x] Owner's genuine read-only verifier recomputed five numeric train-only means, population standard deviations and source ranges against exactly 6,981 original AI4I source training rows, matching the saved feature contract.
- [x] Owner's genuine read-only verifier recomputed all eight predictors for 9,973 original source UDI records (79,784 values), verified exact source UDI/target matches and all four Stage 6 output SHA-256 digests.
- [x] Risk-qualified **Stage 6 AI4I-only train-only feature engineering technical sign-off** recorded below. This does NOT certify independently verified multimodal image labels/rights or SCANIA unified supervised task compatibility. **Stage 7 final data validation has not begun.**

**Final stage decision:** Stage 6 **technically complete for eligible original AI4I tabular train-only features**, with source-value review passed and unresolved SCANIA task and image supervision gates explicitly carried forward. AI4I remains **publisher-synthetic**, not real measured manufacturing history. Stage 7 has not begun.

## Final actual owner-run Stage 6 read-only source/feature review — 2026-11-21

The owner ran the **merged, unchanged reviewer** `src/preprocessing/review_stage6_ai4i_features.py` on the existing local Stage 5 split metadata, the original SHA-checked publisher-synthetic AI4I CSV and the actual generated Stage 6 files, and supplied this genuine terminal result:

```json
{
  "status": "STAGE6_ACTUAL_TRAIN_ONLY_FEATURES_VERIFIED_READ_ONLY",
  "original_stage6_report_sha256": "0250e7063eaae1f551a843cde3f963ba95f16f08cb261bd40b592783c58a3973",
  "prior_stage5_owner_verified_report_sha256": "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda",
  "actual_original_ai4i_source_sha256_verified": true,
  "all_four_stage6_output_file_sha256_verified": true,
  "all_9973_original_source_udi_memberships_and_targets_verified": true,
  "all_27_original_disputed_udis_excluded_and_quarantined": true,
  "numeric_original_features_fit_only_on_6981_training_udis_verified": 5,
  "numeric_train_only_fitted_means_standard_deviations_and_ranges_recomputed": true,
  "all_8_predictor_values_recomputed_from_original_source": true,
  "individual_predictor_values_verified": 79784,
  "per_partition": {
    "train": {
      "original_udis_verified": 6981,
      "original_failure_target_counts": {"0": 6750, "1": 231},
      "all_eight_predictors_recomputed_from_original_source": true
    },
    "validation": {
      "original_udis_verified": 1497,
      "original_failure_target_counts": {"0": 1447, "1": 50},
      "all_eight_predictors_recomputed_from_original_source": true
    },
    "test": {
      "original_udis_verified": 1495,
      "original_failure_target_counts": {"0": 1446, "1": 49},
      "all_eight_predictors_recomputed_from_original_source": true
    }
  },
  "scania_unified_supervised_feature_matrix_created": false,
  "supervised_image_features_created": false,
  "image_class_truth_and_reuse_rights_verified": false,
  "source_data_or_original_labels_modified_by_review": false,
  "feature_stage6_technical_signoff_still_requires_review": true
}
```

The local original Stage 6 report SHA-256 `0250e7063eaae1f551a843cde3f963ba95f16f08cb261bd40b592783c58a3973` is the actual fingerprint returned by the read-only reviewer; the approved original Stage 5 source partition evidence fingerprint remains `9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda`. Neither fingerprint represents an external publisher signature. The reviewer's `feature_stage6_technical_signoff_still_requires_review=true` field records the **pre-decision** reviewer state: the output has now been reviewed and this document is the separate subsequent technical sign-off. Do **not** rewrite either local evidence JSON to change those flags.

### Verified final acceptance criteria

- [x] **All four existing Stage 6 derived output hashes** matched the SHA-256 digests recorded by the actual original feature-engineering report (three original-derived AI4I feature CSVs plus train-only fitted parameter contract JSON). The source AI4I CSV original SHA was independently checked by the same read-only verifier.
- [x] **All 9,973** source-consistent original UDI-to-split memberships, original labels and source Type mappings reconciled exactly against immutable Stage 5 assignment manifests and source AI4I CSV: train **6,981** (0=6750,1=231), validation **1,497** (0=1447,1=50), test **1,495** (0=1446,1=49).
- [x] **Exactly the 27** original AI4I source binary target/mode disagreements remain disjoint from *every* supervised output view and present in the earlier immutable Stage 5 quarantine manifest; the unchanged original source's 10,000 rows were not deleted or relabeled.
- [x] **All five** numerical feature means, population standard deviations and original source ranges were **recomputed from the 6,981 assigned training UDIs only**. Neither held-out validation nor test observations contributed to fitted statistics.
- [x] **All eight predictor values for all 9,973 UDI rows** (exactly **79,784 individual predictor values**) were independently recomputed from original source columns and the rederived train-only transformation parameters and matched the three existing output CSVs. The five numeric z-scores in validation/test used the same unchanged train-only fit parameters; all three fixed Type indicators were checked against original Type.
- [x] Original `UDI` and `Machine failure` are deliberately named **output metadata, NOT predictor columns**. Original Product ID and five failure-mode target flags `TWF/HDF/PWF/OSF/RNF` are not among the eight approved predictor fields; no source target leakage, correction, global fit, scaling from holdouts, imputation, outlier removal, class rebalancing, or synthetic new observations were performed.
- [x] No raw SCANIA sensor source rows or vehicle memberships modified; no compatible **unified** SCANIA supervised feature matrix generated from its original mismatched repair/censor train and five-class val/test target semantics.
- [x] No original Kaggle image bytes read/transformed/shared; no supervised image feature extraction, model training/evaluation or claim that any source image class or individual-photo rights are verified. Original image evidence/rights issue #43 remains **OPEN**.
- [x] No fourth dataset, independent pump manuals, fabricated source features/records, same-machine linked cross-source pairs, trained ML model or Stage 7 data-final-validation work.

### Technical decision and explicit scope

**Stage 6 technical decision:** `STAGE6_ELIGIBLE_AI4I_TRAIN_ONLY_FEATURE_ENGINEERING_COMPLETE_WITH_SCANIA_AND_IMAGE_GATES`.

This is a **source-derived, tabular AI4I-only feature preparation sign-off**, not a certificate that a fully supervised multimodal dataset is prepared. AI4I itself is publisher-synthetic. The original Stage 5 random stratified internal split does not establish chronological, new-machine or real-factory generalization. Source-internal target/mode agreement in 9,973 rows is not independent failure-ground-truth certification.

**SCANIA Component X v2:** keep its actual official vehicle cohorts and raw/metadata evidence; separate source-train right-censored time-to-event endpoints from five-class validation/test original tasks. Do not claim a compatible unified supervised evaluation task or invent target remappings.

**Kaggle image source:** all 234 original fault-photo references are still prohibited from verified-label supervised image features/evaluation and permission-dependent use until visual label verification and original image rights/provenance evidence actually exist. Eight disputed labels remain quarantined and 219 additional source-folder labels are provisional, not independently expert-verified. [Image annotation and rights issue #43](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/43) remains open.

**Next sequential stage after merge:** Stage 7 — **Final Data Validation** may examine the approved original **AI4I** train-only feature artifacts and all original evidence/lineage, and must explicitly report the incomplete SCANIA task contract and image use restrictions. **It must NOT sign off the project as full three-source supervised multimodal-ready.** Stage 8 Model Development has not started. No Stage 7 feature/output generation occurred in this Stage 6 work.
