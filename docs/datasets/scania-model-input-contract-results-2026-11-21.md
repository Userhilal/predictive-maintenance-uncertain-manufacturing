# SCANIA v2 — Actual source-only model-input contract execution (2026-11-21)

**Observed run status:** `ORIGINAL_SCANIA_MODEL_INPUT_CONTRACT_PREPARED`.

**Sole data source for this step:** the owner's original [SCANIA Component X version 2 Researchdata records](https://researchdata.se/en/catalogue/dataset/2024-34/2), represented through the previously executed and reviewed original-data manifest, full 105-feature train-fit profile and source-quality report. The owner executed the merged `src/preprocessing/create_scania_model_input_contract.py` locally and shared its full terminal summary. The underlying JSONs were not uploaded to GitHub, and this report does not claim an independent re-execution on the original CSVs.

## Original-data contract execution: actual results

| Observed field | Value |
|---|---|
| `status` | `ORIGINAL_SCANIA_MODEL_INPUT_CONTRACT_PREPARED` |
| `source_sensor_column_count` | **105** |
| `supervised_fit_known_original_readouts` | **737,995** |
| `fit_unknown_short_censored_masked_from_binary_loss` | **162,292** |
| `internal_holdout_known_original_readouts` | **182,063** |
| `internal_holdout_unknown_short_censored_masked_from_binary_loss` | **40,102** |
| `source_missing_input_policy` | `preserve_missing_as_missing_at_model_runtime` |
| `scale_input_values` | `false` |
| `clip_extreme_input_values` | `false` |
| `impute_missing_values` | `false` |
| `creates_feature_matrix` | `false` |
| `fits_model` | `false` |

The original vehicle-grouped internal training partition contains 737,995 + 162,292 = **900,287 existing observations**. The separate original internal holdout contains 182,063 + 40,102 = **222,165**. Total **1,122,452** original SCANIA training observations; no new source observations are introduced.

The script that produced the status validates the owner's **existing** genuine source-only manifest report, 105-sensor profile and source-quality-review JSON, including profile/review SHA-256 concordance and original source population/missingness totals. Therefore this **passed its implemented metadata/contract checks**; it does not replace direct raw CSV validation, and it does not train or evaluate a predictive model.

**Local generated contract path:** `data/processed/scania_model_input_contract.json`. The contract's complete ordered source sensor names and validation fingerprints are in this local file. The owner shared only the compact printed summary here; no additional per-sensor numeric values are asserted.

## Agreed first baseline input contract

- Keep **105 original SCANIA v2 numeric sensor features** in source order with no scaling, clipping, winsorization, imputation or automatic dropping in the first baseline.
- Represent *already missing* original sensor values as missing in the model's runtime input; **require a learner with native missing-numeric support**. Never present an imputation or derived numeric fill as a genuine recorded measurement.
- Source vehicle IDs, source times, CSV row references, future sensor readings, repair/censor endpoint, derived 48-step label and internal partition metadata must **never** be predictors.
- Preserve actual vehicle-ID-only split: **18,869 training-fit vehicles** and **4,681 internal holdout vehicles**. Repeated readouts per vehicle are dependent, so statistical evaluation must be vehicle-aware.
- The **162,292 training-fit** and **40,102 holdout** originally short-censored readouts remain **UNKNOWN** for the 48-step binary task and are not labeled healthy. Excluding unknowns from binary supervised loss can bias evaluation toward cases with longer observed follow-up. A censoring-aware survival alternative should be evaluated separately.
- Official original validation/test vehicles remain separate; their five-class labels apply to each vehicle's last provided source readout. Never invent precise future event times or join the unrelated Kaggle images/AI4I records by fabricated machine IDs.
- The prior 95 large standardized range flags are **review heuristics only**; no original sensor values have been clipped or removed on their basis.

## What remains before model training and claims of readiness

1. Select and record a versioned native-missing model implementation; check its actual numeric missing-value behavior.
2. Implement a strict source-row loader that reads the **real original 105 sensor cells** corresponding to manifest references, verifies the source hashes/order and keeps target/vehicle-group fields entirely outside feature input.
3. Preserve vehicle-grouped internal evaluation, assess repeated-readout dependence, imbalanced repair outcomes, early-censoring selection bias and official train vs. validation/test truncation mismatch.
4. Compare publisher-supplied source hashes if available from the original Researchdata version; **currently unverified** independently (local raw-data hashes matched only the owner's earlier audit).
5. Review the independent original Kaggle image dataset's provenance/contradictory labels. SCANIA readiness does not certify the complete three-source project.

**Decision:** Source-only **input-contract creation is complete**, and no synthetic data, new source observations, feature matrix, imputation or model training occurred. **Predictive modeling and external evaluation are NOT yet complete.**
