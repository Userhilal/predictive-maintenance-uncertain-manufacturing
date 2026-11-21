# Stage 2 — Actual three-source data-audit execution results (2026-11-21)

**Current disposition: SOURCE-ONLY AUDIT EXECUTED; DETAILED QUALITY-REPORT REVIEW PENDING.**

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

## Remaining acceptance step

Review the **actual detailed report**, especially SCANIA per-split missingness/repair-class distribution, AI4I observed min/max and UDI concentration, and Kaggle class totals, small images, extension mismatches and source duplicate filenames. This is a read-only extraction of the ignored local JSON, not a rerun of the expensive original-image/SCANIA audit. Once those details are reviewed, issue a risk-qualified **Stage 2 audit sign-off** that accurately preserves the open Kaggle photo provenance and licensing restrictions. **Do not begin Stage 3 Data Cleaning before this review.**

Related: [Stage 2 audit methodology](stage2-original-data-auditing.md), [Stage 2 tracking issue #32](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/32).
