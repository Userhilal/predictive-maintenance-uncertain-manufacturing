# Stage 3 — Actual conservative original-source cleaning results (2026-11-21)

**Status: OWNER EXECUTED THE SOURCE-PRESERVING CLEANING SCRIPT SUCCESSFULLY. Manifest integrity/partition read-back remains pending.**

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
