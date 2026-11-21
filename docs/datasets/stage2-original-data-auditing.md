# Stage 2 — Original-source Data Auditing, exactly three datasets

**Status: STAGE 2 TECHNICAL AUDIT COMPLETE WITH DOCUMENTED OPEN ISSUES (2026-11-21).** Owner executed the source audit and the read-only detailed report reviewer on genuine original files. This audit-only sign-off does not certify image rights, correct conflicting labels, or clean source data; see [actual review and sign-off](stage2-audit-results-2026-11-21.md). See [actual user-run Stage 2 results and risk register](stage2-audit-results-2026-11-21.md). Stage 1 original-file collection is complete and signed off. This stage does **not** clean, correct, delete, relabel, split, engineer features, train a model, or download any other data.

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

## Review existing actual report without re-running heavy source audits

After the owner has executed the Stage 2 audit successfully, print the remaining important factual source-quality details with the read-only helper:

```powershell
py -3.11 src/preprocessing/review_stage2_report.py --input "data/processed/stage2_original_data_quality.json"
```

This command does **not** rerun SCANIA's million-plus original readouts, re-open the 234 image sources, or rewrite/overwrite the existing Stage 2 JSON. It prints the existing observed SCANIA per-split missingness/event counts, original AI4I numeric ranges and UDI concentrations, and Kaggle per-class image counts, small-image totals, exact conflicting source-folder filenames and file extension/content anomalies. Share the actual output for the final quality-gate review. Its report SHA-256 establishes which local Stage 2 evidence was summarized.

## Stage 2 acceptance gates

- [x] Owner ran the genuine consolidated source-only audit and provided the real terminal output on 2026-11-21 (33,641 SCANIA vehicles; 10,000 AI4I rows; 234 original images).
- [x] Original SCANIA population, missing sensor counts, source target counts and three-split integrity reconciled with the actual owner-read report.
- [x] Original AI4I full-source quality summary reviewed, including original label counts, numeric limits, UDI concentration, 27 contradictions and published synthetic status.
- [x] All 234 original Kaggle images audited; exact duplicates, cross-label duplicates, image resolution, extension-content mismatch and heuristic dHash candidates documented **without changing labels or deleting data**.
- [x] Explicit disclosure of unverified third-party publisher hashes and **Kaggle image rights / provenance**; permission-dependent image activities and public redistribution remain gated on actual usage-rights evidence, not declared approved.
- [x] Source-grounded **technical audit sign-off with disclosed risks and review queues** published, reserving cleaning for Stage 3, label decisions for Stage 4, splits for Stage 5 and transformations for Stage 6. No unverified image label was called correct.

**Decision now:** Stage 2 **TECHNICAL AUDIT COMPLETE WITH DOCUMENTED OPEN ISSUES**; open risks remain explicitly unresolved. Next Stage 3 — Data Cleaning, *only after sign-off PR merge*. Do not proceed to Stage 3 until this real-source audit report is evaluated. In particular, the audit script does not certify complete usage permissions for Kaggle photographs or independently published SHA fingerprints.
