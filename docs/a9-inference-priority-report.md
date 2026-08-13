# SIPATURE A9 Inference, Aggregation, and Priority Report

## Production Contract

Run `20260801-a9-tfidf-lexical-v1-r5` uses the A8-selected `tfidf-aspect-silver-v1` artifact for aspect detection. The model SHA-256 is `9132efbf60f24c234571902026d9d0e1d88a0a4911098efb955d50e2c5a07606`; its manifest SHA-256 is `61df6aa0b0064b163d86b88f197731ff179c7217e8d1d8d428dc95fe3c8097ce`. Inference requires scikit-learn 1.7.2, matching the training environment.

The controlled IndoBERT polarity weights were not available in this workspace. A9 therefore uses the explicitly versioned deterministic fallback `lexical-polarity-v1` on aspects selected by TF-IDF. It must not be described as IndoBERT or as a calibrated polarity model. Severity remains `unavailable_no_supported_model`; missing severity is never encoded as low or zero.

## Full-Corpus Result

The immutable r5 run processed all 12,234 canonical textual reviews. It produced 9,785 aspect predictions for 5,942 reviews, 1,682 destination-aspect signals across 280 destinations, and 598 restricted evidence items. All 388 canonical technical destination records were retained, including destinations with no sufficient signal. Exposure uses all 22,169 clean records; 1,670 signals have additional rating-only exposure context beyond their textual support.

| Output | Count |
| --- | ---: |
| Canonical textual reviews | 12,234 |
| Reviews with at least one aspect | 5,942 |
| Aspect predictions | 9,785 |
| Destination-aspect signals | 1,682 |
| Destinations with signals | 280 |
| Restricted evidence items | 598 |
| Total canonical destination records | 388 |

Signal data confidence was `medium` for 49 signals, `low` for 769, and `insufficient` for 864. No signal has a severe count because no supported severity model exists.

## Aggregation and Priority

Aggregation uses validation-selected TF-IDF thresholds, Bayesian smoothing with `alpha=10`, two-year freshness half-life, a duplicate-group discount of 0.50, and a maximum of three high-confidence negative evidence snippets per destination-aspect. The corpus maximum publication estimate is the reproducible time anchor; missing dates receive a conservative 0.50 freshness weight.

Priority uses complaint frequency, model confidence, persistence, and visitor exposure. Severity, facility gap, and feasibility are unavailable, so their weights are removed and available weights are renormalized. Output exposes original weights, effective weights, values, and contributions. Confidence is lowered when components are missing. The lexical polarity fallback emits labels only and does not fabricate a probability.

The evidence gate produced 210 actionable issues across 103 destinations. Every actionable issue has anonymized evidence, confidence, data status, explanation, recommended field verification, and a deterministic candidate intervention. There were zero actionable issues without evidence and zero destination-level priority propagation errors. Unresolved destination placeholders are retained for coverage but receive `Insufficient Data`, never an operational rank.

These are triage signals against weak-supervision-trained components, not proof that a field condition exists. Field verification remains mandatory.

## Sensitivity and Human Gate

A one-at-a-time +20% perturbation was run for all seven configured priority weights. Top-20 Jaccard overlap ranged from 0.8182 to 1.0000. This is an initial mechanical stability check, not stakeholder validation.

A deterministic restricted queue of 25 destinations was prepared for expert review. All judgment fields remain empty. External expert review is not possible for this team, so evidence correctness, unsupported-alert rate, intervention relevance, NDCG, and rank correlation remain unavailable and must not be claimed. Internal validation is limited to the mechanical sensitivity check above plus a small team gold-annotation reference (see `docs/annotation-runbook.md`).

## Privacy and Integration Status

Review predictions, provenance, evidence, the expert queue, and the generated app export remain under `ml/artifacts/a9/` and are ignored by Git. The safe aggregate evidence at `docs/evidence/a9/20260801-a9-tfidf-lexical-v1-r5/summary.json` contains no review text or reviewer identity.

The generated export passed the strict A9 JSON schema and all stage artifact hashes matched their manifests. Its SHA-256 is `f349a499afe04cdb9fafde8101e136470a41ca53815bd0c829dd62f07ca812b0`. It has not replaced the application baseline. A10 still requires privacy review, app-taxonomy adaptation, runtime validation, UI version display, typecheck/build, and route smoke tests.
