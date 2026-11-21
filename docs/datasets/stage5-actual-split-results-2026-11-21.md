# Stage 5 — Actual original-source partition execution (2026-11-21)

**Final technical decision (2026-11-21): STAGE 5 ELIGIBLE TABULAR/TELEMETRY SPLIT ASSIGNMENTS COMPLETE AND INTEGRITY REVIEWED, WITH ORIGINAL IMAGE SUPERVISION AND SCANIA CROSS-TASK MODEL READINESS EXPLICITLY BLOCKED.** The original owner-run Stage 5 JSON retains its preliminary `stage5_signed_off=false` field; this signed-off source-partition policy is recorded separately and does not overwrite the original evidence.

The owner merged the Stage 5 implementation and ran the original-source splitting script on their own unchanged, genuinely acquired three data sources using the **merged Stage 4 restricted label-eligibility policy**. These observations come from the owner's **actual terminal JSON**, not downloaded sample data or fabricated records.

The command used `src/preprocessing/split_stage5_eligible_sources.py` with original SCANIA target CSVs and source audit, the unchanged original AI4I 2020 CSV, and previously SHA-verified Stage 4 lineage evidence. Original image source ZIP bytes were neither opened nor split in this phase. Original source files were not modified; no new measurements, label edits, engineering or model fitting occurred.

## Actual Stage 5 owner terminal summary

```json
{
  "status": "STAGE5_SOURCE_RESPECTING_TABULAR_SPLIT_MANIFESTS_CREATED_REVIEW_REQUIRED",
  "scania_official_vehicles": {
    "train": 23550,
    "validation": 5046,
    "test": 5045
  },
  "scania_source_readouts_not_resplit": 1516819,
  "ai4i_eligible_original_rows": 9973,
  "ai4i_original_disputed_udis_quarantined": 27,
  "ai4i_assigned_source_rows_by_cohort": {
    "train": 6981,
    "validation": 1497,
    "test": 1495
  },
  "ai4i_source_binary_target_by_cohort": {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49}
  },
  "images_supervised_splits_created": false,
  "all_original_files_unchanged": true,
  "stage5_signed_off": false,
  "full_report": "data\\processed\\stage5_eligible_splits\\stage5_split_report.json"
}
```

### Verified summary arithmetic

| Original AI4I supervised partition | Original target 0 | Original target 1 | Total |
|---|---:|---:|---:|
| Training | 6,750 | 231 | 6,981 |
| Validation | 1,447 | 50 | 1,497 |
| Test | 1,446 | 49 | 1,495 |
| **Derived assignment total** | **9,643** | **330** | **9,973** |

Exactly **27 original contradictory UDI members** were written separately into a **quarantine reference** view, not deleted from the original 10,000-row CSV. The derived partitions sum to all 9,973 source-consistent rows. These are **publisher-synthetic AI4I observations**, not a newly synthetic dataset generated in the project. Source consistency is not independently verified failure truth.

**SCANIA official source vehicles:** 23,550 train + 5,046 validation + 5,045 test = **33,641 distinct original vehicles**, with 1,516,819 original readouts remaining in their existing source partitions (not duplicated or resplit). Original train repair-event/right-censored source targets are **not compatible out of the box** with the official validation/test source five-class outcome categories. Stage 5 produces original cohort/target lineage only, not a properly defined shared predictive task.

**Images:** All 234 original Kaggle images **remain blocked from approved supervised splitting**: none of their class labels has independent visual verification, and rights for the original photo content are not verified. Image annotation and rights issue [#43](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/43) stays open. Do not present supervised image-model accuracy or claim a usable image training split.

## Final source-only metadata review before Stage 5 technical sign-off

New `src/preprocessing/review_stage5_splits.py` inspects **only the previously created local `stage5_split_report.json` and seven derived source-reference assignment CSVs**, not raw SCANIA/AI4I files, original photo ZIPs or any external source. This review:

- Recomputes all **seven original generated assignment manifest SHA-256 digests** and compares them with those recorded by the source-run Stage 5 JSON.
- Reads all **three SCANIA original vehicle/target cohort manifests** and checks the 33,641 unique/disjoint IDs, original 23,550/5,046/5,045 source counts, the official original target domains and distinct source semantics, and nonnegative finite original train study endpoints.
- Checks **all 9,973 AI4I eligible original source UDI assignments** have valid original binary targets and types, no duplicated/cross-cohort UDI, and the original 27 UDI exclusions are fully disjoint and account for all 10,000 original IDs. Recomputes per-cohort original target/product Type/UDI-band diagnostic counts from the metadata (UDI bands are *audit-only*, not model features).
- **Reconstructs the deterministic exact seed=42 strata** from the 9,973 original UDI/target/Type manifest rows, matching the script's sorted original UDI order, per-stratum seeded shuffle and 70/15/15 within-stratum rounding. This checks every eligible row's cohort assignment rather than only aggregate totals; it **does not re-run Stage 5 against original raw source data** or write a new split.
- Rejects any false assertion of permission-cleared images, source label edits, model training, feature engineering, fourth datasets, or a unified SCANIA binary/5-class outcome task.

After merging the review PR, run from the existing Windows repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/review_stage5_splits.py --input-dir "data/processed/stage5_eligible_splits"
```

**No need to run `split_stage5_eligible_sources.py` again.** The original local Stage 5 output is intentionally write-once; do not overwrite it. Send the actual read-only JSON for final review.

### Strictly scoped acceptance decision

- [x] Real owner-local original-source Stage 5 splitting executed successfully.
- [x] Initial source-size arithmetic and full original cohort/AI4I exclusion totals reconcile to original Stage 4 eligibility policy.
- [x] Zero supervised image partitions generated and source files/labels reported unchanged.
- [ ] All seven original Stage 5 CSV hashes, original source vehicle/UDI partitions and exact AI4I seeded assignment membership reverified by the owner-local read-only reviewer.
- [ ] Source-specific limitations and risk-qualified Stage 5 **tabular/telemetry-only partition sign-off** formally documented; **not** a full supervised three-source multimodal-ready split.

**Stage 5 is not fully signed off yet.** No Stage 6 feature engineering, Stage 7 final data certification or Stage 8 model development is authorized by this preliminary result.

## Actual owner-executed final Stage 5 assignment integrity review

The owner ran the **fixed**, merged `review_stage5_splits.py` on the existing local Stage 5 original-source assignment metadata and provided the complete terminal JSON:

```json
{
  "status": "STAGE5_ACTUAL_SOURCE_SPLIT_MANIFESTS_REVIEWED_READ_ONLY",
  "original_stage5_report_sha256": "9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda",
  "original_stage4_report_sha256": "c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29",
  "all_seven_original_assignment_csv_sha256_verified": true,
  "scania_official_partition_vehicles": {
    "train": 23550,
    "validation": 5046,
    "test": 5045
  },
  "scania_original_repair_censor_and_five_class_tasks_kept_distinct": true,
  "original_scania_readouts_not_resplit": 1516819,
  "ai4i_eligible_original_udi_count": 9973,
  "ai4i_quarantined_original_udis": 27,
  "ai4i_original_eligible_partition_counts": {
    "train": 6981,
    "validation": 1497,
    "test": 1495
  },
  "ai4i_original_target_counts_per_partition": {
    "train": {"0": 6750, "1": 231},
    "validation": {"0": 1447, "1": 50},
    "test": {"0": 1446, "1": 49}
  },
  "ai4i_original_product_type_counts_per_partition": {
    "train": {"H": 699, "L": 4189, "M": 2093},
    "validation": {"H": 150, "L": 898, "M": 449},
    "test": {"H": 149, "L": 897, "M": 449}
  },
  "ai4i_exact_seeded_class_type_assignment_reconstructed": true,
  "ai4i_all_10000_original_udi_references_accounted": true,
  "images_supervised_partitions_created": false,
  "image_original_labels_or_reuse_rights_verified": false,
  "original_source_files_or_labels_modified": false,
  "stage5_signoff_requires_review_of_this_output": true
}
```

The original Stage 5 report fingerprint `9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda` is the actual owner-reported local evidence hash (not an independent publisher signature). The four-stage original provenance links remain: Stage 4 report `c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29`, Stage 3 and 2 original-report fingerprints recorded in prior reports. The reviewer verified **all seven CSV SHA-256 values in the report** and the original source assignment membership.

### Final exact acceptance checks

- [x] SCANIA exactly **33,641** unique, non-overlapping source vehicle target metadata references across **23,550 train / 5,046 validation / 5,045 test**; **1,516,819** original readouts **not resplit**; train repair/right-censoring target remains semantically distinct from val/test five-class targets.
- [x] AI4I **9,973** source-consistent original UDI references each in exactly one split, **27** disputed original UDI references in a separate nonoverlapping quarantine. All **10,000** original UDIs accounted for.
- [x] Original eligible AI4I failure-target counts **9,643 source negatives** and **330 source positives** reconcile across train, validation and test; no source target bit-flips or rows physically removed from original.
- [x] Original AI4I source `Type` (H/L/M) split counts checked: train **699/4,189/2,093**, validation **150/898/449**, test **149/897/449**. Totals **H=998, L=5,984, M=2,991**, or **9,973** eligible rows; do not conflate these with original 10,000-row Type counts, as the 27 quarantined UDIs are not assigned.
- [x] **Exact original AI4I UDI-to-partition assignment** reproduced from existing derived UDI/Type/target manifest using original deterministic seed=42, target+Type strata and recorded proportions; no overlap or incompatible source class/Type.
- [x] **All seven** existing derived CSV manifest SHA-256 values matched those originally written by the Stage 5 run. Stage 5 reviewer ran **read-only**: it neither reprocessed original source CSV files nor rewrote the resulting assignment files.
- [x] **Zero supervised Kaggle image partitions** produced; **all 234** original image references remain blocked from verified-label supervised image splitting, training and evaluation pending independent visual annotation and genuine rights/provenance evidence tracked in issue #43.
- [x] No source files, original source labels or source image bytes modified; no new datasets or external pump PDFs, no fabricated machine/field observations, no feature engineering, no scaling/imputation, and no model trained.

### Exact boundary and final decision

**Technical sign-off:** `STAGE5_ELIGIBLE_TABULAR_SOURCE_PARTITIONS_COMPLETE_WITH_IMAGE_AND_TASK_RESTRICTIONS`.

This means **eligible tabular/telemetry source partitioning is verified**: the original SCANIA cohort assignment is preserved and the original AI4I source-consistent supervised benchmark memberships are validly assigned. It does **not** mean:
- SCANIA's original **right-censored train time-to-repair** task has a model-ready target/evaluation contract equivalent to its official five-class val/test source labels. Task-specific endpoint/censoring and evaluation compatibility must be resolved **before claiming performance on a unified SCANIA model**.
- AI4I is longitudinal real manufacturing data or that an IID random split proves future-time or out-of-factory generalization. The 9,973 rows remain **originally publisher-synthetic**, source-internally consistent, not independently ground-truth-certified.
- The original Kaggle fault images are approved for supervised training/evaluation. They are **NOT**. Exact source class quality, individual image permissions, and image rights remain unresolved; issue #43 is an independent hard gate. No user-supplied photo pixels were redistributed.
- The three independent data sources contain real same-machine linked data. They **do not have verified cross-source machine pairing**, so do not pretend that a SCANIA readout is linked to an AI4I label or a Kaggle defect photo.

The owner-run Stage 5 viewer reports `stage5_signoff_requires_review_of_this_output=true` because it ran *before* human review. Its complete output has now been reviewed; this document is the **separate post-review technical sign-off**, not a modification of the original local report.

**Next sequential phase after merging this sign-off:** Stage 6 — Feature Engineering can be prepared only for **the eligible, already partitioned original AI4I tabular data**, with **train-only learned transforms** and no leakage from the original AI4I failure mode flags or source identifiers. SCANIA original cohort/telemetry feature processing may be source-safe, but a unified supervised target/performance claim requires independently defined task compatibility and censor handling. All image feature learning for supervised use remains blocked pending issue #43. No Stage 6 work occurred in Stage 5.
