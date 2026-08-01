# A10 Preliminary Product Integration

## Status

SIPATURE now uses the privacy-safe aggregate projection of A9 run
`20260801-a9-tfidf-lexical-v1-r5`. The original UI hierarchy, visual tokens,
map interaction, destination cards, navigation, and responsive layout are
preserved. Mock ML scores, mock opportunities, and review snippets from the
blueprint were removed.

## Integrated Artifacts

| Item | Integrated value |
| --- | ---: |
| Canonical destinations | 388 |
| Mappable destinations | 322 |
| Unresolved destinations | 66 |
| Text reviews inferred | 12,234 |
| Reviews with predictions | 5,942 |
| Aspect predictions | 9,785 |
| Destinations with signals | 280 |
| Actionable destinations | 103 |
| Actionable issues/candidate interventions | 210 |

The application displays model version, generation time, source hash,
taxonomy version, confidence, priority, complaint-derived health, support,
recommended field verification, candidate intervention, and missing component
status.

## Data Boundary

`sipature-app/scripts/generate-a9-data.mjs` verifies the frozen app export
SHA-256 before producing:

- `src/data/generated/a9-places.json`
- `src/data/generated/a9-interventions.json`
- `src/data/generated/a9-corpus.json`

The public projection excludes evidence text, review IDs, reviewer identity,
source files, source rows, profile links, and review-level provenance. Evidence
remains restricted pending privacy review. The UI explains this state instead
of showing mock or fabricated evidence.

The legacy blueprint data was reduced to `metadata-enrichment.json`, containing
only place identity, coordinates, category, address, fee, hours, rating,
operating status, facilities, district, and subdistrict. No legacy ML score,
aspect row, trend, evidence, opportunity, or rating-derived severity remains.

## Product Semantics

- The 14-aspect A9 taxonomy is preserved without collapsing independent
  aspects.
- `priority_score` replaces the unrelated blueprint friction score.
- Bayesian-smoothed complaint rate replaces the unrelated Wilson rate.
- Severity, facility gap, feasibility, and trend remain unavailable.
- `Insufficient Data` is not treated as healthy or as zero reviews.
- Unresolved destinations remain searchable/auditable but are not mapped or
  ranked.
- The former UMKM page now shows candidate interventions, not investment or
  market claims unsupported by A9.
- The simulator removes selected exported issues under a fixed non-causal
  assumption and returns unknown health when no issue remains.
- The analyzer is explicitly a separate lexical sandbox using synthetic
  examples. It does not claim to run A9 and does not alter batch priorities.

## Verification

The following checks passed on 2026-08-01:

```text
npm run data:a9
npm run typecheck
npm run build
```

Production route smoke tests returned HTTP 200 for overview, queue, candidate
interventions, simulator, analyzer, method, actionable destination detail,
insufficient destination detail, unresolved destination detail, and all API
routes.

Semantic smoke assertions verified:

- Model version `a9-tfidf-lexical-v1.0.4`.
- 388 loaded destinations and 103 actionable destinations.
- No evidence/review provenance keys in destination API output.
- Simulator always returns a non-causal caveat.
- Analyzer returns method `lexical_demo_v1` and no A9 model version.
- No restricted review identifiers in `.next`.
- No absolute workspace path in client static assets.

## Remaining Human Gates

- Complete expert review of 25 prepared cases.
- Calculate evidence correctness, unsupported alert rate, and intervention
  relevance.
- Complete evidence privacy review before enabling verbatim snippets.
- Perform manual visual QA on target phones/tablets in addition to responsive
  code and route checks.
