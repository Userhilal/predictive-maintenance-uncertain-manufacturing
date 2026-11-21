# Team collaboration guide

## Everyday workflow

1. Clone the shared repository and pull the latest `main`.
2. Create a branch for one focused task, for example `docs/dataset-audit`, `data/ai4i-quality`, or `feat/failure-baseline`.
3. Make small commits with descriptive messages.
4. Push the branch and open a pull request (PR) targeting `main`.
5. Ask the other teammate for review. Discuss and resolve comments before merging.
6. Pull `main` again after merge.

## Pull request checklist

- [ ] The change has a clear scope and explanation.
- [ ] Source links are provided for new data claims.
- [ ] No private information, keys, or unauthorized data is included.
- [ ] Data handling changes explain any transformations and preserve raw sources.
- [ ] Any relevant tests/checks are described, including those not run.
- [ ] A teammate has reviewed the proposed change.

## Rules

- Never commit directly to `main` for substantive work.
- Do not force-push shared branches.
- Do not modify source datasets in place; create derivative data separately.
- Do not combine examples from the three datasets as if they came from the same equipment.
- Use GitHub Issues to record planned work and blocking data problems.

## Initial ownership

Assign tasks through GitHub Issues after both collaborators have access. Both contributors should participate in review and data-quality decisions.
