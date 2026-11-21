# SCANIA Component X v2 — Full original-file audit results

**Source:** [User-supplied Researchdata dataset 2024-34, version 2](https://researchdata.se/en/catalogue/dataset/2024-34/2)

**Evidence:** `scania_audit.json` uploaded by the project owner after running `src/preprocessing/audit_scania.py` locally against all nine original CSVs extracted under `2024-34-2/data` (2026-11-21). Values below are transcribed or calculated from that report, **not generated from artificial records**. Raw CSVs remain on the user's computer.

## Overall original-data audit

| Check | Actual result |
|---|---|
| Validator status | `RAW_CSV_AUDIT_EXECUTED` |
| Operational readings | **1,516,819** |
| Vehicles | **33,641** |
| Operational fields | **107** (vehicle ID, time step, 105 features) |
| Original data modified by validator | No (read-only script) |
| Vehicle IDs disjoint across train/validation/test | Yes |
| Specification and target files have explicit vehicle IDs | Yes for all three splits |
| Vehicle–target linkage | Verified by implemented ID-set checks |
| Invalid nonnumeric/nonfinite features | 0 reported |
| Backward-in-file timestamps / repeated adjacent time steps | 0 reported |
| Missing specification cells | 0 reported |
| Missing target cells | 0 reported |
| Official provider checksums independently compared | **No — still open** |

## Per-split observations from real CSVs

| Split | Vehicles | Readouts | Readouts per vehicle (min–max) | Maximum per-feature missingness | Aggregate feature-cell missingness | Target counts |
|---|---:|---:|---|---:|---:|---|
| Train | 23,550 | 1,122,452 | 5–303 | 0.858% | 0.301% | Censored 21,278; repair event 2,272 |
| Validation | 5,046 | 196,227 | 1–209 | 0.808% | 0.293% | Classes 0–4: 4,910 / 16 / 14 / 30 / 76 |
| Test | 5,045 | 198,140 | 1–262 | 0.895% | 0.319% | Classes 0–4: 4,903 / 26 / 15 / 41 / 60 |

Across all three partitions there are **481,376 missing sensor cells out of 159,265,995 available feature cells**, or **0.302% overall**.

The aggregate feature-cell missingness percentages above were computed by summing the report's **105 per-feature missing-cell counts** and dividing by (number of operational readouts × 105). This is not the fraction of rows containing any missing entry. A few histogram-bin groups share identical missing-value counts; per-vehicle and row-level missingness patterns need examination before imputation.

## Remaining-data concerns

1. The 105 operational features have *some missing cells* even though every individual feature has less than 1% missingness in each split. The most frequently missing bins belong to the `291_*` group (9,628 training readings, 1,585 validation, 1,774 test per bin). Preserve original missing values and fit any imputation method using **training records only**.
2. Heavy target imbalance: 2,272 recorded train repairs of 23,550 vehicles (~9.65%); class 0 accounts for 4,910/5,046 validation vehicles and 4,903/5,045 test vehicles. Treat other censored training records as **right-censored**, not known never-fail cases.
3. The CSV audit checks schema, counts, ID sets, missingness and timestamps. It does **not** independently verify every engineering assumption, machine-level target semantics, annotation correctness, or feature causality. Validate observation-cutoff rules before time-to-event modeling.
4. All nine locally calculated SHA-256 values are present in the uploaded report; they were **not** compared with official provider checksums. Do not claim publisher-verified byte-for-byte authenticity.
5. SCANIA is real **truck-component** history, not a factory manufacturing line. It is not synchronized with the separate Mendeley AI4I observations or Kaggle machinery photographs. Do not manufacture cross-dataset machine links, fake observations, or simulated maintenance history.

## Audit decision

**Original SCANIA CSV structural/data-quality audit: PASS for the implemented checks, with documented residual missingness and source-hash verification pending.** This supports moving to a separate, cautious SCANIA preprocessing design, not claiming a validated predictive model or complete project dataset sign-off.

The user's original, unchanged CSVs remain outside GitHub; only the aggregate audit results and methodological notes are recorded here. Keep [Issue #4](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/4) open until provenance and preprocessing decisions are reviewed.
