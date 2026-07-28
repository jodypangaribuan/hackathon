# Locked Data Splits

Destination-grouped train, validation, and test data.

Expected outputs:

```text
train_v1.jsonl
validation_v1.jsonl
test_v1.jsonl
split_manifest_v1.json
```

Rules:

- A destination occurs in exactly one split.
- A duplicate group occurs in exactly one split.
- The test split is locked before model tuning.
- The manifest records seed, destination IDs, label distributions, annotation version, and source hash.
