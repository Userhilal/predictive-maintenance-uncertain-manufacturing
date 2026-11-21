# Stage 5 — Source-respecting Data Splitting (eligible source cohorts only)

**Status: STAGE 5 ELIGIBLE TABULAR/TELEMETRY SOURCE PARTITIONING TECHNICALLY COMPLETE AFTER OWNER-RUN SEVEN-MANIFEST INTEGRITY REVIEW (2026-11-21).** No image supervised partition or unified SCANIA task is approved. Full actual results and final restrictions: [Stage 5 source-partition sign-off](stage5-actual-split-results-2026-11-21.md). Actual terminal results, source limitations and the read-only final review gate are recorded in [Stage 5 genuine owner-run results](stage5-actual-split-results-2026-11-21.md). Stage 4 original-source label-lineage integrity has been signed off **only with strict restrictions**, and issue #43 remains open for original fault-image visual labels and reuse rights. No new datasets are authorized.

## Three original sources only

1. **SCANIA Component X v2:** original 9 CSVs, the same-source 2 PDFs; original publisher train/validation/test vehicle cohorts **must not be reshuffled**.
2. **AI4I 2020:** unchanged Mendeley original **publisher-synthetic** 10,000 records, of which **27 original source target/mode-discordant UDIs** must be absent from all future supervised binary target partitions.
3. **Industrial Machinery Fault Images:** unchanged 234-image Kaggle archive; **no supervised image split may be generated** because individual photo reuse rights and independent true visual class labels have not been established. Image label/rights issue [#43](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/43) stays open.

No fourth source, separate pump PDFs, synthetic fake rows/photos, or invented paired image/telemetry machine samples.

## Source-defined Stage 5 contract

| Source | Stage 5 action | Why this approach |
|---|---|---|
| SCANIA | Preserve the original **23,550 train / 5,046 validation / 5,045 test** vehicle cohorts verbatim. Create **three local metadata manifests** mapping original `vehicle_id` to **the source-designated cohort** and existing original target/repair endpoint only. Original source target CSVs are SHA-reconciled to the owner-run raw Scania audit, and all original vehicle IDs are checked for cohort nonoverlap. | Avoid splitting readouts from the same vehicle across different model cohorts. SCANIA's original train `in_study_repair` **repair-event/right-censor labels are not interchangeable** with original validation/test `class_label` **five-class** labels. These manifests preserve native tasks; **they are not yet a unified classification benchmark.** |
| AI4I | Use the original `UDI` queue from the SHA-verified Stage 4 27-case dispute report to **exclude exactly those original 27 UDI rows** from all derived label-sensitive supervised split assignments. Split only the remaining **9,973 original rows** (9,643 original negative, 330 original positive), with deterministic seed 42, stratified by **original `Machine failure` and original `Type`**, into 70% train / 15% validation / 15% test (rounded within each stratum). | Preserve original source class imbalance and product-type mix while keeping disputed source labels out of supervised evaluation. `UDI`, `Product ID`, and the source `TWF/HDF/PWF/OSF/RNF` failure-mode flags are **not prediction input features**; they are identifiers/leakage-sensitive labels. This is an **IID-like original synthetic benchmark**, NOT a time-ordered, real-machine or cross-factory generalization claim. |
| Kaggle images | **No supervised image cohort assignments.** Include only a factual blocked-state record in the Stage 5 JSON, with 234 original references and all original 219 provisional folder labels understood as non-expert verified. | Unverified true defect labels, ambiguous original photo classes and image reuse rights; source-folder names alone cannot certify the image label or legal usability. |

### Critical SCANIA distinction

SCANIA source `train_tte.csv` is a **time-to-repair / right-censored source task**, while `validation_labels.csv` and `test_labels.csv` are original **five-class** repair-proximity categories. **Do not train a simple binary `in_study_repair` classifier and claim it was validly tested against the five-category validation/test labels.** Stage 5 preserves the official vehicle assignments; any legitimate task-specific target construction, prediction horizon, censor treatment and evaluation compatibility requires a **separately justified later task definition**. SCANIA source `time_step` must not be treated as hours without provider support.

### AI4I label exclusion invariants

- Original `Machine failure=0`: **9,661**, minus **18** disagreement UDIs = **9,643** source-consistent candidate negatives.
- Original `Machine failure=1`: **339**, minus **9** disagreement UDIs = **330** source-consistent candidate positives.
- **9,973** eligible original source rows, each UDI assigned **exactly one** future split.
- Exactly **27** disputed source UDIs retained in an explicit `ai4i_quarantined_27_source_udis.csv` reference manifest; none appears in the 9,973 assignments.
- Original 10,000-row CSV and original flags remain unchanged and available for audit, with no source target corrections.
- The strata are source original **binary label + Type**. The report includes per-split Type counts and UDI 1,000-band positive counts for diagnostics only, **never model features**. The 4001–5000 UDI original concentration noted in Stage 2 remains a distribution/generalizability limitation and should not be falsely interpreted as time.
- A seeded IID-style split can provide a reproducible internal baseline, but **does not** prove future-machine reliability, site transfer or realistic chronology. No learned scaling/imputation/feature engineering occurs in Stage 5.

The machine-readable Stage 4 prerequisite is [the previously signed-off source eligibility policy](stage4-label-eligibility-policy.json). The script validates this policy against the **actual owner-run Stage 4 JSON fingerprint** `c0c32dc6d523a7e67a2e1ec0ed01b01f0ddb4798c671836d2af97717ed56db29` and reruns the Stage 4 *read-only metadata reviewer* to ensure all original queue CSV SHA-256 values still match. It validates AI4I original SHA-256 and the 27 true source mismatches, then creates only **local assignment/label-provenance metadata**, not source image pixels or feature matrices.

## On Windows, run after merging the PR

From the project root:

```powershell
git pull origin main

py -3.11 src/preprocessing/split_stage5_eligible_sources.py --scania-data "C:\Users\hindh\Documents\2024-34-2\data" --scania-audit "data/processed/scania_audit.json" --ai4i "data/raw/ai4i2020.csv" --stage4-dir "data/processed/stage4_label_verification" --policy "docs/datasets/stage4-label-eligibility-policy.json" --output-dir "data/processed/stage5_eligible_splits"
```

No extra Python dependencies or data-source downloads. The script refuses to overwrite an existing Stage 5 output folder and writes using an atomic staging directory. The following **Git-ignored** derived files should appear only after a successful owner-local run:

| File | Purpose |
|---|---|
| `stage5_split_report.json` | Source fingerprints, SCANIA official cohort counts/labels, AI4I eligible split counts/diagnostics, image restriction status, derived CSV SHA-256 |
| `scania_official_train_vehicle_targets.csv` | All original train vehicle IDs and original `in_study_repair` plus recorded `length_of_study_time_step` |
| `scania_official_validation_vehicle_targets.csv` | All original validation vehicle IDs and original five-class labels |
| `scania_official_test_vehicle_targets.csv` | All original test vehicle IDs and original five-class labels |
| `ai4i_train_eligible_udi_assignments.csv` | Only eligible original AI4I UDI + original target + source Type, assigned to train |
| `ai4i_validation_eligible_udi_assignments.csv` | Only eligible original AI4I UDI + original target + source Type, assigned to validation |
| `ai4i_test_eligible_udi_assignments.csv` | Only eligible original AI4I UDI + original target + source Type, assigned to test |
| `ai4i_quarantined_27_source_udis.csv` | Excluded original source UDIs and unchanged original mismatch evidence |

**Do not run the old** `prepare_ai4i.py` or `prepare_fault_images.py` **as data-splitting entrypoints:** those historical scripts may create provisional partitions without the current Stage 4 eligibility policy. Stage 5 must enforce the 27-UDI AI4I quarantine and image split block.

## Exit checks

- [x] Owner merged Stage 5 PR #44 and successfully ran the split manifest generator on real, unchanged original data (2026-11-21).
- [x] All 33,641 SCANIA official original vehicle memberships and original source labels preserved, all cohorts disjoint; 1,516,819 original readouts **not resplit or reproduced**.
- [x] All 9,973 source-consistent AI4I UDIs appear **once** across supervised partitions, each split retaining both binary failure labels; none of the 27 disputed UDIs appears.
- [x] AI4I original source-negative/source-positive and H/L/M Type counts were reconciled within split and reconstructed exactly using the class+Type seeded assignment; source mode flags/UDIs/identifiers are not approved predictive features. This assignment script **did not create feature matrices**.
- [x] Exactly **zero** supervised image splits created; no image rights/class approval asserted. Image evidence issue #43 remains OPEN.
- [x] Owner's actual read-only review verified **all seven** derived CSV SHA-256 digests, unique/disjoint source IDs, source label counts, and **exact AI4I seeded original UDI-to-split assignments**. Actual Stage 5 local report SHA-256 `9bb0db903ee0490cd543ea592ef4773819af58ad57016e6dea3ca7cc86894cda`.
- [x] No original source bytes/labels modified, no fake data or extra datasets, no derived sensor features, no model trained.
- [x] Stage 5 technically signed off **only as eligible tabular/telemetry source partitioning**, not a full supervised three-source multimodal split. Image training/supervised split remains blocked by issue #43 and SCANIA train-vs-val/test target tasks remain distinct.

**Final decision:** `STAGE5_ELIGIBLE_TABULAR_SOURCE_PARTITIONS_COMPLETE_WITH_IMAGE_AND_TASK_RESTRICTIONS`. Stage 6 **not yet started**. It may prepare eligible AI4I source training-only transforms, but must not claim a unified supervised SCANIA target or run supervised fault-image transforms/training without the missing original rights and verified image label evidence. Owner's preliminary local report and 7 manifest SHA-256 fingerprints remain untouched.
