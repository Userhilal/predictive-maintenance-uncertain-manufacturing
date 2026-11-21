# SCANIA Component X v2 — Executed original-only training-manifest results (2026-11-21)

**Status: ORIGINAL_SCANIA_V2_TRAINING_MANIFEST_CREATED**, reported by the project owner after running `src/preprocessing/build_scania_training_manifest.py` against the original SCANIA Component X version-2 files on their computer.

**Authoritative dataset:** https://researchdata.se/en/catalogue/dataset/2024-34/2. The measurements below come from the actual owner-reported console output and repeated `manifest_report.json`, **not** from generated examples, a fabricated source or model predictions. The original SCANIA CSVs and derived CSV manifest remain local and are not committed to GitHub.

## Observed original-data results

| Measure | Internal fit | Internal holdout | Combined original train |
|---|---:|---:|---:|
| Distinct original vehicles | **18,869** | **4,681** | **23,550** |
| Original readouts with repair within next 48 source time steps | 20,721 | 5,037 | 25,758 |
| Original readouts known to have no recorded repair within 48 steps | 717,274 | 177,026 | 894,300 |
| **UNKNOWN short-censored follow-up (blank binary target)** | **162,292** | **40,102** | **202,394** |
| **All referenced original source readouts** | **900,287** | **222,165** | **1,122,452** |
| Source readouts with known 48-step outcome | 737,995 | 182,063 | 920,058 |

Actual fit/holdout counts are determined solely by the original vehicle identifiers and the published versioned partition salt `scania-v2-vehicle-internal-split-v1`, independent of repair time or outcome. All readouts of the same source vehicle are assigned to one partition. Note that counts of observations are **not independent machines**. Existing validation and test sets are not touched.

## Source-integrity and synthetic-data controls reported by executed script

| Output field | Original-source run value |
|---|---|
| `original_training_vehicles` | `23550` |
| `original_training_readouts_referenced` | `1122452` |
| `prediction_horizon_original_steps` | `48` |
| `original_csv_sha256_matches_owner_audit` | `true` |
| `original_horizon_audit_counts_match` | `true` |
| `source_missing_sensor_cells_confirmed` | `354634` |
| `readouts_with_missing_sensor_confirmed` | `22481` |
| `source_csvs_modified` | `false` |
| `new_sensor_observations_generated` | `false` |
| `new_source_repair_events_generated` | `false` |
| `binary_target_only_derived_from_original_followup` | `true` |
| `unknown_short_censored_has_blank_binary_target` | `true` |
| `source_sensor_values_not_copied` | `true` |
| `model_trained` | `false` |
| `not_a_feature_matrix` | `true` |
| `publisher_file_hashes_verified` | **`false`** |

The manifest contains source readout references and **derived target metadata**; it does not create additional genuine sensor observations or artificial event history. The nullable binary target is derived from actual recorded future repair/censoring data **only after** the original as-of readout has been included. It is categorically **not a predictor feature**.

The 202,394 short-censored readouts are an *unknown outcome* for the binary 48-step task, not healthy/negative cases. Dropping them from binary supervised loss may introduce informative-follow-up selection bias; no claim of unbiased generalization should be made without evaluation.

## Decision and next gates

**PASS for the implemented manifest-building/consistency checks.** The executed report matches every previously measured SCANIA v2 original-source cohort count and original missingness totals. The source-only manifest references 1,122,452 real training readings from 23,550 unique vehicles, using a vehicle-grouped internal fit/holdout partition.

**NOT YET A TRAINED MODEL OR A COMPLETE MODEL INPUT MATRIX.** Before supervised fitting:
1. Define source-only, *past/current-only* predictor features from the real operational CSV (without using target status, repair endpoint, future values, or vehicle ID as a predictor).
2. Fit any imputation, encoding or scaling using internal training-fit vehicles **only**, applying those fitted transformations to internal holdout, official validation and official test. Never change the original source files.
3. Keep multiple observations of a vehicle together for internal validation and report appropriate vehicle-clustered metrics; avoid treating correlated readouts as independent cases.
4. Address train/official-validation observation selection mismatch. The official held-out groups have **original truncated histories** and source five-class labels for the last readout; they do not have exact future repair timestamps.
5. Keep unknown short-censored outcomes excluded from *binary classification loss*, or use a proper censoring-aware survival approach; do not silently label them 0.
6. Publisher-signed or published original file checksums have **not** been independently compared; local hashes do match the previous owner's source audit.
7. Project-wide Kaggle original image provenance and contradictory label review remains open. SCANIA truck histories must not be falsely merged by machine ID with unrelated original Kaggle images or Mendeley AI4I 2020 data.

**Acceptance scope:** SCANIA original-file audit, observation indexing, endpoint timing audit, 48-step observability audit and original-only manifest-building have completed the stated checks. No artificial source data, invented maintenance histories, model training, cost estimates or source synchronization are claimed.

See [source-only manifest policy](scania-training-manifest-policy.md), [real 48-step observability results](scania-horizon48-audit-results-2026-11-21.md) and [Issue #4](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/4).
