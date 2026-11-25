# Stage 7 — Final Data Validation (three-original-source integrity, qualified readiness)

**CURRENT STATUS: OWNER-LOCAL STAGE 7 AUDIT EXECUTED AND QUALIFIED REPORT REVIEW COMPLETE (2026-11-25).** See [final qualified acceptance](final-qualified-acceptance-2026-11-25.md). The original report is preserved; unrestricted multimodal readiness remains blocked.

This audit is **not** a new data collection step. Stages 1–6 were technically closed only within their source-specific eligibility restrictions. Stage 6 qualified sign-off for the AI4I publisher-synthetic benchmark was based on an actual owner-run SHA/source/value verification: **9,973 eligible original UDI records**, **27 disputed UDIs excluded**, **6,981** train-only fit rows, **8** approved predictor columns, and **79,784** recomputed source-derived predictor values. Original Stage 6 report SHA-256: `0250e7063eaae1f551a843cde3f963ba95f16f08cb261bd40b592783c58a3973`.

**Stage 7 aims to determine what is actually validated and what remains blocked**, not assert that three unrelated sources are already a linked multimodal manufacturing training dataset.

## Exactly three owner-approved original datasets

| Original source | What Stage 7 can check | Qualified decision, until genuinely new evidence exists |
|---|---|---|
| **SCANIA Component X v2** | Rehash **all nine unchanged original source CSVs** against the owner-reviewed original raw audit; reverify all **33,641 official distinct vehicle-level target members** and **1,516,819 original operational readouts**, with original missing sensor values preserved. | Original raw file provenance, source-cohort integrity and target distinction can pass. **NOT a ready unified supervised model**: original train `in_study_repair` right-censored endpoint semantics differ from publisher validation/test five-class proximity targets. Explicit compatible source task/evaluation design remains blocked. |
| **AI4I 2020** | Re-run the existing Stage 5/6 **read-only original-data UDI, exclusion, value and SHA reviews**. Independently summarize finite numeric feature distributions, exact class prevalence and original Type counts for eligible **6,981/1,497/1,495** cohorts; ensure the normalized **training** columns have near-zero mean and unit population standard deviation. | Source-consistent **9,973 original publisher-synthetic rows**, eight leakage-safe transformed predictors and original immutable labels are a **reproducible internal IID-like tabular benchmark candidate** only. **27** original target/mode disagreements remain excluded/quarantined. No real-factory, chronological or independent failure-truth claim. |
| **Industrial Machinery Fault Image Dataset** | SHA-verify the original **unchanged ZIP** against original SHA fingerprint and owner-reviewed Stage 3 source manifest; rerun Stage 3/4 **metadata-only integrity and exact queue** checks. This Stage 7 tool **does not extract/decode/inspect pixels**, copy photos, or produce image features/splits. | **All 234 original photo references remain BLOCKED** for verified-label supervised training/evaluation or permission-dependent image use: **0** per-photo independently verified class labels, **8** quarantined source annotation/provenance cases, and original license/individual reuse rights **UNVERIFIED**. Existing image QA issue [#43](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/43) stays open. |

The three sources **are not proven linked by machine identifiers**. No same-machine image/telemetry pairing, fourth dataset, pump PDF/manual, fake repair, new synthetic user-generated measurement or training example is authorized. AI4I was published *synthetic*, not new data fabricated in this project.

## Audit details and gates

Stage 7's new `src/preprocessing/validate_stage7_final_data.py` performs one **source-preserving, write-once validation**:

1. Rechecks the genuine **Stage 2 original audit report SHA**, Stage 3 cleaning manifest SHA and derived image membership queues, Stage 4 source label-lineage SHA and 27 UDI/8 image unresolved reviews, Stage 5 seven assignment hashes and exact UDI cohort reproducibility, Stage 6 four output hashes and **all 79,784** original AI4I predictor values. It refuses altered evidence.
2. Reopens and SHA-checks all **nine original SCANIA Component X v2 CSVs** on the owner's laptop, plus the validated official train/validation/test *different target* label definitions. It does **not** materialize a new SCANIA supervised feature matrix or new source task labels.
3. SHA-checks the **exact original Kaggle ZIP bytes** (metadata/identity audit only), reconciling with the original Stage 3 fingerprint. **No extraction, pixel decoding, prediction, AI vision model or redistribution**. This cannot establish the correctness of an individual visual class or a license.
4. Rechecks the original unchanged AI4I source CSV and all three eligible derived feature files. Per train/validation/test partition, report original target 0/1 prevalence, original H/L/M Type counts, finite z-score mean/population std/range, and descriptive count of absolute z-scores over 3 for **five** numerical source feature columns. The five normalized train feature columns must be centered and scaled to tolerance. The held-out distributions are **diagnostics**, not thresholds to discard legitimate original observations or tune parameters.
5. Outputs **one** Git-ignored original-source validation JSON. No data edits, extra features, unsupervised or supervised fitted models, training/evaluation results, new split, label correction, changed image status or imaginary missing measurement.

The report will explicitly carry three eligibility decisions: `AI4I internal tabular benchmark candidate: PASS (source-consistent only)`, `SCANIA unified supervised task: BLOCKED`, `original image supervised/permission-dependent use: BLOCKED`. **`full_three_source_supervised_multimodal_dataset_approved=false` is a REQUIRED correct result, not an execution failure.** The script reports `stage7_signed_off=false` until the output is reviewed separately. A Stage 7 audit report must **not** be misused as proof of full project's finished data preparation or full multimodal training readiness.

## Execute on the actual owner's local originals

After merging the Stage 7 implementation PR, from the Windows PowerShell repository root:

```powershell
git pull origin main

py -3.11 src/preprocessing/validate_stage7_final_data.py --scania-data "C:\Users\hindh\Documents\2024-34-2\data" --images-zip "C:\Users\hindh\Downloads\archive.zip" --output-dir "data/processed/stage7_final_validation"
```

All other paths default to the **existing unchanged** `data/processed` and `data/raw` files verified in Stages 1–6. Uses only the existing Python 3.11 standard library and repo scripts; no Pillow, outside APIs, image uploads, external documents or source downloads required.

**Write-once result:** `data/processed/stage7_final_validation/stage7_final_source_validation_report.json`. The program refuses to overwrite previously run Stage 7 output directories. Do NOT rerun Stage 6 feature generation or Stage 5 splitting. The Stage 7 JSON itself is *not* a final sign-off until the actual terminal output and source restrictions are reviewed.

## Historical execution checklist and acceptance criteria

The checklist below describes the original procedure; the completed qualified review is recorded in the linked acceptance document.

- [ ] Merge Stage 7 code PR after Python syntax CI and run it on **all three genuine original local source files/archives** as configured.
- [ ] Verify original SCANIA 9 CSV SHA values and official source vehicle/readout target semantics; explicitly leave common supervised target/evaluation contract **BLOCKED**.
- [ ] Reverify Stage 2–6 chained evidence hashes, 7 Stage 5 assignment manifests, four Stage 6 feature files and 79,784 AI4I predictor values, with no fitted holdout transforms, 27 original disputed UDI exclusions preserved.
- [ ] Review actual AI4I original-source per-split target prevalence, original Type counts and finite z-score distribution diagnostics; **no generalization claims from IID publisher-synthetic observations**.
- [ ] Rehash the exact original fault photo ZIP **without copying image pixels**; source images remain **BLOCKED** for supervised learning/rights-dependent use and provenance classes unresolved under issue #43.
- [ ] Confirm exactly 3 original sources, no source files/labels modified, no fake data, no invented cross-source machine pairs, no models trained or predictions generated.
- [ ] Sign off **only the scope that passes** (eligible AI4I internal tabular source and verified original-file provenance). **DO NOT** declare the complete three-source supervised multimodal project data-ready while SCANIA tasks and original image labels/rights remain blocked.
- [ ] Stage 8 Model Development is NOT authorized in this PR. If later considered, only a separately scoped original-source AI4I tabular baseline might be eligible after the Stage 7 qualified review; model readiness for SCANIA and Kaggle photos is not established.

**Final disposition:** original-source technical integrity and eligible AI4I internal benchmark accepted after owner-local execution and report review. Full supervised multimodal readiness remains blocked. Exact original Stage 7 report byte fingerprint was not supplied. Stage 8 implementation not authorized.
