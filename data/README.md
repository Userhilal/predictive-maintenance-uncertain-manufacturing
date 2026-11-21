# Data storage

Store downloaded source datasets **outside GitHub**. Suggested local directories:

```text
data/raw/        # Original downloaded data (read-only; ignored by Git)
data/processed/  # Derived files (ignored by Git)
data/external/   # Licensed external source copies (ignored by Git)
```

Keep source URLs, checksums, license notes, and transformations in `docs/datasets/`. Never commit private data, raw image collections, or multi-GB CSV files.
