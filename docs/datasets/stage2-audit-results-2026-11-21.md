# Stage 2 — Actual three-source data-audit execution results (2026-11-21)

**Final disposition (2026-11-21): STAGE 2 TECHNICAL DATA AUDITING COMPLETE — original-source findings and open risks explicitly documented.** The earlier owner-run JSON contains a preliminary `stage2_signed_off: false` value generated before this detailed review; this human-reviewed sign-off records the separate outcome without editing the original evidence or claiming the raw data is clean, the labels resolved, or the image rights verified.

This document transcribes the actual terminal summary supplied by the repository owner after merging PR #31 and installing Pillow 13.0.0. The script reads exactly the three sources approved by the owner: SCANIA Component X v2, AI4I 2020 and Industrial Machinery Fault Images. The report's full source-level details remain only on the owner's Windows laptop at `data/processed/stage2_original_data_quality.json`. Do **not** treat this summary as an independent second dataset execution or imply the full ignored JSON file was inspected remotely.

## Genuine user execution

```json
{
  "status": "STAGE2_THREE_ORIGINAL_DATA_SOURCE_AUDIT_CREATED_REVIEW_REQUIRED",
  "scania_original_vehicles": 33641,
  "scania_original_readouts": 1516819,
  "scania_missing_sensor_cells": 481376,
  "ai4i_source_rows": 10000,
  "ai4i_source_failure_label_counts": {"0": 9661, "1": 339},
  "ai4i_source_label_disagreement_candidates": 27,
  "image_source_count": 234,
  "image_exact_duplicate_groups": 9,
  "image_cross_class_exact_duplicate_groups": 2,
  "image_perceptual_near_duplicate_review_candidates": 0,
  "kaggle_per_photo_rights_verified": false,
  "stage2_signed_off": false,
  "full_report_path": "data\\processed\\stage2_original_data_quality.json"
}
```

**Run completed successfully.** Python printed a **non-fatal Pillow 13 `Image.Image.getdata` deprecation warning**. A subsequent source-only patch replaces `getdata()` on the already-converted 8-bit grayscale dHash thumbnail with `tobytes()`, preserving each sampled pixel byte and dHash semantics; no original images or output values are changed.

## Verified from actual Stage 2 compact summary

| Dataset | Verified original-source finding | Evidence status |
|---|---|---|
| SCANIA Component X v2 | 33,641 source vehicles; 1,516,819 genuine operational readouts; **481,376 originally missing sensor cells** across 105 sensor columns in three splits | Actual prior SCANIA raw audit, source SHA-matched Stage 1 inventory and user-run Stage 2 reconciliation |
| AI4I 2020 | 10,000 originally published synthetic rows; 9,661 original binary `Machine failure=0`, 339 original `Machine failure=1` (3.39% positive); **27 original failure-mode vs global-target mismatch cases** | Actual user-run Stage 2 original CSV validation |
| Industrial Machinery Fault Images | 234 source photos in unchanged ZIP; **9 exact-byte duplicate groups**, including **2 groups with conflicting source-folder labels** | Actual user-run Stage 2 unchanged original image archive validation |
| Image candidate visually similar pairs | **0 detected** under the **specific dHash <=5** comparison of one representative per exact-byte SHA group | A threshold-limited negative screening result, **not proof that no near-duplicates or reused equipment photographs exist** |
| Kaggle image-per-photo reuse permissions | **Not verified** | Open source-rights/provenance limit; do not claim permission or public redistribution approval |

These are **audit findings, not corrected data**. In particular:

- The 27 AI4I original target/mode disagreements are **flagged for Stage 4 Label Verification**, not corrected or silently relabeled now.
- Exact image duplicates and two conflicting-folder-label groups are **flagged for Stage 3 Cleaning and Stage 4 Label Verification**, not deleted or relabeled now.
- SCANIA original missing sensor cells require a documented Stage 3 strategy; do not invent sensor readings or claim all readings are complete. Real SCANIA trucks are not manufacturing lines.
- Original SCANIA training repair/censor indicator is not identical to original validation/test 5-class labels. Do not flatten label semantics or treat right-censored vehicles as always healthy.
- The original AI4I benchmark was itself **synthetic as published**, not user-generated data. No synthetic records were produced by the project's audit.
- The three sources have **no established same-machine ID linkage**. Do not create fabricated matched sensor-photo pairs.

## Stage 2 risk register at current review

| Finding / residual evidence gap | Stage 2 status | Disposition in correct later stage |
|---|---|---|
| Source fingerprint reconciliation, basic CSV/ZIP integrity | **PASS** against earlier owner-computed downloaded-source hashes | Preserve raw and immutable provenance; independent publisher-signed hashes unavailable |
| SCANIA source missingness, censoring, source target semantics | **FINDINGS RECORDED**, no source changes | Stage 3 missing-value handling; Stage 4 label/observability definitions; Stage 5 group-aware split use |
| AI4I 27 target/mode disagreements, 3.39% failure positives | **FINDINGS RECORDED** | Stage 4 label decision policy, Stage 5 stratification/generalization review |
| Exact duplicated images and two cross-label duplicate groups | **FINDINGS RECORDED** | Stage 3 duplicate handling; Stage 4 label verification; Stage 5 leakage-resistant image partition |
| Perceptual dHash negative scan | **0 candidate pairs at the chosen threshold, limited evidence** | Further visual/manual checking before image model claim if needed |
| Exact Kaggle photo license, ownership and individual origin | **OPEN — NOT CERTIFIED** | Record as unresolved and gate any image activities requiring permission; license clarity cannot be fabricated |
| Additional independent manufacturer-/publisher-issued SHA verification | **OPEN — NOT CERTIFIED** | Do not misrepresent local-source SHA matches as provider-signed authentication |
| Full detailed local Stage 2 JSON report | **EXISTS on owner's laptop, detailed per-source fields not yet shared** | Review summary fields for source class counts, numeric ranges, highest-missing sensors, low-resolution images and exact source conflicts **before formal Stage 2 sign-off** |

**No additional datasets and no separate pump manuals are needed.** The two original PDFs accompanying SCANIA v2 are part of the SCANIA source package, not new datasets.

## Historical acceptance step (subsequently satisfied by the detailed review below)

Review the **actual detailed report**, especially SCANIA per-split missingness/repair-class distribution, AI4I observed min/max and UDI concentration, and Kaggle class totals, small images, extension mismatches and source duplicate filenames. This is a read-only extraction of the ignored local JSON, not a rerun of the expensive original-image/SCANIA audit. Once those details are reviewed, issue a risk-qualified **Stage 2 audit sign-off** that accurately preserves the open Kaggle photo provenance and licensing restrictions. **Do not begin Stage 3 Data Cleaning before this review.**

Related: [Stage 2 audit methodology](stage2-original-data-auditing.md), [Stage 2 tracking issue #32](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/32).


## Actual detailed Stage 2 report reviewed and disposition signed off

The owner ran the repository's **read-only** `review_stage2_report.py` on the **existing, owner-run** full audit and pasted its actual JSON response. Local raw evidence report fingerprint:

```
07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67
```

The read-only review's status was `STAGE2_ACTUAL_REPORT_DETAILS_READ_ONLY`, and it reported `not_stage3_cleaning_or_stage4_relabeling: true`. This is direct evidence supplied by the owner; the assistant did **not** remotely run the original source files or independently inspect the unshared full JSON.

### SCANIA Component X v2: source data integrity and missingness

| Source split | Original vehicles | Original readouts | Missing original sensor cells | Missing fraction of 105-sensor cells | Features with missing |
|---|---:|---:|---:|---:|---:|
| Train | 23,550 | 1,122,452 | 354,634 | 0.300901% | 104/105 |
| Validation | 5,046 | 196,227 | 60,339 | 0.292853% | 104/105 |
| Test | 5,045 | 198,140 | 66,403 | 0.319173% | 104/105 |
| **Total** | **33,641** | **1,516,819** | **481,376** | **~0.302247%** | Do not infer distinct union from total |

The three largest listed missing source features within each split are `291_0`, `291_1` and `291_10`, tied at **9,628** missing source readouts each in train (**0.857765%** of that split's readouts), **1,585** in validation (**0.807738%**) and **1,774** in test (**0.895327%**). The detailed report showed **no specification missing cells and no target missing cells** in each split. These findings do not mean there are no sensor missing values or justify imputing them without a Stage 3 policy. Existing genuine original SCANIA source audit had reported no invalid numeric sensor observations or backward/repeated adjacent timestamps.

Original training repair/censor outcomes: `0=21,278` and `1=2,272`; these are **study repair observations versus censoring**, not a binary normal-vs-failure label identical to the test/validation classification target. Validation classes `0=4,910,1=16,2=14,3=30,4=76`; test classes `0=4,903,1=26,2=15,3=41,4=60`. Vehicle/target joins and original train/validation/test vehicle partition disjointness were recorded as checked by the previously successful genuine source audit, cross-linked to unchanged owner-audited SCANIA source hashes.

**Disposition:** raw technical audit sufficient to proceed to an explicit *Stage 3 missing-value strategy*, with source schema/target semantics preserved.

### AI4I 2020: complete published synthetic benchmark

- **10,000** source rows; original `Machine failure` outcome: **9,661=0**, **339=1** (**3.39%** positive). No missing original CSV values or source duplicate feature vectors under the previously run validator.
- Type counts: `H=1,003; L=6,000; M=2,997`.
- Original failure-mode positive counts (not disjoint): `TWF=46`, `HDF=115`, `PWF=95`, `OSF=98`, `RNF=19`.
- Original target/flag disagreements: **27**, comprising **18** positive mode flag with global binary target zero and **9** global-positive rows with no positive mode flag; **24** rows have multiple positive mode flags. **Do not reinterpret these 24 as 24 target contradictions**; multi-mode cases and the 27 disagreements are different facts.
- Original observed numeric min/max (not clinical/physical plausibility certification):

| Original variable | Min | Max |
|---|---:|---:|
| Air temperature [K] | 295.3 | 304.5 |
| Process temperature [K] | 305.7 | 313.8 |
| Rotational speed [rpm] | 1,168 | 2,886 |
| Torque [Nm] | 3.8 | 76.6 |
| Tool wear [min] | 0 | 253 |

- Positive-class counts per successive original 1,000-UDI bands: **23,29,22,27,134,20,23,22,17,22**. The **4001–5000** band holds **134/339 = ~39.53%** of all positives, despite 10% of original records. This is an observed source distribution concentration, **not** a proven sensor anomaly or an invented source time series.

**Disposition:** Stage 2 audited imbalanced classes, label discrepancies and UDI distribution; label judgments are reserved for **Stage 4**, and future generalization/splitting concerns for **Stage 5**. Original AI4I is already synthetic as published; no new synthetic observations were created.

### Industrial Machinery Fault Images: actual original-archive quality

| Source-folder class | Original images |
|---|---:|
| Crack | 47 |
| Misalignment | 53 |
| Normal condition | 48 |
| Surface defects | 43 |
| Wear | 43 |
| **Total** | **234** |

- **210/234 (89.74%)** have minimum image dimension **under 300px**, including **168/234 (71.79%) under 200px**. Small images are a model-feasibility warning, not a justification to create replacement images.
- **Nine** exact-byte duplicate groups recorded; **two groups** are identical bytes in **different original source-folder classes**:
  - `Dataset/Crack/29_.jpg` and `Dataset/Wear/29_.jpg`.
  - `Dataset/Surface defects/24_.jpg` and `Dataset/Wear/21_.jpg`.
- Two original filename extension versus actual decoded-image-format mismatches: `Dataset/Misalignment/34_.jpeg` and `Dataset/Wear/42_.png`. Original ZIP members remain unchanged.
- The specific representative-group dHash procedure with Hamming threshold <=5 reported **zero additional candidate pairs**; this does **not** certify absence of near-duplicates, cropped copies, visual machine overlap, or source mislabeling.
- **Exact Kaggle dataset usage/license and per-photo provenance/rights remain unverified**. Accessible public source material did not establish verified rights for each photo. Treat **public redistribution or otherwise permission-dependent image usage as blocked pending actual permissions evidence**; do not invent a license or regard an archive fingerprint as a permission.

**Disposition:** Record original quality exceptions without removing, relabeling or inventing images. Duplicate handling belongs to **Stage 3**, conflict resolution to **Stage 4**, and leakage-safe split policy to **Stage 5**. Rights/provenance are a separate unresolved publication/usage gate, explicitly **not cleared by Stage 2**.

## Stage 2 technical-audit exit decision

- [x] Exactly the same **three approved original sources** audited; no supplementary pump guides.
- [x] Original source hashes/archives cross-checked against previously owner-measured source fingerprints and Stage 1 evidence (not independent publisher-signed checksums).
- [x] Owner executed complete preliminary three-source audit on real local bytes; local report SHA-256 recorded.
- [x] Owner executed read-only full-report reviewer and shared original source-quality specifics.
- [x] SCANIA all-three-split populations, missingness, original outcomes and source-integrity limitations reviewed.
- [x] AI4I complete original-source schema, class imbalance, numeric ranges, 27 flag/target disagreements and UDI failure concentration reviewed.
- [x] Kaggle all 234 class-folder totals, exact duplicates/cross-class contradictions, image resolution, mislabeled extensions and dHash screening reviewed.
- [x] Risks and downstream stage ownership explicitly documented; no source data were cleaned, overwritten, relabeled, split, engineered or trained during Stage 2.
- [x] Original image license/per-photo reuse rights recorded as **UNVERIFIED**; no legal clearance or public redistribution permissions claimed.

**Decision: `STAGE2_TECHNICAL_DATA_AUDIT_COMPLETE_WITH_DOCUMENTED_OPEN_ISSUES`.** This is *the audit's completion*, not data cleaning, corrected labels, or full legal permission certification. **Stage 3 Data Cleaning is the next work stage only after this sign-off documentation is merged.** Every later stage must preserve source originals, apply documented changes only to derived/curated output, and keep the three-source separation intact.
