# Stage 6 — Feature Engineering (eligible AI4I original data only)

**Status: STAGE 6 ELIGIBLE ORIGINAL AI4I TRAIN-ONLY FEATURE ENGINEERING TECHNICALLY COMPLETE AFTER REAL OWNER-RUN SOURCE/VALUE/FOUR-MANIFEST VERIFICATION (2026-11-21).** This is an AI4I-only feature preparation sign-off, **NOT** full independent multimodal label/rights/task readiness. The [actual owner-run 79,784-value review and technical sign-off](stage6-actual-feature-results-2026-11-21.md) records original local Stage 6 report SHA-256 `0250e7063eaae1f551a843cde3f963ba95f16f08cb261bd40b592783c58a3973`. See [the actual user-executed Stage 6 terminal summary and source-level review contract](stage6-actual-feature-results-2026-11-21.md). This source is AI4I's originally published synthetic benchmark; no independent three-source multimodal feature readiness is claimed.

Stage 5 **eligible tabular/telemetry source partition integrity** was signed off with actual owner-run seven-manifest hashes and exact AI4I seeded UDI reconstruction (Stage 5 local report SHA-256 `9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda`). Original SCANIA train repair/right-censor and official val/test five-class target compatibility remains **unresolved**, and all source Kaggle fault photos remain **blocked for supervised image feature/training use** while their image labels and rights/provenance remain unverified (issue #43).

Stage 6 is deliberately limited to **the 9,973 accepted original AI4I 2020 records** from the published-synthetic manufacturing benchmark, all governed by the exact previously verified UDI train/validation/test assignment. Original dataset CSV remains unchanged.

## Source and transform contract

| Original data item | Treatment in this phase | Data leakage guard |
|---|---|---|
| Original `Type` (L, M, H) | **Three** deterministic mutually exclusive 0/1 indicator predictors, `type_H`, `type_L`, `type_M` | Category vocabulary is the original source's fixed three-class domain; not inferred from val/test and no target correlation encoding |
| Air temperature [K] | Numeric `air_temperature_K_train_z` | Mean and population standard deviation fitted from **6,981 training UDI rows only** |
| Process temperature [K] | Numeric `process_temperature_K_train_z` | Same train-only fit policy |
| Rotational speed [rpm] | Numeric `rotational_speed_rpm_train_z` | Same train-only fit policy |
| Torque [Nm] | Numeric `torque_Nm_train_z` | Same train-only fit policy |
| Tool wear [min] | Numeric `tool_wear_min_train_z` | Same train-only fit policy |
| Original `Machine failure` | Retained only as `original_machine_failure_target_not_a_feature` **label metadata** | Never an input predictor or source of normalization statistics |
| Original `UDI` | Retained only as `source_udi_not_a_feature` **join/provenance metadata** | Never an input predictor or time axis |
| Original `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | **Entirely excluded from engineered predictor columns** | Original IDs and source failure-mode labels would cause identity/target leakage; 27 original discordant UDI rows also never enter any supervised partition |

**Final engineered predictor count: 8** = 3 original source Type indicators + 5 train-only-standardized numerical source measurements. No interaction terms, fault thresholds, outlier deletion, synthetic numeric series, labels inferred from original source mode flags or source UDI bins are created. Do **not** turn UDI into a time index.

The AI4I original CSV contains **10,000 original rows** with **27 unresolved original binary target/mode-flag disagreements**. Stage 4 mandates these exact 27 UDI rows be quarantined, leaving **9,973 eligible source-consistent rows**: train **6,981** (6,750 negative, 231 positive), validation **1,497** (1,447 negative, 50 positive) and test **1,495** (1,446 negative, 49 positive). Source agreement is **not independent failure-label ground truth**. Each engineered CSV is an output *view* of exactly the corresponding original eligible Stage 5 UDI records, in the same UDI order, with unchanged original failure target as separate metadata.

### Fit/transform safety rules

- Read and SHA-verify the unchanged original AI4I CSV; read the **already approved Stage 5 seven-manifest review**, whose report hash must still equal `9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda`.
- Recompute Stage 5 metadata SHA-256 and exact AI4I seed+source-UDI assignment from existing derived metadata before creating features. Reconcile source UDI, `Type` and binary target for each of the **9,973 eligible rows** against the original source bytes. Reconfirm the exact original 27 disputed UDIs never enter these views.
- Compute **five** `mean` and `population_std` values using **training rows only** and reject any nonfinite/constant feature; no overall-dataset means, validation/test fitting, scaling leakage, target-based transforms or model fitting.
- Apply the same frozen train-only numeric parameters to *both* validation and test. **Do not clip** held-out z-score magnitudes using held-out distribution. Zero source missing numeric values are already verified; do not invent imputation values or repair original data.
- Include the source UDI and binary target in each derived file strictly as **explicitly named metadata**, outside the eight approved predictor fields. Requiring ML code to select the contract's ordered predictor names prevents using a label or ID as feature.
- Output only to a brand-new local Git-ignored `data/processed/stage6_ai4i_features` folder. Refuse overwrites and use atomic staging/rename to preserve previous signed-off files.

## Explicit restricted sources

**SCANIA Component X v2 (the existing nine original CSVs and two same-source PDFs):** Stage 5 preserves the original 23,550/5,046/5,045 source vehicle cohorts and 1,516,819 original readouts, **not** a unified cross-cohort supervised prediction task. SCANIA source observations and their censored labels are not rewritten or engineered in this Stage 6 AI4I-specific implementation. Earlier separate SCANIA training-horizon or sensor-profile scripts must **not** be treated as authorizing a unified official validation/test label task without separately reviewing its source-grounded endpoint and censoring specification.

**Industrial Machinery Fault Images original archive (234 photos):** no images, visual embeddings, supervised image features, image train/test groups, or per-photo model training datasets created. Source-folder labels are not independently verified and original photo license/individual reuse rights remain **UNVERIFIED**, tracked under issue #43. Never claim this tabular AI4I feature output completes multimodal feature engineering.

**Exactly three original approved sources; no fourth dataset, independent pump manuals, synthetic newly created observations/photos or fabricated cross-source same-machine pairs.** AI4I itself is published synthetic data, not original factory field sensor measurements.

## Execute on the owner's real original local data

After merging this Stage 6 PR, from the Windows repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/engineer_stage6_ai4i_features.py --ai4i "data/raw/ai4i2020.csv" --stage5-dir "data/processed/stage5_eligible_splits" --stage4-policy "docs/datasets/stage4-label-eligibility-policy.json" --output-dir "data/processed/stage6_ai4i_features"
```

No extra data downloads or Python libraries required beyond standard Python 3.11 and the existing repository scripts. The script writes **only five derived local files**, without modifying source or earlier signed-off artifacts:

| Local output | Meaning |
|---|---|
| `ai4i_train_features.csv` | 6,981 original training UDI records, 8 engineered predictor columns plus explicit source UDI and original target **metadata** |
| `ai4i_validation_features.csv` | 1,497 original validation UDI rows using **same training fitted parameters** |
| `ai4i_test_features.csv` | 1,495 original test UDI rows using **same training fitted parameters** |
| `ai4i_train_only_feature_contract.json` | **Five source-measurement train-only mean/std/range parameters**, original source SHA and Stage 5 provenance, eight approved predictors and explicitly forbidden target/UDI/failure-mode source columns |
| `stage6_feature_report.json` | Source UDI/target/Type reconciliation, 6,981 train-only fit rows, three output cohort counts/label distributions, image/SCANIA source blocks, derived file SHA-256 fingerprints |

### Stage 6 exit checks (still to do)

- [x] Owner merged Stage 6 PR #49 and successfully executed the feature producer on the unchanged original AI4I CSV, using the same approved Stage 5/Stage 4 source evidence. Real terminal JSON received 2026-11-21.
- [x] Owner's final source-value reviewer confirms exactly **6,981 training UDI rows** fitted five numeric transformers; exactly **8** predictor fields for **9,973** original source-consistent UDI rows.
- [x] All **27** original disputed source UDI rows remained excluded from all engineered outputs; targets and UDI remain metadata outside approved predictor columns.
- [x] All **five** numeric train-only means, population standard deviations, min/max values were independently recomputed from original **6,981 training UDI** source measurements and matched; frozen parameters applied to validation/test without holdout fitting.
- [x] All **four** derived Stage 6 file SHA-256 values verified against real local Stage 6 report; original Stage 5 assignment membership/source targets verified, and all **79,784** engineered predictor values recomputed for 9,973 original source UDIs; identifier, source modes and global target are not input predictors.
- [x] All SCANIA original task incompatibility and Kaggle image visual-label/rights restrictions remain active; no original source file, original metadata, image bytes or model modified.
- [x] Risk-qualified **Stage 6 original AI4I-only feature engineering technical sign-off** documented after actual owner-run source-value and SHA checks; **does NOT** clear SCANIA's cross-task model readiness, Kaggle image label/rights or full three-source multimodal model readiness.

**Final decision:** `STAGE6_ELIGIBLE_AI4I_TRAIN_ONLY_FEATURE_ENGINEERING_COMPLETE_WITH_SCANIA_AND_IMAGE_GATES`. Original local Stage 6 source report retains its preliminary pre-approval `stage6_signed_off=false` and must remain unchanged; the genuine post-review sign-off is the separate results document. **Stage 7 Final Data Validation may begin after the sign-off PR is merged**, strictly scoped to eligible tabular AI4I and explicit unresolved SCANIA/image constraints. **Stage 8 model development is not started.**
