# Three-source independent-evidence catalog (2026-11-25)

The owner has explicitly accepted a revised integration scope: all three original datasets contribute to one system through distinct source-specific tasks, not a paired physical machine or failure event. This supersedes only the earlier decision to leave SCANIA outside the common catalog; it does not revoke any source-quality or scientific restriction from the [qualified acceptance](final-qualified-acceptance-2026-11-25.md).

## Actual owner-local build

Status: `THREE_SOURCE_CATALOG_BUILT_FAILURE_TYPE_TIME_SERIES_JOIN_BLOCKED`. The owner provided the full successful build summary: nine pinned SCANIA source CSVs verified; 33,641 vehicle histories and 1,516,819 original readouts referenced; 9,973 eligible AI4I tabular rows; 133 strict photo references and 55 exploratory links. The original 15 catalog output fingerprints were produced. All SCANIA failure mechanisms remain UNKNOWN. No verified SCANIA-to-photo links, no fabricated rows, no data changes or models.

| Source | Intended module | Evidence limitation |
|---|---|---|
| AI4I | Internal failure-mechanism classification | Publisher-synthetic tabular, not real longitudinal histories; RNF not evaluable on held-out splits. |
| SCANIA | Repair-risk and time-to-event analysis | Anonymized component and sensors; native censor/repair and proximity targets remain distinct; no known five-mode cause labels. |
| Kaggle | Exploratory visual reference retrieval | No confirmed AI4I failure labels; photo reuse rights unverified, permission-dependent use blocked. |

No SCANIA native proximity class may be mapped to TWF/HDF/PWF/OSF/RNF. The AI4I/photo link counts remain 16/11/4/24/0 respectively and are not training targets. SCANIA data rows remain in original CSVs.

## New safeguards

The correction package delivered to the owner implements `verify_integration.py`, which reconstructs the catalog in a temporary directory and compares exact inventory, 15 output hashes and the report itself. It rejects forged report hashes. `load_history.py` filters the original pinned readout CSV by exact split and vehicle ID; it never assumes that the rows are contiguous. It compares the selected catalog row to original target metadata and checks original row ordinals, timestamps and counts. It emits ordered raw sensor cells (missing strings preserved), not native targets as predictors. Full histories are inspection-only until an as-of cutoff is defined.

Ten additional checks passed in the development environment using the actual original photo-side reconstruction and deliberately corrupted isolated copies, plus missing/invalid input tests. **Full post-generation verification of the three-source catalog and positive SCANIA retrieval are pending owner-local execution**; exact raw SCANIA/AI4I files are not available in that environment. No independent full source run is claimed. The code package must be added on this branch before merging. CI is source-free and does not replace local checks.

## Local acceptance

```powershell
py -3.11 Three_Source_Integration/verify_integration.py --scania-data "$HOME\Documents\2024-34-2\data" --images-zip "$HOME\Downloads\archive.zip" --test-retrieval
```

Expected: `THREE_SOURCE_CATALOG_VERIFIED_INDEPENDENT_EVIDENCE_ONLY`, 15 files plus report checked, actual retrieval counts for first/last vehicle in each split and a noncontiguous example if available. The existing catalog is write-once; preserve it, use original paths/platform (v1 stores absolute paths). A relocated dataset must be rebuilt to a new version, not silently alter the old report.

## Architecture restriction

Independent evidence outputs must retain source, task, entity context, target semantics, uncertainty (once evaluated) and provenance. The future integration layer may present side-by-side evidence; it must not combine unrelated probabilities or present an AI4I diagnosis and a SCANIA risk estimate as observations of one machine. No joint per-machine prediction, actual production loss, or repair-cost claim is approved. Model/RAG/decision implementation is not part of this change. Issues #43 and #56 remain open for their scientific blockers. No additional dataset or MATWI.
