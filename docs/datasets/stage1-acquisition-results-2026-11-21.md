# Stage 1 — Original-source acquisition verified locally (2026-11-21)

**File acquisition result:** `THREE_ORIGINAL_DATASETS_AND_SCANIA_DOCUMENTS_LOCALLY_VERIFIED`

The project owner ran the already merged `src/preprocessing/audit_stage1_collection.py` against their **previously acquired, original SCANIA v2 data files, original AI4I CSV, and unchanged original Kaggle image archive**. This is an actual local collection-inventory result, not a simulated test or assertion that generated data were used.

## Observed local inventory

| Original source element | Reported original-file check |
|---|---|
| SCANIA Component X version 2 original CSVs | **9/9 verified** against owner-recorded original-source audit SHA-256 |
| SCANIA Component X official documentation PDFs | **2/2 verified**, PDF headers and file presence |
| AI4I 2020 original source CSV | **PRESENT**, matching prior original SHA-256 |
| Kaggle Industrial Machinery Fault Images original ZIP | **PRESENT**, matching prior original ZIP SHA-256 and archive-structure checks |
| Additional supporting manuals checked in this run | **0** |
| Exact Kaggle image-per-photo reuse rights | **Unverified** |

**Full owner-run terminal status:**

```json
{
  "status": "THREE_ORIGINAL_DATASETS_AND_SCANIA_DOCUMENTS_LOCALLY_VERIFIED",
  "scania_original_csv_verified": 9,
  "scania_original_pdfs_verified": 2,
  "ai4i_original_csv_status": "PRESENT",
  "fault_image_original_zip_status": "PRESENT",
  "supporting_manual_pdfs_checked": 0,
  "stage1_collection_signoff": "FILE_ACQUISITION_CHECKS_PASSED_RIGHTS_REVIEW_OPEN",
  "fault_image_reuse_rights_verified": false,
  "full_inventory_file": "data\\processed\\stage1_collection_inventory_verified.json"
}
```

**Original-source acquisition paths established by real execution:**

- SCANIA originals were in `C:\Users\hindh\Documents\2024-34-2\data`, with source documentation in the sibling `documentation` folder.
- AI4I original was extracted unchanged from a **nested original archive** `Predictive maintenance dataset.zip` to the user's local `data/raw/ai4i2020.csv`. SHA-256 of the extracted, unchanged original CSV: `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`. The outer archive's own fingerprint was recorded separately; do not conflate them.
- Kaggle original `C:\Users\hindh\Downloads\archive.zip` matched previously owner-audited SHA-256 `d30ffdcdcda1258ac95d89dd90539fe7ffd7b398e693ada652b4f63c073c9b28`, with original expected source-image structure.

The first local inventory had genuinely returned **MISSING** for AI4I/image files because its guessed `data/raw` paths did not contain those originals. Both were subsequently located, the AI4I nested CSV SHA was checked before any extraction, and the final inventory was executed with **correct actual file locations and a new versioned output filename**. The earlier incomplete report remains preserved; no audit evidence was overwritten.

## Important distinction: acquired files vs complete Stage 1 scope and legal reuse

**PASS:** All three approved original dataset archives/CSVs and both official SCANIA accompanying PDFs are currently present and pass the implemented file/fingerprint collection checks. The SCANIA data is from *real trucks*, Mendeley AI4I is *publisher-synthetic*, and the unrelated Kaggle images cannot be presented as photos of the same machines in the sensor datasets.

**OPEN — Independent supporting OCR/RAG technical manuals:** Prior project material specifically named two general guides `pump.pdf` (*Improving Pumping System Performance*) and `pumplcc_1001.pdf` (*Pump Life Cycle Costs*) for OCR/RAG and maintenance context. They were described as previously collected in an earlier academic prototype, but **this current laptop collection inventory did not receive either as a supporting-PDF path** (`supporting_manual_pdfs_checked: 0`). Until their actual local paths, basic file integrity and provenance are inventoried, the broader project's supporting-document collection should not be marked complete. These guides are independent documents, not a fourth approved sensor dataset or machine-registered SCANIA manuals.

**OPEN — Image rights:** The exact Kaggle dataset's reuse license and individual photograph provenance/reuse rights have not been independently verified. A matching original archive hash **does not grant permission to redistribute or publicly train on restricted imagery**. Preserve rights as unresolved; determine allowable usage before any public image redistribution or release.

**OPEN — Publisher authentication:** The SHA-256 matches to the owner's previous original-source local checksums, not independently certified publisher-issued checksums. Do not represent them as external provenance certification.

**NOT claimed:** final data cleaning, resolved labels, approved train/validation/test splits across all sources, feature engineering, final data validation, RAG-ready grounded text corpus, training or model performance.

## Stage 1 closeout checklist (strict sequence requested by owner)

- [x] File collection of all three approved datasets physically verified on owner laptop.
- [x] Two official SCANIA source documentation PDFs verified.
- [x] AI4I original nested source CSV extracted *unchanged*, with exact previously audited SHA-256.
- [x] Kaggle original archive located and verified against earlier owner-audited hash.
- [ ] Inventory original local `pump.pdf` and `pumplcc_1001.pdf` if still in OCR/RAG scope, with their actual paths and source/reference attribution; no fabricated manuals.
- [ ] Preserve and clearly disposition source image reuse/legal caveat (may remain a separate unresolved publication gate, but never claim license verified).
- [ ] Sign off **full Stage 1 project-materials collection** after technical documents are accounted for, then begin **Stage 2 Data Auditing**. Do not skip stages 3–6 or jump to Stage 7.

**Decision:** `THREE_CORE_DATASET_FILE_ACQUISITION_PASSED`; **full Stage 1 project-material inventory remains open** until the supporting-document scope and declared licensing limitations are resolved. No additional raw datasets, source rows, generated sensor values or fake image measurements were created.

See [Stage 1 collection-closure policy](stage1-collection-closure.md) and [GitHub Stage 1 tracking issue #28](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/28).
