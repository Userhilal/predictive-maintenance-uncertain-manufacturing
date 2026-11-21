# Stage 1 — Original Data Collection closure checklist

**Scope:** Finish Stage 1 before starting Stage 2. The project uses **exactly three approved data datasets** (SCANIA Component X v2, the original user-supplied AI4I 2020/Mendeley records, and the original Kaggle fault-image archive). Technical PDFs are supporting **documents**, not fourth datasets or source-matched SCANIA maintenance histories.

**Current decision:** The three sources are previously documented and their originals were processed in earlier owner-run audits, but a **single current local collection inventory has not yet been executed**. Do not declare full Stage 1 sign-off from a list of URLs alone.

## Source register — what can be established from earlier actual evidence

| Approved source | Original acquisition evidence in project | Reference | Rights/provenance limit |
|---|---|---|---|
| SCANIA Component X v2 | Owner successfully ran genuine nine-original-CSV audit and subsequent indexed real-readout pipeline; 33,641 source vehicles and 1,516,819 recorded readouts | https://researchdata.se/en/catalogue/dataset/2024-34/2 | Original provider lists **CC BY 4.0**. The dataset's **nine CSVs and two original documentation PDFs** should be inventoried separately. SHA-256 values from the owner-run audit are not independent provider-signed checksums |
| Mendeley AI4I 2020 V1 | The unchanged previously uploaded/extracted `ai4i2020.csv` had 10,000 records and SHA-256 `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e` in the project data-preparation record | https://data.mendeley.com/datasets/5ww3zv87y7/1 | Mendeley record lists **CC0 1.0**. The original AI4I benchmark is **publisher-synthetic**, not real factory measurements. This Mendeley record re-describes AI4I originally available from UCI; do not claim independently authenticated upstream original authorship |
| Industrial machinery fault images | Existing owner-audited unchanged ZIP fingerprint `d30ffdcdcda1258ac95d89dd90539fe7ffd7b398e693ada652b4f63c073c9b28`; 234 original image entries | https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data | **Exact dataset license and individual photo rights are not verified.** Kaggle availability does not certify ownership. Do not redistribute or present the images as rights-cleared. Review labels, duplicates and provenance only at their later agreed stages |

SCANIA provider's original version-2 listing includes:
- Nine original source CSVs (three each for train/validation/test).
- **`2024_IDA_challenge_v2.pdf`** and **`Scania_component_X_PdM.pdf`** original supporting documentation PDFs.
- The source record explicitly lists CC BY 4.0, provided attribution terms are respected.

These source facts were checked against the listed official Researchdata v2 and Mendeley V1 publisher records on **2026-11-21**. The precise original Kaggle dataset licensing could **not** be independently confirmed from the readable source; do not invent it.

The previously mentioned pump technical manuals, if collected separately, are **independent supporting PDF documents**, not a fourth machine-sensor dataset and not documented as joined to SCANIA vehicle histories. Their actual local filenames, provenance, reuse conditions and SHA-256 still need a separate inventory. Providing `--supporting-pdf` paths in the script records local presence and hashes only, **not** independent permission or content validation.

## Stage 1 evidence-only inventory script

`src/preprocessing/audit_stage1_collection.py` reads local **existing, unmodified** data originals and already owner-generated original SCANIA audit report.

It checks:
- All **nine** SCANIA version-2 CSV files exist and match every previous owner-run original raw CSV SHA-256 fingerprint.
- Both SCANIA source documentation PDF files exist and have a PDF header (basic file-level check only, not OCR or content validation).
- The original previously source-audited **AI4I CSV** matches its actual prior source fingerprint and has the original 14-column CSV header.
- The original previously source-audited **Kaggle ZIP** matches the prior source fingerprint, contains 234 original file members under the expected five class folders, has unique safe paths and passes ZIP CRC checks. This does **not** evaluate image labels or resolve rights.
- Optionally records existing machine/manual PDFs (source file name, byte size, local hash and PDF header), without creating any new document or source data.

It **does not download, replace, generate, clean, split, train on, or fabricate any source data**. No external files are uploaded, no raw CSVs/images are added to GitHub, and no predicted model performance is asserted.

## Run once on the actual original files

From the cloned repository in PowerShell, after merging the PR:

```powershell
git pull origin main

py -3.11 src/preprocessing/audit_stage1_collection.py --scania-data "C:\Users\hindh\Documents\2024-34-2\data" --scania-audit "data/processed/scania_audit.json" --ai4i "data/raw/ai4i2020.csv" --images "data/raw/industrial_fault_images.zip" --output "data/processed/stage1_collection_inventory.json"
```

By default the SCANIA PDF originals are checked in **`C:\Users\hindh\Documents\2024-34-2\documentation`** (sibling of the original `data` directory). Use `--scania-docs "EXACT_EXISTING_DOCUMENTATION_FOLDER"` if they are somewhere else. If your already-collected AI4I CSV or original image ZIP are stored elsewhere, **point `--ai4i` or `--images` to their actual existing paths**; do not download substitute copies to make the check pass.

To inventory existing supplemental technical manuals, append the flag once per actual file, for example:

```powershell
--supporting-pdf "EXACT_PATH_TO_EXISTING_PUMP_PDF"
```

(Place that argument on the same invocation line; it is optional and never changes the approved dataset count.)

The terminal prints only the summarized source-file collection status. The full local `stage1_collection_inventory.json` includes actual sizes, SHA-256 values, per-file presence and reasons for any missing/mismatched source. Since it is ignored under `data/processed/`, it is not committed to GitHub.

If a file is missing or its digest differs, **stop** and use the original source archive from your own previously approved files. Never generate substitute machine measurements/images or suppress checks by inventing an expected fingerprint. The script refuses overwriting an earlier report; use a new versioned output path for subsequent runs.

## Exit criteria for Stage 1 (before Stage 2)

- [ ] **9/9** genuine original SCANIA v2 CSVs present and consistent with the previous owner's original-data audit.
- [ ] **2/2** original SCANIA documentation PDFs locally present.
- [ ] Original approved AI4I CSV present and same unchanged, owner-audited SHA-256.
- [ ] Original approved fault-image ZIP present, fingerprint and original 234-member structure verified.
- [ ] Supporting technical/manual PDF inventory either recorded from actual files or explicitly scoped out; no fake PDFs.
- [ ] License/source register retained in GitHub: SCANIA CC BY 4.0 and Mendeley V1 CC0 1.0 as listed by their pages; Kaggle exact license/per-image photo rights **OPEN** and explicitly disclosed.
- [ ] Owner-run local collection-inventory report reviewed and source availability gate confirmed.

**Stage 1 file acquisition** can be declared complete when the actual originals and required documentation are verified, with every unresolved rights/provenance issue explicitly registered. This **does not itself certify full legal reuse permissions or high-quality image labels**. If project requirements demand rights-cleared images at the collection stage, full Stage 1 closure must remain **BLOCKED** until that external evidence is provided. Do not silently waive this restriction.

The next stage is **Stage 2 Data Auditing** only after Stage 1's actual local file collection evidence is reviewed and any required rights limitations accepted. Later Stage 3 Cleaning, Stage 4 Labels, Stage 5 Splits, Stage 6 Features, Stage 7 Final Data Validation must be closed sequentially, not bundled together.
