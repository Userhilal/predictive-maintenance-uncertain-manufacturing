# Stage 4 — Actual original-source label-lineage execution (2026-11-21)

**Final technical disposition (2026-11-21): STAGE 4 ORIGINAL-SOURCE LABEL-LINEAGE VERIFICATION COMPLETE WITH STRICT SUPERVISED-USE EXCLUSIONS.** The owner-executed read-only check of all four Stage 4 metadata manifests passed. All 27 AI4I source discrepancies remain **quarantined for label-sensitive training**, and **ALL 234 image labels are not independently verified**; image supervised model training/evaluation remains **blocked** until real annotation and photo rights evidence. Stage 4 technical source-provenance sign-off must never be represented as approval of full three-source model-ready labeled data.

The owner merged PR #39 and executed `src/preprocessing/verify_stage4_labels.py` with all three *original* previously acquired and audited sources: SCANIA Component X v2 official vehicle-level target files, Mendeley AI4I 2020 original CSV and the Stage 3 verified reference manifests for the original Kaggle 234-image archive. This document transcribes the **actual owner terminal output**, not simulated rows, placeholder image labels, unverified source permissions, or an independent second execution. The four derived Stage 4 CSV manifests and full Stage 4 JSON live locally at `data/processed/stage4_label_verification` and were **not** uploaded to GitHub.

## Actual terminal result

```json
{
  "status": "STAGE4_ORIGINAL_SOURCE_LABEL_LINEAGE_CHECKED_ADJUDICATION_OPEN",
  "scania_source_label_rows_verified": {
    "train": 23550, "validation": 5046, "test": 5045
  },
  "scania_source_label_domains_counts": {
    "train": {"0": 21278, "1": 2272},
    "validation": {"0": 4910, "1": 16, "2": 14, "3": 30, "4": 76},
    "test": {"0": 4903, "1": 26, "2": 15, "3": 41, "4": 60}
  },
  "ai4i_original_rows": 10000,
  "ai4i_source_label_flag_disagreements_unresolved": 27,
  "images_original_source_members": 234,
  "images_label_or_provenance_quarantined": 8,
  "images_independently_verified_labels": 0,
  "source_labels_modified": false,
  "stage4_signed_off": false,
  "local_output_dir": "data\\processed\\stage4_label_verification"
}
```

## Source-specific integrity findings and model-use boundaries

| Source | Actual original-source label finding | Verification limitation |
|---|---|---|
| SCANIA v2 | Train: **23,550** original explicit unique vehicle IDs; original study repair/censor `0=21,278, 1=2,272`; validation: **5,046** original unique vehicles, original classes `0=4910, 1=16, 2=14, 3=30, 4=76`; test: **5,045** original unique vehicles, `0=4903, 1=26, 2=15, 3=41, 4=60`. Original source target file SHA-256 values reconciled against the actual earlier full source raw CSV audit. | Training repair/censor endpoint `in_study_repair` **is not the same task** as validation/test 5-class repair-proximity labels. This verifies *source provenance and domains*, not true physical vehicle outcome beyond the source. No fabricated label mapping or future-event claims. |
| AI4I 2020 | **10,000** original source rows with global binary `Machine failure`; **27** original source binary-vs-union-of-five-mode disagreements remain pending (**18** mode positive/overall zero; **9** overall positive/no mode flag). Four source-derived metadata CSV files created across both datasets, no source label edits. | **No auto relabel**. The original UCI AI4I metadata describes the global label as indicating failure when any listed failure mode is active, yet the owner-file counts conflict in 27 rows; this is an observed *source-internal inconsistency* requiring source-aware disposition, not proof which column is truthful. Source original dataset remains the owner's **Mendeley version 1**. |
| Original fault images | All **234** original ZIP member references preserved, including **219** provisional folder-label candidates, seven same-folder duplicate references and **eight quarantined source-image cases** (four cross-folder exact-duplicate conflicting labels + four flagged photos). **Zero** original source-image class labels have independent expert visual verification. | Original class folder is an annotation, not proof of visible physical fault or image rights. The exact image archive license/individual photo origin and reuse rights are **UNVERIFIED**, not implicitly cleared by source integrity checks. |

**Independently authoritative source metadata (not an additional dataset):** [UCI's official AI4I 2020 original dataset description](https://archive.ics.uci.edu/dataset/601/ai4i) explicitly says the global `Machine failure` label is derived from the presence of at least one of five modes. This provides *source-definition context* for the 27 owner-measured disagreements, **not** a reason to invent a correction or load a fourth dataset. The author's description also refers to simulated/synthetic manufacturing data, which must never be represented as real longitudinal factory machine observations.

### Explicit, safe Stage 4 policy while evidence remains absent

- Keep the unchanged original **SCANIA** repair/censor and five-class source targets, distinct by prediction task and cohort. No time-to-event labels derived from last-readout class by assumption.
- Keep the unchanged original **AI4I** binary target and five mode flags in source. **Do not infer that the 27 source rows are clean labels.** Keep their original UDI references explicitly flagged. Any later *supervised label-sensitive* downstream derived view must either (a) exclude them **with transparent counts and provenance** or (b) have a source-grounded, documented adjudication; do not flip or erase flags merely because a majority column disagrees.
- Keep **all eight** original disputed/quarantined image entries *quarantined*, as in Stage 3. The remaining **219** source-folder-labeled original image references must be described as **provisional, not independently visually label-verified**, until there is real image inspection or annotation evidence.
- Keep image-publication and all **permission-dependent image uses** gated on the original dataset license and individual photo reuse rights. No unrestricted distribution assumption.
- There are **only three approved original datasets**. No extra pump PDFs, new datasets, assistant-generated mock data, repaired synthetic repairs, labels invented from filenames, or fake cross-source same-machine label joins.

## Follow-up read-only Stage 4 provenance/manifest check

PR for `src/preprocessing/review_stage4_labels.py` adds a **read-only** final check of the **existing** Stage 4 local JSON report and four metadata CSV manifests. It verifies SHA-256 values against the report, row counts, exact queue membership, all original source classes and both label semantics, and that no corrections/source rights were falsely certified.

After merging that PR, run in PowerShell from the cloned repository root:

```powershell
git pull origin main
py -3.11 src/preprocessing/review_stage4_labels.py --input-dir "data/processed/stage4_label_verification"
```

**This command does not rerun original dataset processing or overwrite the local Stage 4 files.** Send the genuine JSON printed from the existing report. The final question for Stage 4 is then whether the project has enough external source evidence for disputed labels and original image class annotation integrity, or whether those samples must remain explicitly excluded/blocked. **Do not assert Stage 4 complete solely from a successful manifest integrity check.**

## Stage 4 exit gates (not yet satisfied)

- [x] Source-only Stage 4 code merged, owner-run original target/flag provenance read successful.
- [x] Original SCANIA target counts and the different 2-way repair/censor vs 5-class semantics documented, source target hashes checked.
- [x] Exact AI4I 27 original source target/mode disagreements and eight quarantined images tracked without label edits.
- [x] Zero images marked independently human-verified; original image rights/provenance not falsely cleared.
- [ ] Owner executes the read-only Stage 4 report/queue hash and membership check.
- [ ] Decide and document a **defensible Stage 4 resolution or restriction** for 27 ambiguous AI4I rows and original source-image label/rights risks, recognizing no independent image visual annotation evidence yet.
- [ ] Only after that review, record a risk-qualified Stage 4 determination. **Stage 5 Data Splitting must not start prematurely**.

**Current status: STAGE 4 ORIGINAL LABEL LINEAGE EXECUTED; ADJUDICATION AND FINAL SIGN-OFF OPEN.** No additional datasets are authorized.

## Actual owner-run final Stage 4 manifest review

The owner supplied a genuine run of the merged read-only `review_stage4_labels.py` against the existing local Stage 4 evidence folder. It returned `STAGE4_ACTUAL_SOURCE_LABEL_MANIFESTS_REVIEWED_READ_ONLY`, and the **full previously generated Stage 4 report** was fingerprinted as:

```text
c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29
```

The original Stage 3 report fingerprint remained `3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186`. The actual check reported `all_four_stage4_lineage_csv_sha256_verified=true`, `exactly_three_original_sources=true`, `original_files_or_source_labels_modified=false`, and `split_or_feature_or_model_created=false`.

Observed original source label counts were independently reconciled by **the owner's executed scripts**:

- **SCANIA:** train **23,550** original target records, validation **5,046**, test **5,045**; source repair/censor versus five-class semantics remain strictly distinct. No independent field-outcome ground truth beyond original source certification.
- **AI4I:** **10,000** original rows, `0=9,661` and `1=339`. Exactly **27** contradictory target/mode rows, including **18** original target=0/mode-positive, **9** original target=1/no-mode-positive. All 27 source UDIs appear in the previously created review queue; their target truth is **not adjudicated**.
- **Images:** **234** original ZIP member references, exact folder categories `47/53/48/43/43`, nine exact-byte duplicate groups, **219** provisional source-folder label references, **7** same-folder duplicate copies, **4** cross-class duplicated/conflicting references and **4** previously pending manual-review references. All **eight** known source label/provenance disputed image references remained quarantined. **Independently visually verified image classes = 0**, and individual-photo reuse rights remain **UNVERIFIED**.

The original local JSON had `stage4_signed_off=false` and the read-only viewer had `label_adjudication_and_stage4_signoff_still_open=true`; both correctly reflect their **pre-human-review execution state**. We preserve these original user-run artifacts and record the later risk-qualified *technical* disposition here. No source files, original labels, or existing fingerprints are overwritten.

## Conclusive Stage 4 source-label policy — no guessed corrections

The machine-readable [Stage 4 supervised-use policy](stage4-label-eligibility-policy.json) is **an explicit downstream eligibility contract**, not a newly measured dataset, a split, or a claim of extra annotation.

### SCANIA (original source targets accepted for source-defined tasks)

The original train event/`in_study_repair` and right-censoring endpoint belong to the **time-to-event task**; validation/test `class_label=0..4` belong to the official separate **five-class proximity task**. Never silently create a combined binary failure target, classify censored vehicles as permanently healthy, or infer unobserved repair event times. Stage 5 must preserve original vehicles and official source cohort boundaries.

### AI4I (27 ambiguities quarantined, 9,973 source-consistent candidates)

Preserve the exact original 10,000-row CSV and all five mode flags unchanged. For **future Stage 5 label-sensitive supervised views only**, use the original source UDI membership from the existing `ai4i_27_source_label_disagreements_for_review.csv` review queue as an **exclusion rule** until independent source-grounded adjudication. The 27 disputed records remain in the original dataset and review queue, but are **not permitted to enter train, validation or test supervised views** for the global binary failure target without adjudication.

This leaves **9,973 source-consistent (not independently truth-verified) candidate rows**: original target `0=9,643` and `1=330`. These counts follow directly from 9,661 original negatives less 18 disputed original negatives and 339 original positives less nine disputed original positives. They **are not the result of executing Stage 5**. Stage 5 should explicitly verify them from local source UDI lineage. Never use TWF/HDF/PWF/OSF/RNF as input predictors of the overall `Machine failure` target, since they encode failure modes and could cause target leakage.

The [official UCI description of the same AI4I 2020 dataset](https://archive.ics.uci.edu/dataset/601/ai4i) describes machine failure as the union of five failure modes, yet the original owner-audited rows have 27 mismatches. The definition discrepancy **supports quarantine**, not automatic bit flips or made-up labels.

### Kaggle industrial fault images (supervised model use blocked)

The 219 provisional image references possess only **source-folder annotations**, *not independent visual class verification*. In addition to the eight quarantined source-image label/provenance cases and seven same-class exact duplicates, **all 234 original image references are ineligible for verified-label supervised training/evaluation and publication/other permission-dependent image use until both (a) actual source-photo rights/provenance and (b) suitable independent visual annotation evidence are established.** A Stage 5 program may carry image **metadata-only source lineage** and the quarantine decisions, but must not generate an approved supervised image split or present an image-classifier evaluation as scientifically cleared.

The Kaggle source page could be located, but **its individual-photo reuse rights and exact usable permissions were not verified**. We neither infer a license from Kaggle hosting nor assert all photos were created by the uploader. A source-folder name remains an unverified label even if its source ZIP membership is authenticated.

### Review-gate decision

- [x] Original SCANIA 3-file target integrity and distinct domain/meaning verified against owner-source raw audit; no fabricated labels.
- [x] Original AI4I UDI-level 10,000-label lineage integrity and exact 27 source disagreement queue verified by SHA; **no corrections claimed**.
- [x] Original image ZIP member-level 234-label lineage and eight source-review cases verified by SHA; zero false expert approval claims.
- [x] Source eligibility contract recorded: AI4I 27 disputed UDIs excluded from *future* supervised views; all image supervised use withheld pending quality and rights.
- [x] No data splitting, feature engineering, source-label edits, photo distribution or new datasets.
- [x] Risks explicitly carried forward with hard restrictions rather than inventing full independent label adjudication.

**Technical source-label verification decision:** `STAGE4_SOURCE_LABEL_INTEGRITY_COMPLETE_WITH_EXPLICIT_TRAINING_ELIGIBILITY_RESTRICTIONS`.

**Crucial limitation:** This is **NOT** proof that all three sources are label-verified or eligible for a multimodal trained model. The photo source remains **unverified and blocked for supervised use**; the 27 original AI4I contradictions remain **unresolved but quarantined**. These restrictions must be enforced in any later Stage 5 data-splitting implementation, not treated as advisory. If the project requires verified use of all three original sources for training, the additional image evidence must be provided and reviewed **before** a full three-source model can be approved.
