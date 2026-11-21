# SCANIA v2 — Original-only training cohort manifest

**Status (2026-11-21):** The owner successfully executed the original-only SCANIA v2 training manifest. It references 1,122,452 original train readouts across 23,550 genuine vehicles and preserves the previous 25,758 / 894,300 / 202,394 measured target-observability counts; all source hashes match the earlier owner's local audit. See [actual measured manifest results](scania-training-manifest-results-2026-11-21.md). **No model was trained; no source rows fabricated.**

**Strict provenance:** Only [the original owner-supplied SCANIA Component X v2](https://researchdata.se/en/catalogue/dataset/2024-34/2), its genuine downloaded CSVs, and the previously *owner-executed source-only audit/index/horizon reports*. No replacement dataset, artificial vehicle, invented sensor measurement, synthetic failure or fake source history.

## Previous measured checks

The owner ran the original nine-CSV audit, original observation index, endpoint timing check, and 48-step outcome-observability audit. The last report measured 1,122,452 real train readouts for 23,550 vehicles; 25,758 source readouts with a known repair in 48 steps, 894,300 with no recorded repair in 48 steps, and 202,394 short-censored unknown readouts. These are **source observations, not independent training vehicles**. See [actual 48-step audit](scania-horizon48-audit-results-2026-11-21.md).

## This step: traceable manifest, no fabricated data

The new script is `src/preprocessing/build_scania_training_manifest.py`.

It makes a **reference/target manifest**, not a new synthetic dataset, not a sensor feature matrix, and not a trained model. Exactly one manifest row corresponds to each genuine original training CSV readout: actual `vehicle_id`, actual `time_step`, exact source CSV row number, and real per-vehicle observation ordinal.

**As-of selection** is predefined and outcome-independent: include **all existing observed training readouts** as candidate prediction times. This does not depend on the repair endpoint, future count of observations, inferred RUL or validation/test outcome labels. It does not invent timestamps or readouts. The 48-step target is derived **after** the genuine observation timestamp has been fixed.

For an existing source readout time t and its original source repair/censoring endpoint E, D=E−t:

| Original source event and follow-up | Manifest outcome status | Nullable binary target |
|---|---|---|
| Original repair recorded, 0 < D ≤ 48 | `recorded_repair_within_48` | `1` |
| E−t ≥ 48 (source proves at least 48 steps without repair) | `no_recorded_repair_within_48` | `0` |
| Right-censored, 0 < D < 48 | `unknown_short_censored_followup` | **blank** |

These targets are **computed from genuine recorded SCANIA endpoints**; they are *not* invented repairs or new ground-truth observations. Unknown censored readouts remain present with an explicitly blank target. They must not contribute as known negatives to a simple binary classification loss. Dropping them can create follow-up/selection bias; a fully censoring-aware survival model can use additional censoring information later.

## Genuine source data integrity and split safety

- First check genuine source audit metadata and previously recorded original-file SHA-256. The two original training CSVs must match the owner-generated local fingerprints; **publisher hash verification is not claimed**.
- Stream `train_operational_readouts.csv` **in lockstep** with its existing source-only index. Refuse shifted source lines, missing rows, changed source vehicle IDs, inconsistent real timestamps or missingness counts.
- Require the newly derived status totals to equal the owner's **previous actual 48-step audit**; fail rather than fabricate or silently adjust a count.
- Assign each **original vehicle ID** deterministically to an approximate 80% internal fit and 20% internal holdout group using SHA-256 of the ID with a fixed source-specific salt. This depends only on source vehicle identity, **never the future repair time, event class, or censoring length**.
- All observations of a given vehicle remain in the same internal partition. The official original **validation and test** vehicles/files are untouched. The source `vehicle_id` is a grouping/join identifier **not a model predictor**.
- Keep original source sensor features in the unchanged files. The manifest has only observation references, group assignments, and **target-only** outcome status; do not pass `horizon48_outcome_status` or `source_derived_binary_target` as features.
- This creates **derived rows in a CSV manifest**, but never extra original SCANIA sensor observations, new source events, or synthetic training measurements.

## How to run locally

**For reproduction using the already-merged script**, run inside the existing project root in Windows PowerShell with a NEW output directory; the previous output exists and the script correctly refuses to overwrite it:

```powershell
git pull origin main
py -3.11 src/preprocessing/build_scania_training_manifest.py --audit "data/processed/scania_audit.json" --horizon-audit "data/processed/scania_horizon48_audit.json" --data-dir "C:\Users\hindh\Documents\2024-34-2\data" --index-dir "data/processed/scania_observation_index" --output-dir "data/processed/scania_training_manifest"
```

Review the compact source-derived report:

```powershell
Get-Content "data/processed/scania_training_manifest/manifest_report.json"
```

Outputs are under ignored `data/processed/` and stay on the user's machine:

- `train_original_observation_manifest.csv`: **one reference per genuine original training readout**; no sensor values copied. Columns: `vehicle_id`, `time_step`, `original_csv_row`, `observation_index`, `internal_vehicle_partition`, `horizon48_outcome_status`, `source_derived_binary_target`.
- `manifest_report.json`: original-row counts, genuine source-label counts, grouped vehicle totals, actual fit/holdout proportions, source hash flags and checks.
  
Refuses overwriting an existing output directory; use a versioned destination for a rerun.

## Acceptance before model training

- The owner's actual manifest run must succeed on original files and report **exactly** 1,122,452 original references and the **same** 25,758 / 894,300 / 202,394 source-derived outcome counts previously measured. Fit/holdout **vehicle** counts must be reported from actual IDs; do not invent their values.
- Verify both partitions contain original vehicles and report positive/unknown class counts *after* the real script runs. If the internal holdout does not contain enough positives, revisit the group split **without using hidden test labels or inventing rows**.
- The script **does not construct a model input matrix or train anything**. A later modeling step must define source-feature transformations, group-aware sample weighting, and validation/calibration using *original* holdout data.
- A 48-step classification baseline may mask short-censored unknown targets, but that is **not the same as full censoring-aware RUL**; do not claim true remaining useful life for censored vehicles.
- This project has only three permitted user-provided data sources. SCANIA is real truck fleet history; the original AI4I dataset is synthetic by its publishers, and the Kaggle fault photos are independent. **Never fabricate per-machine links among these sources**.

**Remaining provenance caveat:** SHA-256 comparisons validate consistency against the original owner-run local raw-data audit, **not official publisher checksums**. The separate Kaggle image rights/labels and source integrity review remain open, so the overall multimodal dataset phase is not fully certified.
