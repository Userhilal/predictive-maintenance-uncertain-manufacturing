# Final qualified data-stage acceptance — 2026-11-25

## Decision

Technical preparation of the three original sources is accepted within the source-specific restrictions below. The active AI4I–Kaggle integration is exploratory class-reference metadata only; SCANIA remains independent. No fourth dataset, MATWI, fabricated labels or physical event pairs. This decision permits proceeding to requirements and architecture design, not unrestricted model development.

## Evidence reviewed

- Owner-local full correction: `CORRECTED_FULL_TECHNICAL_PASS_EXPLORATORY_ONLY`.
- Owner-local read-only verification after PR #61 (commit `c44968b`): `PUBLISHED_FULL_TECHNICAL_PASS_EXPLORATORY_ONLY`; all 15 output files and report verified, 225 image hashes, 133 strict photo references, 55 exploratory associations; no original or published files modified.
- Owner-local Git status clean and synchronized; both MATWI directory checks returned false and no MATWI tracked paths.
- Original Stage 7 report supplied in full as terminal text on 2026-11-25 and reviewed: `STAGE7_SOURCE_INTEGRITY_VALIDATED_AI4I_ONLY_FULL_MULTIMODAL_BLOCKED_REVIEW_REQUIRED`. Stage 2–6 fingerprints match the pinned script values; all reported chained checks true. The original report remains unmodified; its own `stage7_signed_off=false` is a producer flag, not overwritten by this separate review. Exact byte SHA-256 of the Stage 7 report itself was not supplied; do not confuse the five verified earlier report hashes with that fingerprint.
- 18 + 9 previously executed regression checks passed on the real Kaggle archive and isolated corruption copies, including missing AI4I negative checks. Full AI4I and SCANIA revalidation is supported by owner-local reports, not independent access to raw files. Remote CI configuration exists; execution remains unconfirmed.

## Accepted source scope

| Source | Technical acceptance | Remaining limitations |
| --- | --- | --- |
| AI4I | 10,000 original rows accounted for; 27 disputed rows excluded; 9,973 eligible; 6,981/1,497/1,495 train/validation/test; 8 train-only engineered predictors and 79,784 checked predictor values. | Publisher-synthetic internal benchmark only; 330 positive observations; no real chronological machine trajectories or external generalization proof. RNF has one training positive and none in held-out splits. |
| Kaggle | 234 references, 225 distinct contents, 219 retained, 6 quarantined, 133 strict photo references. | 0 confirmed AI4I mode labels, 0 verified event pairs; reuse rights unverified. No supervised image training or permission-dependent publication. |
| SCANIA | Nine original CSV fingerprints match prior owner audit; 1,516,819 readouts, 33,641 vehicles, 481,376 missing sensor cells preserved. | Separate source; censored repair endpoint vs official validation/test five-class target compatibility unresolved. No cross-source joins. |

AI4I training means and population standard deviations for five normalized numeric features satisfy the near-zero/near-one tolerance. Partition positive counts are 231, 50 and 49; held-out distribution diagnostics are descriptive. Extreme original observations are retained.

The active 55 exploratory associations are TWF 16 wear analogies, HDF 11 hypotheses, PWF 4 equipment context only, OSF 24 hypotheses, RNF 0. Earlier 79-link view and Phase 2 10,000-row splits are historical, not training inputs. The eight Stage 3 image reference quarantine cases and six distinct canonical quarantined image contents are different counting units.

## Exit and next design gate

Qualified technical data preparation: COMPLETE. Full three-source supervised multimodal readiness: NOT APPROVED. Issues #43 and #56 remain open; #54 retains the unresolved full-scope eligibility gates. Do not rerun unchanged preparation simply to seek a different scientific verdict.

Next: requirements and architecture must explicitly distinguish supported internal AI4I classification, exploratory imagery (subject to rights), separate SCANIA task design, and unsupported production impact, repair/replacement cost and document/RAG evidence. No implementation or training is authorized by this document. No new dataset is approved.
