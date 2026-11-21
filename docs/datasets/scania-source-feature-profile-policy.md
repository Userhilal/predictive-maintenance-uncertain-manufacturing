# SCANIA v2 — Source-only sensor feature profiling

**Status (2026-11-21):** The owner successfully executed the source-only profiler on the original SCANIA v2 CSVs. The terminal summary verifies 105 sensor features, 1,122,452 source readouts, 737,995 known-outcome training-fit readouts used for descriptive statistics and 162,292 unknown training-fit readouts excluded. See [actual execution results](scania-source-feature-profile-results-2026-11-21.md). **Detailed numerical per-feature statistics are not yet independently inspected; the full JSON is still needed.** No imputation or model training.

**Sole source for this step:** [Original SCANIA Component X, version 2](https://researchdata.se/en/catalogue/dataset/2024-34/2). The owner has already run and checked the nine-original-CSV audit, source-only observation index, 48-step outcome-observability audit and ID-grouped training reference manifest. See [the executed training manifest](scania-training-manifest-results-2026-11-21.md).

## What the script does

`src/preprocessing/profile_scania_trainfit_sensors.py` is a **read-only source-feature profile**, not a fitted model and not a new synthetic source dataset.

- Reads genuine `train_operational_readouts.csv` and the existing one-to-one `train_original_observation_manifest.csv` together, checking original vehicle IDs, original timestamps, CSV row numbers and preserved source row count.
- Verifies the two original training CSV SHA-256 fingerprints against the **owner's prior original-file audit**. These are local consistency fingerprints, **not independent publisher hashes**.
- Rechecks manifest 48-step outcome status/nullable target against the genuine original `train_tte.csv` to ensure the source-derived labels have not been silently altered. The true repair/censoring endpoint is **never a sensor predictor**.
- Uses exactly the **105 sensor columns present in the original SCANIA operational CSV**, in their original source order, excluding `vehicle_id`, `time_step`, `in_study_repair`, any endpoint or study duration, the binary label and manifest partition metadata from the sensor feature set.
- Fits descriptive per-feature statistics **only from real train_fit observations with a known 48-step binary target**; the internal holdout and short-censored `UNKNOWN` observations contribute **no values to the fitted statistics**. This follows the already-executed vehicle-ID-only 80/20 partition.
- Reports original nonmissing counts, missing counts, observed means, observed population standard deviations, minima/maxima, and constant/all-missing flags. It does not impute, scale or fabricate any missing value, and does not create a new sensor matrix.
- Checks original training missing-sensor totals against the owner's actual previous manifest report; aborts on shifted index, wrong source, unexpected source row count, altered outcomes, non-finite sensor values in fit, or output overwrite.
- Writes a local **JSON feature profile only**, not 1.1 million new copied source rows, generated images, synthetic machine histories, model predictions or external hosted AI uploads.

## Expected *source counts* established by earlier owner-run audits

These known numbers are input-validation constraints, **not newly observed feature statistics**:

| Source-derived population | Actual existing readouts |
|---|---:|
| Original training readouts | 1,122,452 |
| Fit: known 48-step outcomes | 737,995 |
| Fit: UNKNOWN short-censored outcome, excluded from fitted statistics | 162,292 |
| Internal holdout: known 48-step outcomes, excluded from fit | 182,063 |
| Internal holdout: UNKNOWN, excluded from fit | 40,102 |
| All original training missing sensor cells | 354,634 |
| Real original training readouts with any missing sensor | 22,481 |

**Do not claim the exact feature means or standard deviations until this script actually runs on the owner's 105 original columns.**

## PowerShell commands after the new pull request is merged

From the user's existing repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/profile_scania_trainfit_sensors.py --audit "data/processed/scania_audit.json" --data-dir "C:\Users\hindh\Documents\2024-34-2\data" --manifest-dir "data/processed/scania_training_manifest" --output "data/processed/scania_trainfit_sensor_profile.json"
```

The command displays a concise summary, not all 105 sensor profiles. To display the profile's top-level properties after successful execution:

```powershell
$p = Get-Content "data/processed/scania_trainfit_sensor_profile.json" -Raw | ConvertFrom-Json
$p | Select-Object status, original_sensor_feature_columns, actual_original_readouts_used_to_fit_stats, actual_train_fit_readouts_with_unknown_outcome_excluded, original_train_missing_sensor_cells_verified, missing_cells_imputed, sensor_matrix_created, model_trained
```

The complete `feature_profile` object remains in the JSON on the owner's machine, with values **calculated only from actual original SCANIA readings**. No publisher-approved hash certification is implied.

## Readiness gates before supervised training

1. Verify the user-run report matches original counts, including 105 original sensor columns, 737,995 fit-known source readouts, 162,292 fit-unknown readouts excluded from fitting statistics, and 354,634 original missing sensor cells.
2. Inspect features with zero variance, extreme values or significant missingness. These are source diagnostics only; **do not silently overwrite original missing values or invent replacements**.
3. A future **model-only transformation** may apply numeric scaling/imputation values learned exclusively from fit vehicles and documented clearly as derived model inputs, not real source observations; no such transformation has been applied here.
4. For a first baseline, use the real source readings at or before the selected as-of timestamp. Avoid vehicle identifier and future data as predictors. Keep binary 48-step labels and original endpoint/censoring status out of the input features.
5. Train/holdout metrics must account for repeated readings by the same original vehicle. Short-censored unknown outcomes must not be called known negatives; excluding them from supervised loss introduces possible follow-up-selection bias.
6. The official validation/test source files contain distinct vehicles and source five-class labels for the last original available readout. Feature processing learned on training fit must be applied to held-out inputs unchanged and the official test set reserved for final evaluation.
7. The Mendeley original AI4I 2020 and Kaggle original fault photos are **separate sources**, without verified common SCANIA vehicle IDs. Do not fabricate sensor-to-image matches.
8. The entire project's dataset gate also awaits separate Kaggle image provenance/label review; publisher-side SCANIA SHA-256 verification remains unconfirmed.

**Decision:** This is the next *feature quality and fitting-statistics* gate, not permission to train a model before the actual source-derived report is reviewed.
