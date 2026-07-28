# SIPATURE AI-Assisted Silver Annotation Runbook

## Scope

The active A5 workflow produces **AI-assisted weak-supervision silver labels**. It does not produce human annotations, inter-annotator agreement, adjudicated labels, or a gold dataset. The human commands remain available only as a future quality upgrade.

## Inputs

- `ml/configs/taxonomy.yaml`: taxonomy `1.0.0-rc1`, seed terms, and sampling rules.
- `docs/annotation-guideline.md`: aspect, polarity, severity, evidence, and boundary definitions.
- `ml/data/processed/reviews_clean.parquet`: restricted clean review data.
- `ml/contracts/silver-annotation.schema.json`: silver output contract.

## Generate Samples

From `ml/`:

```bash
make annotation-sample
```

This deterministically creates a 120-review pilot and a disjoint 1.200-review main sample using seed 42. Sampling is stratified and oversamples rare candidate aspects. Candidate retrieval is sampling evidence, not a label.

## Generate Silver Labels

```bash
make silver-annotate
```

The command runs three deterministic profiles: `strict`, `balanced`, and `recall`. A label is retained with at least two matching votes. `silver_confidence` is the fraction of agreeing passes and is not a calibrated probability.

Outputs under `ml/data/annotations/` are restricted and Git-ignored:

- `silver-v1.0.0.jsonl`
- `silver-v1.0.0.manifest.json`
- `silver-disagreement-queue.jsonl`
- `silver-pass-strict.jsonl`
- `silver-pass-balanced.jsonl`
- `silver-pass-recall.jsonl`

The aggregate summary is written to `ml/artifacts/reports/silver_annotation_summary.json`.

## Validate

```bash
sipature-ml silver-validate data/annotations/silver-v1.0.0.jsonl
```

Validation must return zero invalid records. It checks IDs, taxonomy values, unique aspects, polarity/severity constraints, vote counts, confidence, evidence provenance, and verbatim evidence spans.

## Audit

Review all high-severity labels and samples from every aspect/polarity pair. Prioritize `silver-disagreement-queue.jsonl`. Systematic findings require rule or taxonomy changes, regression tests, regeneration, validation, and a new artifact hash.

The v1.0.0 audit corrected negation and question handling, aspect-aware severity, and boundaries involving access/maintenance, sanitation/cleanliness, toilet/public facilities, crowding, and opening hours. The remaining disagreement queue is retained as uncertainty rather than silently promoted to consensus.

## Figures

```bash
sipature-ml silver-figures --figure-dir ../docs/figures/eda
```

Figures are aggregate only and must not expose review text or reviewer identity.

## Optional Human Upgrade

Human pilot, agreement, adjudication, and gold-freeze commands remain implemented but are not part of the active run. If used later, three annotators must work independently, agreement gates must pass, all disagreements must be adjudicated, and the resulting artifact must be versioned separately. AI pass agreement must never be reported as human agreement.
