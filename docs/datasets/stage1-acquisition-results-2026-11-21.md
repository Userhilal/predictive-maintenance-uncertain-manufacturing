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

## Final source scope decision: exactly three datasets

**Final Stage 1 acquisition decision (2026-11-21): COMPLETE.** Following the verified owner-run `THREE_ORIGINAL_DATASETS_AND_SCANIA_DOCUMENTS_LOCALLY_VERIFIED` result, the owner explicitly confirmed the scope is **SCANIA Component X v2, AI4I 2020 and Industrial Machinery Fault Images only**.

Two separately suggested pump publications (`pump.pdf`, `pumplcc_1001.pdf`) are **OUT OF SCOPE**. Their absence in the owner's local inventory is **not** a missing-file or acceptance blocker. They must not be required for this project's RAG, model training or maintenance examples. Both SCANIA provider-package PDFs are *part of the original SCANIA source* and remain counted within the SCANIA acquisition inventory; they are not new datasets.

**Three source acquisition checks: PASS.** The 9 original SCANIA CSVs, the 2 accompanying SCANIA original-source documentation PDFs, the original SHA-matched AI4I CSV, and the original SHA-matched 234-image ZIP are already physically verified. No need to rerun the same successful inventory or obtain any other files.

### Limitations explicitly carried into Stage 2 audit

- The Kaggle image archive's exact reuse license and individual image provenance/rightsholder permissions remain **unverified**. Stage 1 file collection is complete; this is a **source-provenance/rights verification gate** for Stage 2 auditing and any later external use. Do not claim permission to publicly redistribute images.
- Original local SHA-256 comparisons are against previously owner-audited downloaded copies, not externally publisher-signed hash certifications.
- SCANIA vehicle sensor histories, AI4I publisher-synthetic manufacturing records and Kaggle fault images are **separate** sources. No real shared identifiers or joint machine observations are established.
- No cleaning decisions, label sign-off, approved image split, final feature matrix or trained model are implied by completion of Stage 1.

**Next milestone: Stage 2 — Data Auditing only.** The owner requires each of Stages 2 through 6 to be fully resolved sequentially before Stage 7.

See [Stage 1 completed collection policy](stage1-collection-closure.md) and [Stage 1 GitHub evidence issue #28](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/28).
