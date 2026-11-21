# SCANIA Component X v2 — Measured 105-feature quality review (2026-11-21)

**Actual execution status:** `ORIGINAL_SCANIA_105_FEATURE_PROFILE_REVIEW_COMPLETED`.

**Exclusive original source:** https://researchdata.se/en/catalogue/dataset/2024-34/2 . The owner ran the merged source-only `src/preprocessing/review_scania_sensor_profile.py` against the previously generated genuine local `data/processed/scania_trainfit_sensor_profile.json`, and pasted the full terminal JSON response. **These are actual source-derived descriptive results, not synthetic data, new observations or model predictions.**

## Reconciled original-source result

| Returned measured field | Observed result |
|---|---:|
| Source sensor features checked | **105** |
| Original known-outcome train-fit readouts per feature | **737,995** |
| Actual observed train-fit sensor cells | **77,263,458** |
| Actual missing train-fit sensor cells | **226,017** |
| Actual missing fraction among eligible train-fit cells | **0.291674%** |
| Source features entirely missing in fit | **0** |
| Constant-value source features in fit | **0** |
| Source features with at least 1% missingness in fit | **0** |
| Features flagged for large observed standardized min/max distance | **95** |

**Arithmetic:** 77,263,458 observed + 226,017 missing = **77,489,475** actual fit cells = 737,995 real readouts × 105 original sensor columns. This profile uses the known-outcome subset of original `train_fit` vehicles, not all train/test vehicles.

**Original profile SHA-256 locally reported:** `152dcfd174d8b759b26e3781cbd5dedaf03810e9ec0a2c0aec41b690efde478b`. This is a digest of the **owner's local full profile JSON**, not a signature from the SCANIA dataset publisher and not a raw-source hash.

### Source sensor groups with the most missing values

The actual top-15 missingness entries include **all 11 displayed `291_0` through `291_10` columns**, each with **6,211 missing values (0.841605% of eligible fit observations)**, followed by `459_0`, `459_1`, `459_10` and `459_11`, each **5,292 missing values (0.717078%)**. These are measured counts from the owner-run source profile, not reasons to drop features. Shared missing counts among indexed columns may reflect how source fields were recorded, but the report does not establish a mechanism; investigate rather than infer.

### Large numerical-range flags: review only, do not delete source values

The profiler marks **95 of 105 original features** because a source-observed min or max lies at least **10 descriptive standard deviations** from its observed fit mean. These are distribution/scale heuristics, **not identified sensor faults, invalid entries, proof of corrupted data or justified automatic outlier removal**.

Selected actual highest-priority review candidates from the owner-run report:

| Real source feature | Max standardized distance from source fit mean | Original observed min | Original observed max |
|---|---:|---:|---:|
| `459_19` | 194.093 | 0 | 11,765.14630555554 |
| `397_17` | 187.632 | 0 | 1,160,854 |
| `167_0` | 178.421 | 0 | 7,526,574 |
| `459_18` | 171.701 | 0 | 3,875.877027777771 |
| `459_17` | 169.013 | 0 | 34,295.04497222172 |
| `309_0` | 161.615 | 0 | 11,174,358 |
| `291_10` | 148.910 | 0 | 196,706,309 |
| `291_2` | 148.910 | 0 | 11,727,372,293 |

Only these selected candidates and the top 15 were included in the *terminal summary*. The complete 105-feature descriptive profile resides in the owner's local original-profile JSON; a report based only on min/max/mean/std does **not** establish source record corruption or justify deleting any original sensor value.

## Execution error after the completed report: expected overwrite guard

The user ran the same script a second time using the same output path. It raised:

```text
FileExistsError: Refusing to overwrite prior real-source feature review: data\processed\scania_sensor_quality_review.json
```

This is **intentional preservation of the first valid report**. It is not failure of the original successful audit. Do not remove or overwrite the first source-derived report to make the command repeat.

## Acceptance decisions and next modeling gates

- [x] Real original 105-feature profile successfully validated for internal counts, finite descriptive statistics and source/target safeguards.
- [x] All missing and observed fit cells reconcile to the **original 737,995 × 105** population.
- [x] No fully missing or constant original fit feature; no source feature reaches the chosen 1% missingness *review* threshold.
- [x] Report the 95 genuine descriptive extreme-range candidates without dropping or changing source measurements.
- [ ] Before model training, **define and review train-fit-only transformations**, especially for skewed/range-heavy source features. Prefer a simple reversible/auditable model-input approach; any source-value fill/scale must be explicitly marked derived, not portrayed as original measured values.
- [ ] Do not learn imputation, normalization or clipping parameters from original internal holdout/official validation/test. Keep original files unchanged.
- [ ] Preserve the vehicle-grouped internal holdout and explicitly mask the **202,394 short-censored UNKNOWN readouts** from ordinary binary loss, recognizing possible follow-up-selection bias. Consider proper survival/censoring-aware evaluation.
- [ ] Avoid source target, event endpoint, future observation, original vehicle ID and group metadata as model predictors.
- [ ] Original independent publisher-provided SHA-256 comparison remains unverified; the separate original Kaggle image provenance/label audit remains open.

**Decision:** The 105-feature *quality-review step* is **complete for the owner-run report and its implemented checks**. No sensor matrix, artificial measurement, imputation or trained model has been created. These data are from truck fleets and have no verified shared machine IDs with the project's separate original AI4I and Kaggle image sources.
