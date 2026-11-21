# SCANIA v2 — Detailed review of 105 original sensor feature profiles

**Completed (2026-11-21):** The owner successfully executed the source-only 105-sensor review on their existing real SCANIA v2 JSON profile: 105 feature entries checked, 77,263,458 originally observed sensor values and 226,017 missing in the fit-known population (0.291674% missing), zero all-missing/constant or >=1%-missing features, and 95 descriptive extreme-range review flags. See [actual executed results](scania-sensor-quality-results-2026-11-21.md). No new sensor observations, imputation or model training.

**Exclusive source:** [the owner's original Researchdata SCANIA Component X version-2 dataset](https://researchdata.se/en/catalogue/dataset/2024-34/2). The prior [source-only 105-sensor profiler](scania-source-feature-profile-policy.md) created `data/processed/scania_trainfit_sensor_profile.json` on the owner's computer; it has not been added to GitHub. Source data remain unchanged.

## Purpose of this QA step

`src/preprocessing/review_scania_sensor_profile.py` reads **only the existing full JSON profile**. No raw CSV download, no new train/test observations, no synthetic values or repairs, no transformed sensor matrix, no missing-value imputation, and **no model training**.

It verifies the profile's original-data provenance flags and actual measured population:

- 105 distinct original SCANIA sensor features; 737,995 genuine known-outcome training-fit observations per feature.
- 1,122,452 original training readings from 23,550 SCANIA vehicles verified by the existing profiler.
- 162,292 short-censored unknown training-fit outcomes excluded from the original fitted statistics.
- Original training missing-sensor count 354,634 (22,481 source readings with missing sensors); compares subset fit missingness against that genuine source upper bound.
- Every sensor's original observed plus missing count equals the genuine number of known-outcome train-fit observations.
- Per-sensor mean/std/min/max are finite and internally consistent when observed; all-missing and constant flags agree.
- Confirms vehicle ID, source time, target status, repair-endpoint fields and partition metadata were **not included as the 105 model sensor columns**.

## Review produced from actual original observations

The report includes:
- Names of actual sensors **all missing** or **constant** within fit.
- Original sensors with **at least 1% missing values in the fit population** and the 15 most missing sensor names.
- Descriptive extreme-range candidates where a genuine observed min or max lies at least 10 observed standard deviations from the observed train-fit mean (up to 15 reported).

**Both thresholds are for inspection only, not grounds to delete values, assume faults, or impute.** SCANIA sensor definitions are anonymized: an extreme range alone cannot identify a faulty instrument or prove a manufacturing anomaly.

It writes `data/processed/scania_sensor_quality_review.json` locally, with the SHA-256 digest of the full previously created profile JSON, not raw sensor rows. No data is sent to external AI services by the script.

## Run after merging the PR

Use PowerShell from the existing repository root. **Do not rerun the earlier 1.1-million-row sensor profiler**:

```powershell
git pull origin main

py -3.11 src/preprocessing/review_scania_sensor_profile.py --profile "data/processed/scania_trainfit_sensor_profile.json" --output "data/processed/scania_sensor_quality_review.json"
```

The script prints its compact, source-derived report and refuses to overwrite an existing output. Its JSON is ignored by Git.

To read again later:

```powershell
Get-Content "data/processed/scania_sensor_quality_review.json"
```

## What happens after reviewing real measurements

1. Check all-missing or constant original sensors and inspect the highest actual missingness by source feature name.
2. Treat extreme standardized numerical ranges **as inspection candidates**, not proven bad data. Preserve original sensor values.
3. Only then finalize a **model-only** preprocessing approach learned from internal training-fit vehicles and applied unchanged to internal holdout, original validation and original test. No fit of scaling/imputation on held-out data.
4. Preserve the existing original grouped vehicle split and the short-censored unknown targets. Never use repair/end-of-study information as model inputs.
5. Independently published source-file hash comparisons are still **unverified**. This does not certify the unrelated Kaggle machinery fault photos or the original Mendeley AI4I data, which remain independent of real SCANIA vehicle histories.

**Decision:** Detailed 105-sensor quality review is **OPEN** until the actual owner-run report is supplied. No feature-specific profile results, model transformations or model metrics can be claimed yet.
