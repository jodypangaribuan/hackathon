# Processed Data

Canonical, model-ready data produced from interim records.

Expected outputs:

```text
canonical_destinations.parquet
canonical_reviews.parquet
entity_links.parquet
entity_resolution_manifest.json
```

`destination_id` must be stable within a dataset version. False merges must be reviewed before annotation splitting.
