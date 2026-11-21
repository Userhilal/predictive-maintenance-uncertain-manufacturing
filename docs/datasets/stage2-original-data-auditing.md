# Stage 2 — Original-source Data Auditing, exactly three datasets

**Status: AUDIT IMPLEMENTATION PREPARED; ACTUAL CONSOLIDATED OWNER-RUN RESULTS REQUIRED.** Stage 1 original-file collection is complete and signed off. This stage does **not** clean, correct, delete, relabel, split, engineer features, train a model, or download any other data.

The only approved sources:

1. **SCANIA Component X v2**: original nine CSVs plus original two SCANIA-package PDFs, from [Researchdata](https://researchdata.se/en/catalogue/dataset/2024-34/2).
2. **AI4I 2020**, the unchanged Mendeley V1 original [dataset](https://data.mendeley.com/datasets/5ww3zv87y7/1), **synthetic as published**.
3. **Industrial Machinery Fault Image Dataset**, the original 234-image [Kaggle source archive](https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data).

No independent `pump.pdf`, `pumplcc_1001.pdf`, fourth dataset, generated factory telemetry, simulated failure histories or invented source images may be used. No claim that different datasets describe the same machine.

## Why another audit when previous scripts exist?

The owner previously ran the genuine SCANIA raw CSV audit: **33,641** original vehicles across **1,516,819** original operational readouts; known missingness, repair/right-censoring status, original vehicle/target link checks and source split separation. Separately, the previous AI4I and image preparation documents describe observed faults, but their existing *preparation* scripts also create provisional train/validation/test files. **Those splitting/cleaning decisions belong to future stages**, not this data-auditing stage.

The new `src/preprocessing/audit_stage2_quality.py` runs only source-audit/read routines from those modules. It checks the actual existing Stage 1 verified inventory, the actual original SCANIA audit, the original AI4I CSV and original Kaggle ZIP **without generating splits**.

## Checks to perform on actual source files

| Source | Exact Stage 2 checks | What they do not conclude |
|---|---|---|
| SCANIA | Confirm verified prior source audit, original SCANIA source fingerprints recorded in Stage 1 and linked to that original audit; check 3 actual split counts, sensor missing cells/feature rates, malformed values, adjacent time ordering, and real recorded repair/label counts | Not manufacturing factory histories, not hours, no physically confirmed failure at each repair, no independently certified publisher SHA |
| AI4I | Re-read the **entire original 10,000-row CSV** and validate original source hash, schema, numeric values, missingness, UDI uniqueness, Product ID uniqueness, Type and target distributions, source mode-flag conflicts, actual numeric min/max and UDI-band imbalance | 27 previously noted source target/mode inconsistencies are not silently corrected, and source-synthetic data do not prove real production performance |
| Kaggle images | Re-read the **unchanged original ZIP**; validate SHA, structure, decoding/dimensions, source-folder class counts, exact-byte duplicate groups (including conflicting class folders), very small images, file extension/content mismatches, and **dHash-based near-duplicate candidates** to investigate | dHash similarity does not prove identical source photos or validate true defect labels; original equipment instance, individual-photo licenses and origins remain unknown |

**Interpretation rule:** Numerical extremes, missing cells, conflicting target flags and duplicate-image candidates are *findings*, not instructions to change original data. No cleaning/removal in Stage 2, no source relabeling in Stage 2, and no split assignment. These decisions are reserved for Stage 3 Data Cleaning, Stage 4 Label Verification, and Stage 5 Data Splitting, respectively.

Image perceptual similarity is a **review heuristic**: 64-bit difference hashing at Hamming distance <=5 between representative nonidentical exact-byte groups. It can both miss crops/transforms and flag unrelated visually simple images. The report records a bounded list of candidates, their total count and whether output was truncated; it never auto-excludes, relabels, or matches images to sensor records.

## Run on the already-collected three original datasets

From the same Windows PowerShell project root after the PR is merged:

```powershell
git pull origin main

py -3.11 -c "from PIL import Image; print('Pillow installed')"
```

Only if Pillow is missing (a Python library, **not** new data), run:

```powershell
py -3.11 -m pip install Pillow
```

Run the Stage 2 source-only audit:

```powershell
py -3.11 src/preprocessing/audit_stage2_quality.py --stage1 "data/processed/stage1_collection_inventory_verified.json" --scania-audit "data/processed/scania_audit.json" --ai4i "data/raw/ai4i2020.csv" --images "C:\Users\hindh\Downloads\archive.zip" --output "data/processed/stage2_original_data_quality.json"
```

The script reads no other datasets. It writes exactly one local, Git-ignored source audit report and prints a compact summary. The JSON stores measured counts and **original image archive paths only**, never uploaded image bytes. No CSV/PDF/ZIP is changed; source files are not committed to GitHub. Existing output file is never overwritten. The cached SCANIA raw-file report was previously directly executed on the owner's nine actual source CSVs; Stage 2 **does not rerun the 1.5-million-readout full SCANIA pass** because Stage 1 already verified all nine original raw-file hashes against that actual earlier audit.

The compiled Python syntax workflow does **not** validate the user's underlying datasets. Do not claim measured Stage 2 results before the owner executes the script on local originals.

## Stage 2 acceptance gates

- [ ] Owner runs actual consolidated source-only audit and provides the real terminal output.
- [ ] Original SCANIA population, missing sensor counts and three-split integrity reconciled.
- [ ] Actual AI4I full-source quality summary reviewed, especially class imbalance, UDI concentration, target/failure-mode mismatch and original published synthetic status.
- [ ] All 234 original Kaggle images audited; exact duplicates, cross-label duplicates, image resolution, extension-content mismatch, and perceptual candidates documented **without changing labels or deleting data**.
- [ ] Explicit disclosure of unverified third-party publisher hashes and **Kaggle image rights / provenance**. If permitted usage cannot be established, restrict affected image operations accordingly; do not claim public redistribution rights.
- [ ] Create a source-specific **audit sign-off with disclosed risks and review queues**, reserving resolution of cleaning choices to Stage 3, label decisions to Stage 4, splits to Stage 5 and feature transformations to Stage 6. Never silently call unresolved image labels “correct”.

**Decision now:** Stage 2 **OPEN**. Do not proceed to Stage 3 until this real-source audit report is evaluated. In particular, the audit script does not certify complete usage permissions for Kaggle photographs or independently published SHA fingerprints.
