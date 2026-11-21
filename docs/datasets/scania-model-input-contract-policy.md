# SCANIA v2 — First model-input preprocessing contract (no training)

**Status (2026-11-21):** The owner has successfully executed the input-contract builder on the original-source-derived SCANIA v2 manifest, full 105-sensor profile and quality review: `ORIGINAL_SCANIA_MODEL_INPUT_CONTRACT_PREPARED`. The actual terminal output confirms 105 real sensors, 737,995 known-outcome training-fit observations, 162,292 unknown training-fit observations excluded from binary loss, and 182,063 known / 40,102 unknown observations in internal holdout. The baseline input contract preserves original missingness with no clipping/scaling/imputation; **no model is trained**. See [executed source-only contract results](scania-model-input-contract-results-2026-11-21.md).

**Only source:** https://researchdata.se/en/catalogue/dataset/2024-34/2 , the owner's real SCANIA Component X v2 download and its already locally executed source-only profile/manifest/quality audits. These are truck histories, not synchronized factory sensor/photos.

## Data-grounded decision

The real owner-run source-quality report measured **105** original sensor columns, **737,995** known-outcome train-fit readouts, **226,017** missing of 77,489,475 fit cells (**0.291674%**), **zero** constant/all-missing and **zero** features at >=1% missing. **95 of 105** original columns were *flagged for extreme observed min/max distances*: these are only descriptive flags, **not** evidence of corrupted records. No sensor values should be deleted or clipped solely because of these flags.

**Baseline model-input policy:**

- Use **all 105 original numerical sensor columns** in the same source order as the genuine CSV/profile. Exclude `vehicle_id`, `time_step`, source row number, train/holdout partition, study endpoint, censoring field, the 48-step target and any future values from predictors. Original vehicle ID remains **a grouping/reference field only**.
- Preserve every observed numerical sensor value **unchanged**. Do **not** scale, transform, standardize, winsorize, clip or automatically drop original features in the *first* baseline.
- Preserve missing sensor values as **missing at runtime**. Select a first baseline learner that **explicitly supports missing numeric values natively**, not a learner that requires mean/zero filling. NaN is a runtime representation of **already missing** source cells, not a new source measurement or claim that NaN was observed. If a future chosen learner lacks native missing handling, **stop** and write a separately audited training-fit-only imputation policy before modeling; never silently substitute zero or the mean.
- **No fitted transformation parameters** are needed under this identity/natively-missing policy, so there is no risk of learning imputation/scaling parameters from holdout. Any later learned transforms must be fitted on original training-fit vehicles only.
- Keep **18,869** original training-fit and **4,681** internal holdout vehicles disjoint. Use original observations only; keep all readouts of a source vehicle within one partition.
- Only the **737,995** known-outcome `train_fit` observations have a binary 48-step label suitable for first supervised loss. The other **162,292** short-censored fit readouts remain **UNKNOWN** (not negative). The original internal holdout has **182,063** known outcomes and **40,102** unknown; neither group is used to fit transformations or the model. This is a source-derived readout count, **not independent vehicles**. Excluding UNKNOWN records from binary loss may create follow-up selection bias; a later censor-aware survival alternative may be appropriate.
- Original official validation and test remain separate. Validation/test source label classes refer to the **last provided actual readout** for each vehicle; no exact future event date can be invented. Hold out official test until final evaluation.
- Before any model is claimed, define and evaluate imbalance-sensitive and vehicle-grouped metrics, account for strong source train/validation truncation differences, and avoid treating repeated observations from one vehicle as independent machines.

## This PR: source-grounded machine-readable contract

The script `src/preprocessing/create_scania_model_input_contract.py` reads only the **already-existing real-data audit artifacts** on the owner's computer:

- `data/processed/scania_training_manifest/manifest_report.json`
- `data/processed/scania_trainfit_sensor_profile.json`
- `data/processed/scania_sensor_quality_review.json`

It verifies all three statuses and critical real source counts, checks the **SHA-256 of the actual profile JSON** against the owner's previously executed quality-review digest, checks **all 105** per-feature counts/finite descriptive statistics and confirmed missingness totals, verifies the original ID-based vehicle split and UNKNOWN censoring outcomes. It refuses to overwrite an existing contract output file.

It then writes only `data/processed/scania_model_input_contract.json`, containing ordered original sensor names, explicit identity/native-missing policy, source audit SHA-256 fingerprints, verified count metadata, and remaining model-stage safeguards. **It does not reread, copy, impute or modify raw SCANIA CSVs. It does not create a model matrix, additional observations, artificial measurements, trained model or evaluation results.**

The publisher's *independent* checksum is still **unverified**: local hashes/fingerprints in this chain confirm integrity relative to the owner's original source audit, not a certification against official external source checksums.

## Next local execution after merging PR

Use the existing Windows PowerShell terminal in the repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/create_scania_model_input_contract.py --manifest-report "data/processed/scania_training_manifest/manifest_report.json" --profile "data/processed/scania_trainfit_sensor_profile.json" --review "data/processed/scania_sensor_quality_review.json" --output "data/processed/scania_model_input_contract.json"
```

The terminal prints a compact contract summary; the full ordered original sensor names are saved in the local JSON. Do **not** delete the prior quality-review JSON merely to rerun an already-successful audit.

## Remaining project gates

The machine-readable source-only contract must be **executed on the real owner-created artifacts** and reviewed before claiming the first baseline can consume it. A future training step must select a native-missing learner, read the original source rows by validated manifest references, respect known/UNKNOWN outcomes, train on actual fit-group vehicles only, and evaluate separately with vehicle-aware methods. No benchmark numbers are claimed yet.

Separate data-source acceptance remains open for the original Kaggle machinery-fault photos and unresolved original-source publisher SHA comparison. Original AI4I 2020 from Mendeley is *publisher-synthetic*, not a measured factory history; do not invent machine-level connections among these three independent datasets.
