# SCANIA Component X v2 — Executed source-only train-fit sensor profile (2026-11-21)

**Run status:** `ORIGINAL_SCANIA_TRAIN_FIT_SENSOR_PROFILE_CREATED` from the owner's genuine, locally executed SCANIA v2 profiler.

**Source:** https://researchdata.se/en/catalogue/dataset/2024-34/2 . The owner ran `src/preprocessing/profile_scania_trainfit_sensors.py` against the locally stored, unmodified original training source files and the previous source-only grouped manifest. All values below come from the **actual terminal summary shared by the owner**, not from invented source observations or generated fake sensor values.

## Results from the original-source run

| Validated field | Actual reported value |
|---|---:|
| Original sensor feature columns | **105** |
| Original SCANIA train readouts verified against manifest | **1,122,452** |
| Real train-fit readouts with known 48-step outcome used for feature statistics | **737,995** |
| Real train-fit short-censored unknown readouts excluded from fitted statistics | **162,292** |
| Original train sensor missing-value cells verified | **354,634** |
| Original source SHA-256 matches owner's prior local audit | **true** |
| Missing values imputed | **false** |
| Separate sensor input matrix generated | **false** |
| Model trained | **false** |

The profiler's detailed per-sensor actual means, variances, ranges, missing counts and constant/all-missing flags were saved **locally** in `data/processed/scania_trainfit_sensor_profile.json`. The owner shared **only the compact console summary**, not that full 105-feature JSON. Accordingly, this repository documentation **does not assert any specific sensor's mean, missing count, maximum, constant flag or data distribution**.

The 737,995 statistical-fit readouts are existing source measurements from the internally grouped `train_fit` vehicles with *known* 48-step source-derived outcome. The internal holdout was excluded from fitting. Unknown short-censored source readouts were also excluded. This exclusion helps keep simple binary-label-based feature profiling consistent but **may induce informative-follow-up selection bias** and cannot be called unbiased sensor statistics for all vehicles.

## Quality and leakage controls supported by the executed script

The source-only implementation aligns rows in the original `train_operational_readouts.csv` with the previously validated original training manifest; verifies source vehicle IDs, original time steps, source row numbers, ID-only vehicle partition, outcomes against actual `train_tte.csv` and prior raw-audit file SHA-256; and checks original missingness totals. Source repair/censor endpoint and all outcome or partition fields are excluded from the 105 sensor-feature set. The implementation computes only descriptive numerical statistics of **actual existing nonmissing training-fit values** and never adds fake observations or fills missing sensor cells.

**Limits:** the user-provided terminal summary confirms the run and total counts; an independent line-by-line inspection of the generated `feature_profile` object has **not yet occurred**. Official publisher-side checksum comparison still reports unverified. The source is real **truck-component** time series, not factory process measurements, and has no established per-machine links to the separate original AI4I and Kaggle photo datasets.

## Next focused source review — per-feature anomalies

Use the already generated original-only JSON locally. Report:
1. Source feature names for all **zero-variance** and **all-missing-in-fit** sensors.
2. The top ten genuinely most-missing sensors in the 737,995 train-fit known-outcome readouts.
3. Features with nonfinite/unusable or unexpectedly extreme fit stats if present (do **not** invent thresholds, values or replace any source reading).
4. Whether the 105 source features have valid numeric statistics sufficient to plan **a later model-only transformation**.

After this review, choose a documented, train-fit-only model transformation plan that preserves raw observations and does not use source event endpoints or future measurements as predictors. Do not use official validation/test outcomes to design source features.

## Project status

**PASS for implemented original-source train-fit feature-profiling consistency checks**; no model has been trained, no sensor matrix built and no imputation performed. Additional per-feature review, future leak-safe input transformations, vehicle-grouped evaluation, right-censoring selection bias handling, and the separate Kaggle photo source review remain open.

The permitted source set is still only the three user-provided original datasets. The AI4I original source is synthetic *as published*; do not fabricate additional data or claim SCANIA-Kaggle-AI4I observations refer to the same machine.
