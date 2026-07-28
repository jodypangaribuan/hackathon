# Generated SIPATURE Data

This directory receives versioned exports from the ML pipeline. Current application data outside this directory remains a keyword + rating baseline for UI demonstration.

Before replacing any app data:

1. Validate against `ml/contracts/app-export.schema.json`.
2. Verify model, data, config, and schema versions.
3. Verify every displayed evidence item has source provenance.
4. Confirm missing data is not represented as healthy/no issue.
5. Run Next.js typecheck, build, and route smoke tests.
6. Display model version and generated timestamp in the product.

Generated JSON is ignored by Git unless intentionally approved for the submission package.
