# ML-to-App Integration Contract

## Principle

The SIPATURE dashboard consumes versioned, precomputed batch inference. It must not load or run IndoBERT during normal page rendering. Real-time inference is limited to the analyzer/API.

## Contract

Canonical schema: `ml/contracts/app-export.schema.json`.

Every export includes:

- `schema_version`.
- `model_version`.
- `generated_at`.
- Source manifest reference.
- Destination confidence, priority, issues, and evidence provenance.

## Export Location

Development target:

```text
sipature-app/src/data/generated/
```

Do not overwrite current baseline files until the new export passes schema validation and UI smoke tests. Keep baseline and trained-model exports visibly distinguishable.

## Version Compatibility

| App schema | Supported model export | Status |
| --- | --- | --- |
| `1.x` | `1.x` | Planned |

Breaking schema changes require a new major version and coordinated app update.

## Required Gates

1. JSON schema validation passes.
2. Model/data/config hashes are present.
3. Every displayed evidence item resolves to source provenance.
4. Missing data is not encoded as healthy/no issue.
5. App displays model version and generation time.
6. Smoke tests cover overview, map, destination, queue, simulator, analyzer.
