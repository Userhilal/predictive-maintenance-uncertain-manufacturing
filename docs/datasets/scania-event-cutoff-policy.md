# SCANIA Component X v2 — Repair/censoring and prediction-cutoff safety

**Only source:** https://researchdata.se/en/catalogue/dataset/2024-34/2 and documentation included with that original dataset.

**No artificial observations, dummy CSVs, generated repair events, new labels, simulated equipment histories, replacement sensor values or added datasets.**

## Original-data evidence

The owner successfully audited the nine original files and indexed all 1,516,819 actual readouts belonging to 33,641 vehicles. There are 481,376 originally missing sensor cells, preserved as missing; train/validation/test vehicle identifiers remain separate. See [real SCANIA audit](scania-real-audit-results.md) and [real observation-index execution](scania-observation-index-run-2026-11-21.md).

## Interpretation of actual source targets

- **Training:** train_tte.csv contains an endpoint length_of_study_time_step and an in_study_repair indicator. Event 1 means Component X was repaired at its recorded endpoint. Event 0 means right-censored follow-up without recorded repair by that time; it is **not** proof the vehicle can never fail.
- **Validation/test:** class_label applies to the last *provided* observed readout for each vehicle. The original five classes describe proximity windows: class 0 more than 48 time steps or no repair, class 1 24–48, class 2 12–24, class 3 6–12, class 4 0–6. Exact future repair time is not supplied for validation/test; do not invent it or assume unprovided inclusion conventions at boundary values.
- Time steps are anonymized, not established calendar hours or days. Repairs are observed service events, not guaranteed physical breakdowns.

## The proposed diagnostic — not yet executed on the original CSVs

The new Python script **src/preprocessing/audit_scania_cutoffs.py** verifies the source fingerprints against the real local data audit, then compares **existing** training observation timestamps to the recorded repair or censoring endpoints. It checks the source-only index against real counts and produces aggregate numbers only:

- Recorded readouts strictly before, at, or after the source endpoint, separately for repaired and right-censored vehicles.
- Number of genuine training vehicles with and without a readout strictly before the source endpoint.
- Real source/index integrity results.

**It does not create new samples, attach future targets to readouts, choose model prediction times, impute measurements, or train a model.** Consulting future endpoint dates here is for data-quality QA only; doing so for model as-of cutoff selection would be leakage.

## Commands after merging this script's pull request

Use PowerShell in the existing local project directory:

    git pull origin main
    py -3.11 src/preprocessing/audit_scania_cutoffs.py --audit "data/processed/scania_audit.json" --check-audit-only

Then use only your already-downloaded SCANIA data:

    py -3.11 src/preprocessing/audit_scania_cutoffs.py --audit "data/processed/scania_audit.json" --data-dir "C:\Users\hindh\Documents\2024-34-2\data" --index-dir "data/processed/scania_observation_index" --output "data/processed/scania_cutoff_audit.json"

Inspect:

    Get-Content "data/processed/scania_cutoff_audit.json"

The script refuses changed source files and refuses to overwrite an existing report.

## Required training/evaluation policy after QA

1. Select a future model's **as-of prediction readout by a predeclared, reproducible rule that does not depend on the future repair endpoint or total future readout count**. No artificial prediction timestamps may be introduced.
2. Features must come from time at or before that real readout. The endpoint, repair/censoring flag and validation/test class labels are **targets, not predictors**.
3. Model censored training outcomes as censored, not as guaranteed negative classes for all future periods. Exact RUL is unknown for censored cases.
4. Validation/test original class labels refer to last provided readout in truncated histories; never use their labels to fit feature processing.
5. Multiple actual readouts of one vehicle are correlated. Do not treat them as independently labeled machines.
6. Fit any later model-dependent transformations on training data only. There is currently **no numeric imputation** and no supervised training.
7. Preserve separation from the independent Mendeley AI4I and Kaggle image collections.

**Status:** Proposed source-only cutoff QA script prepared and checked on the genuine uploaded raw-audit report; real full-data cutoff QA execution is still pending on the owner's laptop. Publisher checksum comparison remains unverified.
