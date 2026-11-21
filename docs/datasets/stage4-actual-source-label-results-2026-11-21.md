# Stage 4 — Actual original-source label-lineage execution (2026-11-21)

**STATUS: STAGE 4 LABEL INTEGRITY SCRIPT EXECUTED SUCCESSFULLY, ORIGINAL LABEL ADJUDICATION OPEN.**

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
