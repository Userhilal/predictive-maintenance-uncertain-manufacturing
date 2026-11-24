# Unified five-mode failure mapping — proposed class associations, NOT source truth

**STATUS: A REPRODUCIBLE EXPLORATORY IMAGE↔AI4I MODE REFERENCE MAP, NOT A FINISHED FIVE-CLASS LABELED IMAGE DATASET, NOT SYNCHRONIZED TIME-SERIES/IMAGE PAIRS.**

The user provided a five-mode diagram and explicitly requested a practical mapping. This file implements a **two-layer ontology** rather than silently relabeling the original Kaggle images:

- **Layer 1 — Source observation:** the original **Crack / Misalignment / Normal condition / Surface defects / Wear** folder label; the original ZIP image path/hash; original Stage 3 219 provisional, 7 duplicates excluded, 4 cross-folder conflicts, 4 manually flagged.
- **Layer 2 — AI4I failure mechanism candidate:** `TWF / HDF / PWF / OSF / RNF`, with explicit `WEAK`, `VERY_WEAK` or `SOURCE_FOLDER_NORMAL_UNVERIFIED` status. **No image is assigned a verified AI4I failure mode** without independent evidence and rights.

## Final proposed explicit class-level visual proxy policy

| Failure mode | Original image source folders | Number of original archive refs, including flagged/duplicate | Evidence level | Physical AI4I context | Honest limitation |
|---|---|---:|---|---|---|
| TWF — Tool Wear Failure | Wear | 43 | WEAK candidate | `Tool wear [min]` and original `TWF` flag | General belt/bearing/shaft wear is not necessarily an AI4I cutting tool failure |
| HDF — Heat Dissipation Failure | **No direct source photo class** | 0 | NOT MAPPABLE BY IMAGE FOLDER | Air and process temperature, speed, original `HDF` flag | Image alone cannot identify the heat transfer mechanism |
| PWF — Power Failure | **No direct source photo class** | 0 | NOT MAPPABLE BY IMAGE FOLDER | Torque × angular speed for mechanical power, original `PWF` flag | The AI4I PWF mechanism is mechanical power envelope; do **not** reinterpret as generic electrical supply outage |
| OSF — Overstrain Failure | Crack; Misalignment; Surface defects | **143** (47 + 53 + 43) | WEAK for crack; VERY_WEAK for other two | Torque, tool wear and `Type` source class; original `OSF` flag | Generic cracks, alignment issues and surface flaws have multiple possible causes; they are not the source-defined OSF mechanism |
| RNF — Random Failure | **No direct source photo class** | 0 | NOT MAPPABLE BY IMAGE FOLDER | Original `RNF` label / documented event | **Do not use all residual cases** or unclear images as RNF |
| NO_FAILURE / UNKNOWN (outside five failure mechanisms) | Normal condition | **48** | SOURCE FOLDER ONLY | Original AI4I `Machine failure = 0` is not a proven physical match to this image | The folder name is not an expert verified machine healthy state |

**43 + 143 + 48 = 234** original ZIP image references. These are **unverified candidate visual associations**, **not 234 independent confirmed examples**. Original duplicate/conflict/quarantine flags remain in the output, so only an appropriately reviewed, authorized subset may be considered for future example use. At this stage **0** original images have independently verified AI4I-mode diagnoses, and **0** are verified same machine/event pairs with AI4I or SCANIA.

The user-provided diagram proposed misalignment or surface defects for RNF: **we reject that shortcut** because RNF is a specific independent source-mode target, not a catch-all class for images that cannot be diagnosed.

## Original-source sensor context — what may be associated

| Original source | Safe failure-mode use | What cannot be claimed |
|---|---|---|
| **AI4I 2020** | The five original `TWF/HDF/PWF/OSF/RNF` binary target flags are genuine *source labels*. Numeric original inputs include air/process temperatures, speed, torque and tool wear. The 9,973 accepted original UDI observations have source-mode index records with 27 original disputed global-target/mode UDIs separately excluded. | These are published **synthetic machine-process observations**, **not proven time-series windows from the same identifiable machine**, and the five source failure-mode flag columns are **targets**, not permitted model-input features for predicting those modes. A row-to-photo physical association is not established. |
| **SCANIA Component X v2** | Genuine original longitudinal operational readouts, workshop repair history, and official vehicle cohorts are preserved. | Proprietary variable identities/units are anonymized. Do **not** claim SCANIA `temperature`, `power`, `torque`, `tool wear` or any AI4I five-mode targets exist as verified source columns. SCANIA train time-to-repair/right-censoring target and val/test five-class proximity categories are **not** TWF/HDF/PWF/OSF/RNF. |
| **Original 234-image Kaggle ZIP** | Visible-component appearance source-folder labels and exact archive member paths/hashes; tentative visual prompts for a reviewer. | Original images are NOT source-labeled by AI4I's five mechanisms, individual photo reuse rights and causal diagnoses are still unresolved. All supervised label-dependent and permission-dependent image use remains blocked under [#43](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/43). |

The original dataset primary descriptions confirm: [UCI AI4I 2020](https://archive.ics.uci.edu/dataset/601/ai4i) defines a synthetic process dataset with five source failure-mode flags and source numerical measurements; [SCANIA Component X v2 research article](https://www.nature.com/articles/s41597-025-04802-6) documents anonymization and time-to-repair/proximity-label semantics. **No fourth dataset** is introduced by this mapping.

## Exact implemented output and execution

Policy: [`five-mode-visual-proxy-policy.json`](five-mode-visual-proxy-policy.json).

Stage 7+ metadata-only script: `src/preprocessing/build_five_mode_visual_proxies.py`.

From Windows PowerShell **after merging the PR**:

```powershell
git pull origin main
py -3.11 src/preprocessing/build_five_mode_visual_proxies.py --annotation-dir "data/processed/five_mode_image_annotation" --policy "docs/datasets/five-mode-visual-proxy-policy.json" --output-dir "data/processed/five_mode_visual_proxy_review"
```

This verifies the **existing owner-local five-mode annotation report and both original output CSV SHA-256 values**, preserving the actual original three-source Stage 3/4/5 evidence, 234 exact source photo refs, 9,973 original AI4I source-consistent UDI mode flag labels, 27 originally disputed UDIs excluded. It writes only:

- `original_234_photo_weak_mode_candidates_NOT_GROUND_TRUTH.csv` — one row per original image member; source folder, original hash/Stage 3 action, proposed **candidate** mode, grade, diagnostic caveat, blank verified mode, no rights or true pairing verified.
- `five_mode_unpaired_reference_coverage_NOT_TRAINING.csv` — five mode codes; actual original AI4I source-positive flag counts read from existing local index, and associated **weak** unpaired image candidate counts, with HDF/PWF/RNF at **zero** photo candidates.
- `visual_proxy_association_evidence_report.json` — new local file SHA fingerprints, original proof hashes and all **blocked** readiness flags.

No photos, bytes or image ZIP are copied or transmitted. No AI4I records are joined one-to-one with photos. No source label changes, no model input features, no training/validation/test datasets are created, and **Stage 8 Model Development is not started**.

## Why class association is different from image+time-series fusion

A `TWF` original AI4I source flag and an image of a worn bearing may share a **tentative conceptual failure-mode association**, but they are **unpaired observations from different sources**. It would be invalid to create a new row `(original AI4I UDI 1234, Kaggle Wear photo 17)` and call that a real jointly observed machine failure; the image has no matching manufacturer, actual machine ID, event ID, inspection diagnosis or timing. Same for SCANIA sequences, whose actual Component X failure targets cannot be relabeled as AI4I's five modes.

**To satisfy the user's true full five-mode, every-image-labeled dataset requirement:** (1) visually inspect each permitted photo and diagnose its failure mechanism with genuine equipment/maintenance context; (2) keep genuinely normal, indeterminate and cross-labeled images out of forced five-mode labels; (3) collect real mode-labeled image evidence for **HDF, PWF, RNF**, currently **zero** in the approved photo archive; (4) for synchronized multimodal pairs obtain genuine shared machine/event IDs + timestamp/inspection and original sensor series. In this phase, preserve the original dataset exactly and present visual proxies only as **review hypotheses**.

**Final status:** the requested mapping exists as a reproducible **unpaired candidate taxonomy**, but the five-class verified photo dataset and genuine same-machine sensor/photo pairs remain **NOT complete**. Keep open [issue #56](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/56).
