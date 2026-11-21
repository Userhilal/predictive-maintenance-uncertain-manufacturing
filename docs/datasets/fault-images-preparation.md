# Industrial machinery fault images — Phase 2 preparation

**Status: PROVISIONAL_CURATED_IMAGES_REVIEW_AND_RIGHTS_OPEN.** Reproducible source audit and provisional split proposal, not a certified classifier dataset. No original labels changed or model trained. No artificial/generated replacement images or synthetic test fixtures are permitted; use only the original Kaggle images.

## Original source

- Kaggle: https://www.kaggle.com/datasets/zara2099/industrial-machinery-fault-image-dataset/data
- Original uploaded archive: archive.zip
- SHA-256: d30ffdcdcda1258ac95d89dd90539fe7ffd7b398e693ada652b4f63c073c9b28
- Licensing, photo rights and per-image provenance are **not verified**. Public Kaggle availability does not imply unrestricted reuse.

## Actual audit

| Finding | Result |
|---|---:|
| Total / unreadable images | 234 / 0 |
| Crack / Misalignment / Normal condition / Surface defects / Wear | 47 / 53 / 48 / 43 / 43 |
| Exact duplicate groups | 9 |
| Same-class duplicate copies removed from provisional set | 7 |
| Cross-class duplicate pairs / images quarantined | 2 / 4 |
| Additional ambiguous/provenance-flagged images quarantined | 4 |
| **Provisional candidate images** | **219** |
| Shortest dimension below 300px / below 200px | 210 / 168 |
| File extension vs. actual format mismatches | 2 |

Cross-class identical-image conflicts: Dataset/Crack/29_.jpg = Dataset/Wear/29_.jpg; Dataset/Surface defects/24_.jpg = Dataset/Wear/21_.jpg. **Both images in each pair are quarantined. Do not guess their true labels.**

Seven same-class duplicate copies occur in Misalignment: 40_.jpg↔47_.jpg, 41_.png↔48_.png, 42_.jpg↔49_.jpg, 43_.jpg↔50_.jpg, 44_.jpg↔51_.jpg, 45_.jpg↔52_.jpg, 46_.jpg↔53_.jpg. One canonical image remains only a *provisional* candidate.

Further review: Crack/1_.jpg, Misalignment/1_.jpg, Normal condition/11_.jpg, Wear/4_.jpg. See [review queue](fault-image-manual-review.csv) for source paths and concerns. Their labels are not changed.

Format mismatches: Misalignment/34_.jpeg contains WebP; Wear/42_.png contains JPEG. Source files remain unchanged.

## Provisional stratified image split (seed 42)

| Class | Train | Validation | Test |
|---|---:|---:|---:|
| Crack | 32 | 7 | 6 |
| Misalignment | 32 | 7 | 6 |
| Normal condition | 33 | 7 | 7 |
| Surface defects | 29 | 6 | 7 |
| Wear | 28 | 6 | 6 |
| **Total** | **154** | **33** | **32** |

Exact SHA-256 duplicates cannot cross splits. **Near-duplicate, equipment-instance, label-quality, and photo-rights checks remain open**. These are proposals only, not validated evaluation splits.

## Reproduce locally

Install Pillow:
~~~powershell
py -3.11 -m pip install Pillow
~~~

Put the *unchanged* uploaded ZIP at data/raw/industrial_fault_images.zip. From the repository root run:

~~~powershell
py -3.11 src/preprocessing/prepare_fault_images.py --input data/raw/industrial_fault_images.zip --output data/processed/fault_images --review-file docs/datasets/fault-image-manual-review.csv
py -3.11 -m unittest discover -s tests -v
~~~

Generated local Git-ignored outputs:

- image_manifest.csv: all 234 source paths, classes, hashes, dimensions, image format, review status and split.
- review_and_exclusion_queue.csv: 15 quarantined/excluded entries and reasons.
- provisional_splits.csv: 219 candidate paths, labels and splits.
- quality_report.json: counts, source fingerprint, warnings and limitations.

No original images are uploaded to GitHub.

## Outstanding acceptance conditions

- [ ] Verify image-level provenance, license, attribution and permitted reuse.
- [ ] Review ambiguous class labels and conflicting exact-image labels.
- [ ] Check perceptual near-duplicates and machine-instance overlap before model assessment.
- [ ] Resolve labeling consistency across multiple equipment types.
- [ ] Freeze final reviewed splits after human sign-off.

The image dataset is **not synchronized** with AI4I or SCANIA. Do not imply common machine identifiers or use it as matched multi-sensor observations.
