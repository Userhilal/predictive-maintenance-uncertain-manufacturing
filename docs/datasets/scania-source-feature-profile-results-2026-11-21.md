# SCANIA Component X v2 — Real original sensor-profile execution (2026-11-21)

**Execution status:** `ORIGINAL_SCANIA_TRAIN_FIT_SENSOR_PROFILE_CREATED` (the owner executed `src/preprocessing/profile_scania_trainfit_sensors.py` locally against the **original SCANIA v2 CSVs** and the already validated original-data training manifest).

**Sole source:** [Original Researchdata SCANIA Component X v2](https://researchdata.se/en/catalogue/dataset/2024-34/2). No additional data sources, fabricated sensor observations, artificial fault events or invented dataset joins were used.

## Observed terminal summary from the owner's real-data run

| Key returned by script | Observed value |
|---|---|
| `status` | `ORIGINAL_SCANIA_TRAIN_FIT_SENSOR_PROFILE_CREATED` |
| `original_sensor_feature_columns` | **105** |
| `original_training_readouts_verified` | **1,122,452** |
| `actual_original_readouts_used_to_fit_stats` | **737,995** |
| `actual_train_fit_readouts_with_unknown_outcome_excluded` | **162,292** |
| `original_train_missing_sensor_cells_verified` | **354,634** |
| `source_csv_sha256_matches_owners_raw_audit` | `true` |
| `missing_cells_imputed` | `false` |
| `sensor_matrix_created` | `false` |
| `model_trained` | `false` |

The original 105 sensors were assessed only using **existing** training-fit observations whose 48-step outcome is known from the original repair/censor records. Internal-holdout observations and training-fit short-censored unknown observations are excluded from fitting descriptive sensor statistics, as specified in the source-only profiler's implementation. These figures match earlier owner-run audits and training manifest.

**Local output file:** `data/processed/scania_trainfit_sensor_profile.json`. The source CSVs and this output stay on the owner's computer, not in GitHub.

## What is verified vs. what remains unknown

**PASS (implemented source-only checks):** the profile script completed over the original input data, verified 1,122,452 source readout references, confirmed local file checksums against the prior genuine owner-run raw-data audit, retained the original missing-cell count and used the predetermined 737,995 source-known training-fit observations for observed-value statistics. It did not impute missing values, create a new sensor matrix or train a model.

**Not yet inspected:** the **105 detailed per-feature profiles** (observed mean/std/min/max, observed/missing counts, all-missing/constant flags). The owner supplied only the terminal summary, **not** the full `feature_profile` dictionary. Consequently, no feature-specific numeric statistics, outlier claims, all-missing counts or missing-value transformation decisions are asserted in this document. The full JSON is needed for that technical review.

**Still unverified:** independent publisher-provided source checksum comparison; this workflow matches actual local CSV fingerprints against the earlier owner's audit only, which is not independent provider authentication.

## Next real-data quality gate

1. Inspect the **actual 105 sensor-profile entries**, after the owner shares the full JSON file or prints a compact summary of its features, including per-feature missingness and constant/all-missing flags.
2. Based on genuinely observed feature distributions, define train-fit-only model preprocessing (such as missing-value handling and scaling), explicitly **distinguishing derived model inputs from recorded original measurements**. Never modify source CSVs or pretend imputed cells are observed data.
3. Do not pass the 48-step outcome, original repair endpoint, censoring status, source vehicle ID, or any future observation as an input feature.
4. Keep genuine grouped vehicle partitions intact; treat multiple observations of the same original vehicle as correlated and handle short-censored unknown outcomes honestly.
5. Keep original official validation/test separate; the original test is reserved for final evaluation. Source event times for validation/test are not provided and must not be invented.
6. The separate original Kaggle image-label provenance and rights work remains incomplete, so SCANIA profile success does not certify the entire three-dataset project.

**Decision:** The source-only SCANIA train-fit sensor-profiling execution is **complete for the reported top-level checks**. The detailed feature-review and modeling preprocessing policy remain **open** until the true full profile is inspected. No model training or new source data have been performed.
