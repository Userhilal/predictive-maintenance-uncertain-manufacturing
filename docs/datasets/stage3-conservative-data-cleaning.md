# Stage 3 — Conservative data cleaning for exactly three original sources

**Status: ACTUAL OWNER-RUN STAGE 3 CLEANING EXECUTED SUCCESSFULLY; MANIFEST INTEGRITY REVIEW STILL PENDING.** The owner's observed local outcome is recorded in [actual Stage 3 cleaning results](stage3-cleaning-results-2026-11-21.md). No original data bytes were changed. Formal Stage 3 sign-off awaits a read-only verification of the generated three CSV manifests.

The owner finished Stage 1 Data Collection and Stage 2 technical Data Auditing using **exactly three sources**. Stage 2 source-audit report was produced from real original bytes and its SHA-256 was verified by the owner through the read-only reviewer: `07fa57306fd93f09bb2ba28ebecb1be7526043503aacb1991478da42073eab67`. The Stage 2 technical sign-off is documented in [the actual real-source audit results](stage2-audit-results-2026-11-21.md). Source-image licenses, exact individual origins, and re-use rights remain unverified; no new data are to be collected.

**Only approved datasets (NO independent external pump PDFs):**

1. SCANIA Component X v2 original nine CSVs + two PDFs that belong to the original SCANIA source.
2. AI4I 2020 original 10,000-row published-synthetic dataset from user-supplied Mendeley archive.
3. Industrial Machinery Fault Image Dataset original 234-image user-supplied Kaggle ZIP.

## Policy and actual transformation scope

| Source | Stage 2 observed problem | Conservative Stage 3 handling | Reserved for later |
|---|---|---|---|
| SCANIA | 481,376 originally absent sensor cells across 1,516,819 original readouts, 105 sensors and all three original source splits | **Retain missing as missing** (no invented value or global mean fill). No outlier clipping, row dropping, feature scaling, source target/censor changes. Same 33,641 vehicles and original readout counts | Stage 4 event/censor definitions, Stage 5 group/split handling, Stage 6 *train-fit-only* feature transformations/model-native handling |
| AI4I 2020 | No source missing cells or duplicate feature vectors, but 339/10,000 positives and 27 original global-failure vs mode-flag discrepancies | **Keep every unchanged original row**. No target correction, no 27-row exclusion, no resampling/oversampling, no normalization, no identifier-driven synthetic trajectories | Stage 4 independent source label decisions; Stage 5 split/generalisability |
| Kaggle images | 234 original images; 9 exact duplicate groups; 2 contradictory cross-folder-label duplicate groups (4 source files); four manually flagged ambiguity/provenance examples | **Generate a non-destructive image manifest**, not copied or repackaged images: choose one deterministic path from each same-class exact-byte group (7 duplicate *references* excluded); quarantine both members of each cross-class exact-byte group (4) and 4 already-pending manual-review items; **219 provisional candidate references**. Preserve original bytes, labels, dimensions and formats. No class reassignments. The two filename/format mismatches remain as accurately documented source metadata | Stage 4 label checking and human approval, source rights; Stage 5 leakage-safe image splits; Stage 6 visual features |

These dispositions are not a claim that every image is correct or licensed. The 219 candidate references **must not be represented as permission-cleared, human-verified or ready for an approved classifier**, and the 15 excluded/quarantined members are **not physically removed from the source ZIP**. Suspected near-duplicates outside the exact-byte groups remain a known limitation of the earlier dHash <=5 heuristic.

### Source-image row-accounting invariant

| Action written in full manifest | Original ZIP member count |
|---|---:|
| `provisional_candidate` (retained source references, pending quality/rights approval) | 219 |
| `exclude_same_class_duplicate` (one representative retained per exact-byte original same-class group) | 7 |
| `quarantine_conflicting_labels` (2 identical-byte groups assigned two different original classes) | 4 |
| `quarantine_manual_review` (4 earlier source ambiguities) | 4 |
| **All original source members accounted for** | **234** |

The four previously flagged source paths are `Dataset/Crack/1_.jpg`, `Dataset/Misalignment/1_.jpg`, `Dataset/Normal condition/11_.jpg`, `Dataset/Wear/4_.jpg`; their review statuses remain **pending**. No Stage 4 adjudications are permitted in the Stage 3 script. The original cross-class paths are `Dataset/Crack/29_.jpg`↔`Dataset/Wear/29_.jpg` and `Dataset/Surface defects/24_.jpg`↔`Dataset/Wear/21_.jpg`.

The Stage 3 script delegates raw image decoding/byte hashing to the already source-audited `read_images` routine and reuses `assign_review_status` **without calling the image splitting function**. All source class-folder labels remain unchanged.

## Run against the unchanged, actual original sources

First merge the Stage 3 code PR, then from the cloned project root in PowerShell:

```powershell
git pull origin main

py -3.11 src/preprocessing/clean_stage3_originals.py --stage2 "data/processed/stage2_original_data_quality.json" --scania-audit "data/processed/scania_audit.json" --ai4i "data/raw/ai4i2020.csv" --images "C:\Users\hindh\Downloads\archive.zip" --review-file "docs/datasets/fault-image-manual-review.csv" --output-dir "data/processed/stage3_cleaning"
```

Pillow is already installed on the owner's Python 3.11, from Stage 2. No additional datasets, synthetic examples, or pump guides required.

**Output (Git-ignored local derived metadata only):**

- `data/processed/stage3_cleaning/stage3_cleaning_report.json`: three-source cleaning policy/result, original report fingerprint, original image action counts, manifest hashes, and explicit limitations.
- `data/processed/stage3_cleaning/original_images_full_action_manifest.csv`: one row for **each of the 234 original ZIP members** with image hash, original folder label and cleaning action. **This is a manifest, not image pixels.**
- `data/processed/stage3_cleaning/image_provisional_candidates_219.csv`: the 219 retained original-member references, **not** a final license-cleared/human-reviewed dataset.
- `data/processed/stage3_cleaning/image_quarantine_and_exact_duplicates_15.csv`: the 15 independently recorded source issues/duplicates without deleting anything.

**Explicit guarantees:** Original SCANIA CSV/PDF, AI4I CSV and Kaggle ZIP remain unchanged; no source-row drop, imputation, scaling, balancing/oversampling, synthetic values, actual original-image file format conversion, image relabeling, split assignment, model training or independent extra datasets. The cleaning manifest is a **derived selection view only**.

The script refuses to overwrite a pre-existing output directory, verifies the exact owner-reviewed Stage 2 report SHA, rechecks the original AI4I CSV SHA, original image ZIP SHA and source row counts, and checks every quarantined/repeated image count. On error, partial temporary outputs are cleaned without replacing any source or earlier evidence.

## Stage 3 exit criteria

- [x] Owner executed conservative Stage 3 on the same originals and pasted the actual successful terminal JSON with all expected original row and image-status counts.
- [ ] Source SCANIA 33,641 vehicles/1,516,819 original readouts and 481,376 genuinely missing sensor values preserved; clearly documented **no imputation** policy.
- [ ] Source AI4I original 10,000 records/339 original positives preserved with 27 source disagreements left for Stage 4.
- [ ] Exactly 234 original image ZIP members accounted for: 219 provisional references, seven same-class exact-copy references, four cross-label duplicate records and four manual-review records. Cross-class labels **not changed**.
- [ ] Original-image rights/provenance **still not verified**; no usage permission, training-readiness or redistribution claim.
- [ ] Output manifests/report reviewed and Stage 3 cleaning policy/result signed off, **not** mistaken for Stage 4 label sign-off or Stage 5 train/test split readiness.

**Current decision:** Stage 3 original-source-preserving cleaning **EXECUTED SUCCESSFULLY** on owner's originals, but formal completion is pending **read-only integrity review** of generated manifests and report fingerprints; no Stage 4 activity yet. Merge the results reviewer PR and run `py -3.11 src/preprocessing/review_stage3_cleaning.py --input-dir "data/processed/stage3_cleaning"`. Do not rerun cleaning or overwrite the actual output.
