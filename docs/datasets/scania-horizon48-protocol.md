# SCANIA Component X v2 — Prediction horizon and censoring rules

**Status (2026-11-21):** The owner ran the 48-step outcome-observability audit on the original real SCANIA v2 training CSVs. Results: 25,758 source readouts with observed repair within 48 steps, 894,300 with observed no repair during 48 steps, and 202,394 **unknown** from short-censored follow-up. See [actual source audit results](scania-horizon48-audit-results-2026-11-21.md). No model training, imputation or generated source data.

## Source and rationale

Only use the owner's [original Researchdata SCANIA Component X version 2](https://researchdata.se/en/catalogue/dataset/2024-34/2). It has real measured truck operational records and original repair/censor outcomes. The original SCANIA publication explains that:

- The training table provides a vehicle's **repair event** or **right-censoring endpoint**. An unobserved repair during follow-up is not a guaranteed never-repair outcome.
- Validation/test each expose a **truncated original history**, with source class 0 (more than 48 operating time steps before repair or no observed repair), class 1 (48–24), class 2 (24–12), class 3 (12–6), class 4 (6–0). Class boundary conventions must be checked against official challenge documentation before a five-class training label is implemented.
- A vehicle's last available validation/test readout is the actual prediction point. The exact future repair timestamp is not provided in validation/test.

This source motivates a **48 original-time-step imminent-repair horizon** for a first binary risk evaluation against the original validation/test labels (0 vs 1–4), while maintaining a future separate censored survival/RUL study. We do not assert that a repair equals a physically observed breakdown or convert anonymized time steps to days or hours.

## Data preparation protocol (before modeling)

### As-of observation candidates

- **Training:** every existing real SCANIA train readout is an *eligible candidate timestamp*, identified by its original `vehicle_id`, `time_step`, and original CSV row. This selection rule refers only to a measurement's existence at the present time, **not** future repair or censoring time, remaining useful life, or the number of subsequent readouts. No new time points or data rows are created by the audit.
- **Validation/test:** the prediction timestamp is the last original supplied observation for each vehicle, as specified by the SCANIA dataset design. Do not use future hidden observations or holdout labels as inputs.
- **Feature cutoff:** any future predictor for candidate time `t` may use that vehicle's original sensor readings up to and including `t`, plus source specification features known by that time. No later readouts or repair/censoring fields are predictors.
- **Non-independent history:** multiple original train readouts of the same vehicle are correlated. Before actual supervised fitting, choose a vehicle-balanced or clustered training protocol (vehicle-held-out internal folds, no mixed-vehicle holdout contamination), not simple rowwise random splitting.
- **Distribution mismatch:** train has complete history to its observed study endpoint; validation/test stop at a source-selected earlier readout. Assess this shift during validation rather than assuming equal readout-position distributions.

### Outcome observability at 48 original time steps

Let `t` be an original readout time strictly before the source endpoint `E`, and `D=E-t` in the dataset's original anonymized time units. Evaluate outcomes **after** the timestamp has been chosen; this step never chooses the timestamp based on `D`.

| Original training source status | Actual follow-up after t | Meaning for repair within 48 |
|---|---|---|
| Observed repair (event=1) | D ≤ 48 | **Known observed repair within horizon** |
| Observed repair (event=1) | D > 48 | **Known no repair within horizon** |
| Right-censored (event=0) | D ≥ 48 | **Known no observed repair during the entire 48-step horizon** |
| Right-censored (event=0) | 0 < D < 48 | **UNKNOWN:** insufficient follow-up; **not** a negative |

Boundary note: D=48 is included for an observed repair and counted as sufficient follow-up for a censored vehicle. This definition is for the proposed **binary** 48-step task, not a claim about exact five-class class-boundary conventions in the source.

**Important:** Known no repair during 48 observed time steps is not a claim that the component never fails or is permanently healthy. The original event/censor status must remain available separately for later survival analysis; **do not impute or invent event times for censored records.**

### Training and evaluation gates

1. Run the following aggregate feasibility audit on genuine original source records and the previously verified one-to-one index, *before any model is trained*.
2. The audit counts existing readouts that fall into the three known/unknown categories above. It does **not** write or manufacture any training observations, assign row-level target data, construct five-class target files, train models, or impute sensors.
3. If some readouts are unknown due to short censoring, **do not force them into the negative class**. Excluding them from a binary-horizon task may cause follow-up-selection bias; document that limitation and consider censoring-aware survival modeling as an alternative.
4. Use **only training vehicles** for internal model fitting and train-only feature transforms, grouped by vehicle; use the official validation vehicles for model selection and uncertainty calibration; reserve the official test vehicles for **one final evaluation**.
5. Report counts and class imbalance, PR-AUC, precision, recall, calibration/Brier score, confusion matrix and business cost only when supported by genuine observed labels and defensible costs. Do not invent actual factory failure-cost values or production-loss measurements.
6. The original unlabeled/Kaggle machinery images and already-published synthetic AI4I dataset are **independent sources**, not matched sensor histories from the same SCANIA vehicles.

## Run the next read-only audit locally (after merging PR)

From the existing GitHub project root in PowerShell:

```powershell
git pull origin main
py -3.11 src/preprocessing/audit_scania_horizon48.py --audit "data/processed/scania_audit.json" --data-dir "C:\Users\hindh\Documents\2024-34-2\data" --index-dir "data/processed/scania_observation_index" --output "data/processed/scania_horizon48_audit.json"
Get-Content "data/processed/scania_horizon48_audit.json"
```

The script checks original `train_tte.csv` and `train_operational_readouts.csv` file fingerprints against the owner's genuine source audit and streams the original readouts in parallel with their existing source-only observation index. It counts 48-step known-repair, known-not-within-horizon, and unknown-right-censored cases. If original row IDs or timestamps no longer match, the script stops; it will not silently accept a fabricated/shifted index. It refuses overwriting an existing report.

**Completed diagnostic:** The actual source-only 48-step audit was executed locally; the genuine counts and their implications are documented in [real 48-step audit results](scania-horizon48-audit-results-2026-11-21.md).

**Provenance limitation:** file fingerprints are compared against the owner's locally generated real source audit, not independently certified against published SCANIA source hashes. The other two original project data sources are unchanged.
