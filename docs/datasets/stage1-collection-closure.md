# Stage 1 — Data Collection: signed off for exactly three approved sources

**Decision (2026-11-21): COMPLETE — original-file acquisition.** The owner explicitly narrowed this project to **exactly these three sources**:

1. **SCANIA Component X v2**, original Researchdata version 2 (nine original CSVs, with the two PDFs published **inside that SCANIA source package**).
2. **AI4I 2020**, the original user-supplied Mendeley dataset (its source publisher describes synthetic manufacturing-style observations).
3. **Industrial Machinery Fault Image Dataset**, the original user-supplied Kaggle ZIP.

**No additional pump manual datasets, PDFs or other supplementary documents are required or approved.** In particular, `pump.pdf` and `pumplcc_1001.pdf` were previously suggested by mistake and are explicitly **OUT OF SCOPE**. Do not download them, copy them into the current project, use them for RAG, or block Stage 1 because of their absence. The two PDFs **packaged by the original SCANIA provider** remain source documentation *within SCANIA*, not a fourth source.

## Provenance and actual acquisition evidence

The owner executed `src/preprocessing/audit_stage1_collection.py` locally with the actual approved files, returning `THREE_ORIGINAL_DATASETS_AND_SCANIA_DOCUMENTS_LOCALLY_VERIFIED` and `FILE_ACQUISITION_CHECKS_PASSED_RIGHTS_REVIEW_OPEN`:

| Source | Actual owner-run local evidence | Stage 1 collection |
|---|---|---|
| [SCANIA Component X version 2](https://researchdata.se/en/catalogue/dataset/2024-34/2) | **9/9 original CSVs** match prior owner-run SHA-256 audit; **2/2 official same-source documentation PDFs** present | PASS |
| [AI4I 2020, Mendeley V1](https://data.mendeley.com/datasets/5ww3zv87y7/1) | Unchanged original `ai4i2020.csv` extracted from previously supplied nested ZIP; matches previously audited SHA-256 `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e` | PASS |
| [Industrial Machinery Fault Images, Kaggle](https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data) | Original **234-image ZIP** `archive.zip`; matches previous owner-audited SHA-256 `d30ffdcdcda1258ac95d89dd90539fe7ffd7b398e693ada652b4f63c073c9b28`; archive integrity checks passed | PASS |

See [the actual terminal-report transcription and collection evidence](stage1-acquisition-results-2026-11-21.md). The complete local owner-run report remains at `data/processed/stage1_collection_inventory_verified.json`; original raw files and source archives are not committed to GitHub. The earlier incomplete inventory report was preserved as audit history; its initially missing *assumed paths* were resolved and the corrected inventory **passed**.

## Acceptance boundary and limitations

Stage 1 **collection** is complete because all three agreed original datasets are present and the implemented archive/file checks passed. **No extra manuals** and **no new datasets** are required.

This sign-off does **not** certify all source records as trustworthy or permission-cleared:

- Original Researchdata SCANIA v2 lists CC BY 4.0; Mendeley V1 lists CC0 1.0. The specific Kaggle archive's license and **individual image provenance/reuse rights are unresolved**. Record this as an explicit **Stage 2 provenance/rights audit and any later image-use/release gate**, not as an excuse to invent or collect other data. Do not claim rights clearance, redistribute affected photos publicly, or use them in activities requiring unverified permissions.
- SHA-256 matches are comparisons to the **owner's previously recorded original downloaded files**, **not** independent publisher-signed checksum authentication.
- SCANIA is real truck data, AI4I is **publisher-synthetic**, and the Kaggle photographs are independent examples. Do not fabricate same-machine joins, maintenance histories or sensor-photo supervision.
- This step makes **no claims** about Stage 2 auditing, Stage 3 cleaning, Stage 4 label verification, Stage 5 splitting, Stage 6 feature engineering, Stage 7 final data validation, or Stage 8 modeling.

## Final Stage 1 exit checklist

- [x] 9/9 unchanged original SCANIA version-2 CSVs present and owner-hash-matched.
- [x] 2/2 PDFs supplied within the original SCANIA source present.
- [x] Unchanged approved AI4I original CSV present, hash-matched.
- [x] Unchanged approved Kaggle ZIP present, owner-hash-matched, 234 archive members verified.
- [x] Exact approved source scope fixed at **three**, with **no standalone pump guides**.
- [x] Kaggle image rights/provenance and external publisher checksum limitations explicitly recorded **as unresolved**, not falsely cleared.
- [x] Owner-run consolidated original acquisition report checked, Stage 1 acquisition sign-off issued.

**Next step, and only next step:** **Stage 2 — Data Auditing**, across the same three original sources. Complete Stages 2, 3, 4, 5 and 6 **one by one** before Stage 7 final data validation. There is no requirement to create or retrieve additional source materials.
