# Stage 4 — Source Label Verification (exactly three approved datasets)

**Status: IMPLEMENTATION PREPARED; REAL ORIGINAL-DATA EXECUTION AND SOURCE-LABEL REVIEW STILL OPEN.**

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

- [ ] Run the owner-local Stage 4 original-source label integrity script on the same three approved source datasets.
- [ ] Review the actual SCANIA original 23,550/5,046/5,045 target rows, original event/censor and five-class counts, unique ID bindings, unchanged source hashes, and semantic differences without inventing target mappings.
- [ ] Review all 10,000 AI4I source label-lineage entries and the exact **27 original disagreements**; document a defensible label treatment using published original semantics. If they cannot be resolved, explicitly quarantine/disallow disputed records in any later supervised training view without rewriting original labels. A source flag is not an external adjudicator.
- [ ] Review original-source image folder labels and **eight** quarantined source cases. Verify actual visual content and any available annotation provenance before declaring any image class as true. Source-folder labels alone are **provisional**; avoid implying all 219 remaining source-folder labels have been visually verified.
- [ ] Record Kaggle exact dataset license and per-photo provenance as **UNVERIFIED**, unless authoritative evidence establishes them. The source image archive's 234 original members remain unchanged.
- [ ] Formally decide whether Stage 4 source-label verification **can be signed off with documented exclusions/unknown labels** or remains blocked for unavailable independent evidence. **Do not automatically mark Stage 4 complete after producing review queues.**
- [ ] Only after Stage 4 completion consider **Stage 5 Data Splitting**. Stage 6 Feature Engineering and all modeling remain out of scope in Stage 4.

**Current decision: STAGE 4 OPEN.** Any non-adjudicated label or unverified image right must remain explicitly unresolved. This workflow does not misrepresent original-source consistency as proof of correct real-world labels.
