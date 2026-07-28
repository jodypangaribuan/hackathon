# Interim Data

Generated data after ingestion and deterministic cleaning, before canonical entity resolution and final model preparation.

Expected outputs:

```text
clean_reviews.parquet
clean_metadata.parquet
quarantine_rows.parquet
duplicate_groups.parquet
cleaning_manifest.json
```

Every manifest must record source hashes, config version, pipeline version, generated timestamp, and row-count funnel.
