# SCANIA Component X v2 — Real 48-step outcome observability results (2026-11-21)

**Observed status:** `ORIGINAL_SCANIA_48STEP_ELIGIBILITY_AUDITED`

**Original source only:** [Researchdata SCANIA Component X, v2](https://researchdata.se/en/catalogue/dataset/2024-34/2). The project owner ran the merged `src/preprocessing/audit_scania_horizon48.py` locally against the genuine original SCANIA training CSVs and source-only observation index, and shared both the stdout and the saved audit JSON. No extra dataset, mock sensor data, invented failure time, fabricated observation, or model training was used.

## Verified output from the real-source execution

| Original training outcomes at each *existing* readout | Source readouts | Percentage of all 1,122,452 original readouts |
|---|---:|---:|
| Observed Component X repair in (0, 48] anonymized steps | **25,758** | **2.30%** |
| No recorded repair during 48 subsequent observed steps | **894,300** | **79.67%** |
| Outcome **unknown**: right-censored with less than 48 further steps | **202,394** | **18.03%** |
| **All original train readouts examined** | **1,122,452** | **100%** |

**Observed outcomes = 25,758 + 894,300 = 920,058 readouts.** Among source readouts with *known* binary-horizon outcome, the positive fraction is **2.80%** (25,758 / 920,058). This counts original observations, **not independent vehicles**. The 202,394 short-censored candidates are **not negative examples**. Discarding them for a simple binary task would itself introduce follow-up selection bias; a fully censoring-aware survival analysis is a separate future choice.

Original vehicle/split facts from actual script result:

- Training vehicles: **23,550**.
- Readouts associated with event=1 vehicles: **105,852**.
- Readouts associated with right-censored event=0 vehicles: **1,016,600**.
- Source/local-audit fingerprint match: `original_file_hashes_match_local_audit: true`.
- Original readouts remain unchanged; no source rows, event records, model training samples, or per-readout target files were created.
- Independent publisher-supplied source hash comparison: **not verified**.

## What was validated

The implemented read-only script checks that original train operation timestamps and vehicle IDs match their earlier one-to-one source observation index row by row; that both original CSV fingerprints match the previous genuine source audit; and that the train vehicle/readout populations match the original downloaded SCANIA v2 counts. It derives **aggregate observability counts** for the 48-step target. Its results are not a trained model and do not constitute a future-proof performance evaluation.

## Concrete training-readiness protocol (to be approved before actual fitting)

1. **Predict at real observation times only.** For training, the candidate universe is each observed `vehicle_id + time_step` entry from the original training file; do **not** generate additional time points. Do not choose timestamps by looking at future repair/censor dates or by counting future readouts.
2. **Keep the source input and outcome distinct.** At a selected observation, predictor features can use only real sensor values measured at/before that time, plus legitimately pre-existing vehicle specifications. Original `length_of_study_time_step`, `in_study_repair`, and validation/test `class_label` are never predictors. A source event/censor outcome may be attached **only after** the prediction point is chosen and is used for labels/evaluation alone.
3. **Do not call the short-censored observations negative.** Event=0 with endpoint−time < 48 gives an **unknown** binary target. For a simple binary baseline, keep such rows out of *supervised binary loss only* and disclose bias; a survival/censor-aware alternative would retain their information without guessing repair times.
4. **Control vehicle dependence.** Multiple readouts from one real truck are correlated. Partition training vehicles (not rows) for internal cross-validation. Never allow the same `vehicle_id` in both internal train and holdout. Do not report standard test uncertainty as though all 1,122,452 observations were independent samples.
5. **Use genuine held-out evaluations.** Official validation/test prediction point is the last originally provided readout per corresponding original vehicle. Use official **validation** for model selection and calibration; keep **test** untouched for one final evaluation. Consider the train-versus-held-out readout selection/distribution mismatch explicitly.
6. **Train-only preprocessing and transparent metrics.** Any later numeric fill/normalization must be fitted only on training vehicles and reported as a model transformation; it must not overwrite original CSVs or be misrepresented as true source measurements. Report PR-AUC, recall, precision, confusion matrix and calibration as warranted, not accuracy alone.
7. **No unsupported source fusion.** SCANIA remains real truck data; the original Mendeley AI4I 2020 synthetic-by-source data and Kaggle machinery photos are independent and have no verified shared machine IDs. Do not fabricate cross-source links, equipment repair/replace prices or plant downtime impacts.

### Approval distinction

- **Pass:** SCANIA structural audit, original observation indexing, endpoint timing integrity, and **48-step outcome-observability counting** all succeeded on actual source files.
- **Not yet approved:** fully specified source-consistent supervised feature/label extraction and as-of sampling, correct censor-aware training/evaluation implementation, publisher checksum comparison, model performance, or whole-project dataset acceptance (Kaggle photo label/provenance review remains open).

**No new synthetic source records were created.** This report documents actual measurements, not predictions. See [48-step policy](scania-horizon48-protocol.md) and [Issue #4](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/4).
