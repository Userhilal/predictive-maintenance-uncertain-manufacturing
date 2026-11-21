# Stage 3 — Actual conservative original-source cleaning results (2026-11-21)

**Final decision (2026-11-21): STAGE 3 CONSERVATIVE DATA CLEANING COMPLETE — reviewed against actual owner-run metadata, with label/rights limitations explicitly unresolved.** The Stage 3 original local JSON remains a preliminary execution report (`stage3_signed_off=false`); this document separately records the reviewed technical sign-off without modifying the original report.

Stage 1 collection and Stage 2 read-only technical auditing have already been signed off with documented risks. The owner merged Stage 3 PR #35 and executed `src/preprocessing/clean_stage3_originals.py` on exactly the same three original approved sources, against the unchanged actual Stage 2 report with locally verified SHA-256 `07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67`.

This document transcribes **actual owner terminal output**, not simulated dataset execution. The complete local Stage 3 report and three CSV source-reference manifests are Git-ignored; their SHA values and row membership must be read back before final Stage 3 sign-off.

## Actual local terminal result

```json
{
  "status": "STAGE3_CONSERVATIVE_SOURCE_CLEANING_CREATED_REVIEW_REQUIRED",
  "scania_original_readouts_retained": 1516819,
  "scania_missing_sensor_cells_left_missing": 481376,
  "ai4i_original_rows_retained": 10000,
  "ai4i_source_label_conflicts_left_for_stage4": 27,
  "images_original_archive_members": 234,
  "images_provisional_candidates": 219,
  "images_exact_duplicates_and_quarantined": {
    "exclude_same_class_duplicate": 7,
    "provisional_candidate": 219,
    "quarantine_conflicting_labels": 4,
    "quarantine_manual_review": 4
  },
  "original_files_modified": false,
  "stage3_signed_off": false,
  "local_report": "data\\processed\\stage3_cleaning\\stage3_cleaning_report.json"
}
```

## Audited Stage 3 source-preserving dispositions

| Original source | Actual cleaning result | What remains unresolved |
|---|---|---|
| SCANIA Component X v2 | **1,516,819** original source observations retained; **481,376** originally absent sensor cells remain missing; no original source files modified | Native-missing model policy for future Stage 6 and source label/censoring semantics for Stage 4 |
| AI4I 2020 | **10,000** original published-synthetic records preserved unchanged; **27** target/failure-mode disagreements retained | Stage 4 source label verification, Stage 5 distribution-aware split choices |
| Industrial Machinery Fault Images | Original **234** ZIP image members kept intact; **219** provisional candidate *references*, **7** same-class duplicate references excluded from candidate view, **4** cross-class contradictory references quarantined, **4** manually flagged original records quarantined | Stage 4 actual visual label verification, Stage 5 leakage-safe image partitioning; image provenance and reuse rights explicitly NOT verified |

**Key distinction:** the images have **not** been erased, copied, transformed, visually retouched, relabeled, or released. A `provisional_candidate` source path is a **derived manifest selection**, **not** a human-certified, legally authorized training sample. The original image archive is intact. No fourth dataset, unrelated pump manuals, artificial repair histories, user-generated synthetic records, train/test splits or engineered features were introduced.

The preliminary Stage 3 local report correctly contains `stage3_signed_off=false`: it is an original execution fact recorded **before** detailed human audit review. Do not overwrite this evidence to claim sign-off.

## Stage 3 final verification gate (read-only, no re-cleaning)

A new source-only helper, `src/preprocessing/review_stage3_cleaning.py`, reads ONLY the existing ignored local `stage3_cleaning_report.json` and three accompanying CSV metadata manifests. It:

- Recomputes SHA-256 of each manifest and compares with the original Stage 3 report's `manifest_sha256`, with no source bytes read or changed.
- Reconciles **234 unique original ZIP member paths**, source-folder class totals **47/53/48/43/43**, and action counts **219/7/4/4**; verifies the 219 and 15-member CSV views are exact, nonoverlapping subsets of the original 234-row manifest.
- Checks each exact-byte hash group has a coherent one-representative rule or **fully quarantines** conflicting original folder labels; confirms the four known cross-label paths and four previously pending manual-review paths.
- Confirms no row claims human label verification or photo reuse-rights clearance, preserves Stage 2 report provenance, retains SCANIA missing counts/AI4I original records, and rejects unexpected source sets or later-stage operations.

After merging the reviewer PR, run in the same Windows PowerShell repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/review_stage3_cleaning.py --input-dir "data/processed/stage3_cleaning"
```

**Send the real read-only output** to complete the final technical review. Do **not** rerun `clean_stage3_originals.py` into the same existing output directory (it intentionally refuses overwrites). Do not commence Stage 4 Label Verification until Stage 3 manifest review and sign-off.

**Current decision:** `STAGE3_CONSERVATIVE_CLEANING_EXECUTED_REVIEW_REQUIRED`. Stage 3 is **not yet signed off**, and Kaggle image reuse rights are **not verified**. The only three approved sources are SCANIA v2, AI4I 2020 and the original industrial fault-image archive.

## Actual post-cleaning manifest review and formal Stage 3 sign-off

The owner executed the already merged **read-only** `src/preprocessing/review_stage3_cleaning.py` against the three previously generated local CSV image manifests and `stage3_cleaning_report.json`. The returned result was:

```json
{
  "status": "STAGE3_ACTUAL_CLEANING_MANIFESTS_REVIEWED_READ_ONLY",
  "stage3_report_sha256": "3f8e299a9fb70d65cf4a69463185f872e63f7777a5ca7d47e7bcc4b2c7fde186",
  "stage2_evidence_sha256": "07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67",
  "original_three_source_readouts_preserved": 1516819,
  "original_scania_sensor_missing_cells_preserved": 481376,
  "original_ai4i_rows_preserved": 10000,
  "original_ai4i_disputed_target_rows_retained": 27,
  "original_image_members_accounted_for": 234,
  "image_action_counts": {
    "exclude_same_class_duplicate": 7,
    "provisional_candidate": 219,
    "quarantine_conflicting_labels": 4,
    "quarantine_manual_review": 4
  },
  "image_original_folder_class_counts": {
    "Crack": 47,
    "Misalignment": 53,
    "Normal condition": 48,
    "Surface defects": 43,
    "Wear": 43
  },
  "original_exact_image_duplicate_groups": 9,
  "exact_cross_class_conflicting_members_quarantined": 4,
  "original_ambiguous_manual_review_members_quarantined": 4,
  "all_three_image_manifests_sha256_verified": true,
  "original_source_files_modified": false,
  "image_label_or_license_approved": false,
  "splits_or_features_created": false,
  "stage3_final_signoff_requires_review_of_this_output": true
}
```

**Meaning of the last field:** `stage3_final_signoff_requires_review_of_this_output=true` was the reviewer's deliberately cautious pre-signoff annotation. The actual return value has **now been reviewed** and this document serves as the subsequent sign-off. Do not overwrite the existing, already-fingerprinted Stage 3 output just to change its preliminary flags.

### Verified acceptance criteria

- [x] Stage 3 actual cleaning command ran successfully on the previously audited original three sources and produced derived manifest data, without modifying the original files.
- [x] The original 1,516,819 SCANIA readouts and all 481,376 missing original sensor cells are preserved, with **no imputation, clipping, feature transforms or new measurements**.
- [x] All 10,000 original AI4I records and the 27 original failure-mode/target discrepancies are retained without label changes.
- [x] Exactly 234 unique original Kaggle ZIP member references occur in the full derived manifest; original source-folder class counts **47 Crack, 53 Misalignment, 48 Normal condition, 43 Surface defects, 43 Wear**.
- [x] The 219 provisional-candidate references and 15 flagged-reference records form a valid complete, disjoint partition of all 234 originals. The 15 are **7** same-class exact duplicate references, **4** cross-class label-conflicting source-image references, and **4** already-pending manual-review references.
- [x] **Nine** original exact-byte image duplicate groups validated, with all source-folder cross-class groups quarantined, one representative per same-folder exact-byte group retained, no original labels rewritten.
- [x] All **three** derived CSV manifests were hashed and compared to the SHA-256 values originally recorded inside the actual Stage 3 cleaning JSON report. No unexpected source path, membership or hash mismatch found.
- [x] Each image manifest still marks `human_label_verified=false` and `source_photo_reuse_rights_verified=false`. The source image archive and its individual contents were not recompressed, copied, re-encoded, or distributed by this workflow.
- [x] No train/validation/test split, feature engineering, ML training, source-data augmentation, new dataset or unrelated supporting pump PDF added.

**Rights and label limitations are NOT certified away:** The 219 original-image references remain **provisional**, **not human-label-verified**, and their exact photo origins/licenses/reuse rights remain **UNVERIFIED**. Treat image redistribution and any other permission-dependent operations as blocked pending genuine permission evidence. The 27 AI4I discrepancies and original source-folder image conflicts need **Stage 4 Label Verification**; do not resolve or invent labels by assumption.

**Decision: `STAGE3_CONSERVATIVE_CLEANING_COMPLETE_WITH_DOCUMENTED_OPEN_LABEL_AND_RIGHTS_ISSUES`.** This is a technical data-cleaning sign-off only. The next permitted project stage is **Stage 4 — Label Verification**, after this documentation is merged. Stage 5 Splitting, Stage 6 Feature Engineering, Stage 7 Final Data Validation and Stage 8 Model Development are NOT started.
