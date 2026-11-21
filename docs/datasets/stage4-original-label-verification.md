# Stage 4 — Source Label Verification (exactly three approved datasets)

**Status: STAGE 4 ORIGINAL-SOURCE LABEL INTEGRITY TECHNICALLY COMPLETE WITH STRICT DOWNSTREAM ELIGIBILITY RESTRICTIONS (2026-11-21).** The owner executed original-source label validation and the final read-only review of all four derived manifests with their source fingerprints; the final decision and restrictions are documented in [the actual Stage 4 results](stage4-actual-source-label-results-2026-11-21.md) and [machine-readable eligibility policy](stage4-label-eligibility-policy.json). **This is NOT a claim that all original labels are independently verified or that image-model use is approved.** The owner executed the merged Stage 4 verifier on genuine sources; see [actual source-label results and next review step](stage4-actual-source-label-results-2026-11-21.md).

This phase follows the *completed and risk-qualified* Stage 3 source-preserving cleaning sign-off. Stage 4 checks how original labels are represented, linked to their original records, and where their meaning or correctness **cannot be independently established**. It **does not** blindly convert source flags into ground truth, override original labels, make image classifications from file names, split datasets, or train a model.

## Only three source datasets

1. **SCANIA Component X v2:** real fleet sensor/maintenance histories, nine original CSVs plus its two same-source documentation PDFs (Researchdata: https://researchdata.se/en/catalogue/dataset/2024-34/2). **Not** a manufacturing plant sensor dataset.
2. **AI4I 2020:** published synthetic manufacturing benchmark, original unchanged CSV from previously collected Mendeley archive (https://data.mendeley.com/datasets/5ww3zv87y7/1).
3. **Industrial Machinery Fault Image Dataset:** original Kaggle fault photos, originally 234 ZIP members, with Stage 3 manifests representing only its original ZIP entries (https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data).

No extra pump PDF manuals, fourth dataset, generated failure values, synthetic new records, or fabricated cross-source machine ID/label alignment.

## Definitions and actual-source evidence

### SCANIA v2

The [original SCANIA Component X source record](https://researchdata.se/en/catalogue/dataset/2024-34/2) and [published source data paper](https://www.nature.com/articles/s41597-025-04802-6) distinguish the original **`train_tte.csv`** targets from `validation_labels.csv` and `test_labels.csv`:

- **Training**: `in_study_repair` 1 means an observed Component X repair event by `length_of_study_time_step`; 0 indicates right-censoring (no observed event during the study horizon), **not proof the component is permanently healthy**.
- **Validation/test**: `class_label` is one of **five original source-defined categories 0–4** at the selected/last available operational readout, related to repair proximity. These are **not the same binary target** as the training repair/censor field; do not convert one into the other by guessing a time window.
- Earlier original full CSV auditing and Stage 2 detailed source review verified original partition disjointness, explicit vehicle-to-target linkage, no missing target cells, 33,641 vehicles and original class/event counts. In Stage 4, the three **original target CSVs are re-read**, SHA-checked against the genuine original Scania raw audit and validated for unique vehicle IDs, allowed domains, nonnegative finite study times, and original recorded counts. No fabricated per-observation training labels are derived.

### AI4I 2020

- The **original** `Machine failure` target is 0/1 and remains **9,661 negative / 339 positive** across 10,000 original records.
- Exactly **27 original rows** disagree between this binary target and the presence of any of `TWF`, `HDF`, `PWF`, `OSF`, `RNF`. **18** have a positive source failure-mode flag and overall target 0; **9** have overall target 1 but no positive source mode flag. These contradictions may be source-semantic edge cases and **must not be automatically described as wrongly labeled without independent evidence**.
- New outputs: all **10,000 original UDI-to-target / original flag lineage records** with `proposed_corrected_label` intentionally empty, and a separate **27-source-row queue** retaining original UDI + all original source flags, with dispute type and `unresolved` review state. Source-consistent flag patterns are **not independent real-world ground truth certification**.
- No synthetic oversampling, target repair, source row deletion, chronological split assumption based on UDI, or model training.

### Industrial fault images

- The **original class-folder names** are source-provided annotations. They are not sufficient by themselves to confirm a fault is actually visible, nor to verify that the image has reuse rights.
- Stage 3 established a reliable original-image metadata manifest for **234** ZIP members: **219 provisional candidate references**, **7 same-class exact-byte duplicate references** excluded from the candidate view, **4 duplicate-image members with mutually conflicting source-folder labels** quarantined, and **4 additional original manually flagged source photos** quarantined.
- New Stage 4 outputs keep a lineage record for **all 234 original image references**, and list the **8 quarantined source-photo label/provenance cases** separately. All original folder labels remain unchanged, with zero images represented as human-verified without evidence. The 219 provisional references remain **source-folder-labeled only** until actual visual validation.
- Neither copying/re-encoding the source image bytes nor changing labels/licensing fields is part of this stage. Original ZIP license and individual photo rights are still **UNVERIFIED**. Public redistribution and other permission-dependent use may not be described as authorized.

## What to execute next

After merging the Stage 4 PR, run in the same Windows PowerShell clone:

```powershell
git pull origin main

py -3.11 src/preprocessing/verify_stage4_labels.py --scania-data "C:\Users\hindh\Documents\2024-34-2\data" --scania-audit "data/processed/scania_audit.json" --ai4i "data/raw/ai4i2020.csv" --stage3-dir "data/processed/stage3_cleaning" --output-dir "data/processed/stage4_label_verification"
```

This script uses Python's **standard library only** and the already merged, read-only Stage 3 manifest reviewer. It does not require installing another package or obtaining another data source. It verifies the actual original source target CSV file digests against the previously executed raw Scania audit, validates original AI4I source bytes against its previous downloaded-source SHA-256, verifies Stage 3 original manifest hashes, and then writes only **local Git-ignored derived review metadata**:

| File | Contents |
|---|---|
| `stage4_label_verification_report.json` | Source label domains/counts, recorded original-source evidence, unresolved label/rights gates, output manifest SHA-256 values |
| `ai4i_original_10000_label_lineage.csv` | All original 10,000 source UDI target/flag provenance rows; no corrected labels |
| `ai4i_27_source_label_disagreements_for_review.csv` | The exact 27 original conflicting binary-target/mode-flag source rows, pending judgment |
| `images_original_234_label_lineage.csv` | Every original image member path, source folder label, prior Stage 3 cleaning state, SHA reference, explicitly unverified status |
| `images_8_source_label_review_cases.csv` | Four source-folder cross-class identical-byte conflicts and four pre-flagged image cases, **no guessed replacement class** |

The script refuses to overwrite a prior Stage 4 output folder and writes an atomic staging directory, so an error cannot silently replace existing evidence. It writes no original SCANIA, AI4I, or fault image files. **The absence of independent visual labels or photo permissions is made explicit, not silently declared resolved.**

## Stage 4 acceptance gates

- [x] Owner ran Stage 4 original-source label integrity against the same three approved original datasets; genuine terminal result received 2026-11-21.
- [x] Owner's actual SCANIA original 23,550/5,046/5,045 target rows, event/censor and five-class counts, unique vehicle IDs, unchanged source hashes, and semantic differences reviewed; no target mapping invented.
- [x] Owner's entire 10,000 AI4I UDI-level source lineage and exactly **27 original disagreements** checked by source-manifest hashes and exact queue membership. The 27 original source UDIs are explicitly **excluded from future label-sensitive supervised views until independent adjudication**; no original label changed.
- [x] All 234 original image folder-label references and **eight** quarantined source cases reviewed by hash, membership and original folder provenance; **ZERO images independently visually truth-verified**. All original-image supervised use remains **BLOCKED** pending actual visual annotation and rights evidence.
- [x] Kaggle exact dataset license and per-photo provenance recorded as **UNVERIFIED**, not permission-cleared. All 234 original source-image members remain unchanged; any use requiring rights evidence remains blocked.
- [x] Owner-executed final read-only Stage 4 evidence check passed. Technical **source-label integrity** is signed off **only with explicit restrictions**: original AI4I 27 disputed UDIs excluded from future supervised cohorts and all image supervised training/evaluation blocked pending independently verified annotations/rights. This does **NOT** sign off independent label truth for all images.
- [x] Stage 4 technical source-lineage and restriction policy complete; Stage 5 may be considered only for label-eligible SCANIA original cohorts and AI4I **9,973** source-consistent candidate rows. Any Stage 5 *supervised image split* remains blocked until separate image quality/rights checks are actually met. No feature engineering or modeling in Stage 4.

**Current decision: STAGE 4 ORIGINAL-SOURCE LABEL INTEGRITY TECHNICALLY SIGNED OFF WITH STRICT EXCLUSIONS.** AI4I original contradictory target/mode labels remain unresolved and excluded from future supervised views; no Kaggle image class or image reuse right has been independently verified. Full multimodal image model readiness remains blocked. Next stage is *scoped* Stage 5 Splitting for eligible source-defined telemetry/tabular cohorts only, after documentation merge.
