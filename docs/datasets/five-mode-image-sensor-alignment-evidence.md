# Five AI4I failure modes ↔ images and sensor-record alignment

**Status: Annotation preparation ONLY. No individual original image has been verified as TWF, HDF, PWF, OSF or RNF, and no image has been linked to an actual source AI4I or SCANIA machine event.**

The project requires five failure-mode tags: **TWF** (Tool Wear Failure), **HDF** (Heat Dissipation Failure), **PWF** (Power Failure), **OSF** (Overstrain Failure), **RNF** (Random Failure). These codes are published as five **separate binary source target flags** on the originally publisher-synthetic AI4I 2020 source data. They are **not the same five labels** as the original fault photo archive's source folders: `Crack`, `Misalignment`, `Normal condition`, `Surface defects`, `Wear`.

## A direct five-class image-label remapping is NOT justified

| Original image folder | Source class | Safe AI4I five-mode annotation |
|---|---|---|
| `Wear` | Visible wear-like condition | **Unknown** until a reviewer documents actual tooling context and a diagnosed TWF failure. Visible wear alone is not proof of a failure event |
| `Crack` | Visible crack-like defect | **Unknown**; no automatic OSF or other-mode inference from a crack |
| `Misalignment` | Visible alignment defect | **Unknown**; not a unique match for PWF, HDF or OSF |
| `Surface defects` | Visual surface imperfection | **Unknown**; no unique causal mode |
| `Normal condition` | Source asserts no visible fault | **Unknown pending independent inspection**; may eventually be verified as `NO_FAILURE`, which is **not** one of the five failure types |

**Especially important:** HDF (heat dissipation), PWF (power) and RNF (random failure) generally require diagnosis from operating parameters, instruments or event logs, not visual appearance alone. The official AI4I description defines RNF as occurring independently of measured process conditions. Thus forcing **every** photo into exactly one of five modes would manufacture false ground truth.

**Do not relabel `Wear → TWF`, `Crack → OSF`, `Misalignment → PWF`, or `Normal condition → RNF` as shortcuts.** Source folder is a visible-condition label, *not a machine failure mechanism or verified machine event*.

## Actual pairing vs class-level association

1. **True same-event multimodal pairing:** A sensor time window and photo must share a **source-proven machine ID and maintenance/failure event ID**, ideally timestamp, diagnosis and original photo capture provenance. **None of our three approved original sources establishes these cross-source joins.** Do not generate a fake one-to-one photo/sensor pairing.
2. **Class-level association** (not real pairs): If an independently reviewed photo has a **source-supported mode**, it can be shown **as an example for a source failure mode category** beside *unrelated, source-labeled* AI4I records carrying that mode. Explicitly mark `alignment_type=CLASS_ONLY_UNPAIRED`; never call that a same-machine, simultaneous or real-world event. It is a multimodal **reference catalog**, not true observed paired time series.
3. **AI4I is not source-proven as multiple timestamped observations of the same identifiable machine.** Even though it has process measurements and five failure-mode flags, an ordered original `UDI` is **not automatically a real timestamp or machine identity**. The SCANIA original dataset has real machine readout sequences but its official train repair/censor vs validation/test five-class target semantics do **not** provide the five AI4I failure-mode labels, so no justified mapping exists there either.

The source AI4I flag columns are **labels**, not allowed input predictors of those same labels. One source record can have more than one positive failure-mode flag; a final design must decide **multi-label classification** vs **single-class diagnosed event classification** based on real source evidence, rather than discarding ambiguity invisibly. Original 27 binary target/union-of-modes disagreements continue to be quarantined.

## What the source-only preparation script creates

`src/preprocessing/prepare_five_mode_image_annotation.py` reads the SHA-verified owner-run **Stage 3 original 234-image source metadata**, **Stage 4 label/provenance review**, **Stage 5 disjoint source UDI assignments** and unchanged original AI4I CSV. No source photos, pixels, images, new datasets or unapproved links are copied or opened. It writes exactly **three Git-ignored local outputs** under `data/processed/five_mode_image_annotation`:

| Derived file | Content |
|---|---|
| `original_234_image_five_mode_annotation_queue.csv` | One row per **all 234** original ZIP source member paths and hashes, its original visible folder label and earlier conservative source-exclusion/quarantine status, plus **blank expert-reviewed five-mode labels** and annotation evidence fields. Original 219 provisional references stay *PENDING*, 7 exact same-class duplicates stay *EXCLUDED*, 4 contradictory original classes and 4 original manual-review photos stay *QUARANTINED*. Each image has a review state, **not an invented TWF/HDF/PWF/OSF/RNF label**. Photo reuse-rights and same-event links remain `UNVERIFIED`. |
| `original_ai4i_9973_eligible_five_mode_source_index.csv` | One source label record per **9,973 previously eligible original AI4I UDI/split**, including **original** five binary failure-mode flags, original global failure target and Type, plus a list of **actual source-positive** flags. Original 27 disputed source UDIs **excluded**. This is a *label index*, **not a sensor sequence, feature matrix or verified image pairing**. |
| `five_mode_alignment_evidence_report.json` | Evidence fingerprints, source mode-flag frequencies, multiple-positive-mode counts, original 234 source image review-action totals, **zero** verified five-mode photo labels, **zero** original same-event image-to-sensor links, and explicit image rights/annotation blocks. |

Output has SHA-256 fingerprints and refuses overwrite of existing derived outputs. All previous Stages 1–7 reports and original source photos remain untouched.

### Run after merging the preparation PR

```powershell
git pull origin main
py -3.11 src/preprocessing/prepare_five_mode_image_annotation.py --output-dir "data/processed/five_mode_image_annotation"
```

## Evidence-based manual labeling requirements

A reviewer of each original **source image** must record: its original ZIP path and image hash, what is *actually visible*, whether a machine/failure mode can be **causally** diagnosed, the supporting maintenance/equipment/event evidence, reviewer identity and date, and applicable permissions/provenance. Only then can a review status become `VERIFIED` with actual modes from `TWF|HDF|PWF|OSF|RNF`, `VERIFIED_NO_FAILURE`, or `NOT_DIAGNOSTIC`. A failure-mode visual tag unsupported by the original image/context must remain `UNKNOWN`/pending. **A label can be multi-mode only with corresponding independent evidence**. `RNF` in particular must not be labeled purely from a photo.

Per-photo reuse/processing permissions must be verified **before any right-dependent photo sharing, public training, preprocessing or use**. All 234 original source photos remain blocked from approved supervised image learning until the rights and independently verified labels are established, as tracked by [image evidence issue #43](https://github.com/Userhilal/predictive-maintenance-uncertain-manufacturing/issues/43). Annotating *metadata* alone does not grant image use permissions.

**Completion criterion for actual multimodal alignment:** appropriate, legitimately usable, verified per-image failure-mode labels exist for all desired categories **and** a documented mode-level association can be built, clearly marked `CLASS_ONLY_UNPAIRED`. If the project truly requires synchronized photos and timeseries of **the same** failing machine, obtain actual same-event machine ID/time evidence; none of the existing datasets provides it. That cannot be solved through code or renaming classes.

**Do not claim a complete labeled five-mode image corpus or full paired multimodal training data exists.** This preparation does not undo earlier qualified Stages 1–7 audit decisions or authorize Stage 8 model development.
