# Stage 5 — Actual original-source partition execution (2026-11-21)

**Status: STAGE 5 SOURCE-RESPECTING SPLIT ASSIGNMENT EXECUTED SUCCESSFULLY BY OWNER; FULL MANIFEST INTEGRITY REVIEW PENDING.**

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
