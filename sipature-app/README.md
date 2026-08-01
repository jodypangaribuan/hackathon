# SIPATURE

AI early-warning and field-verification prioritization for tourism quality around Lake Toba.

The current app uses the privacy-safe aggregate projection of SIPATURE
Intelligence v1.0.4. Reported issues are signals requiring human verification,
not measurements of field conditions or public verdicts.

## Run

```bash
npm install
npm run dev
```

Open `http://localhost:3100`.

## Routes

| Route | Feature |
| --- | --- |
| `/` | Intelligence overview, map, filters, and actionable destination ranking |
| `/destinasi/[id]` | Reported issues, explainability, verification, and local scenario |
| `/intervensi` | Field-verification queue |
| `/umkm` | Candidate interventions; not investment opportunities |
| `/simulator` | Non-causal issue-removal scenarios |
| `/analyzer` | Clearly separated deterministic lexical sandbox |
| `/metode` | Model contract, traceability, limitations, and Responsible AI |

## Commands

```bash
npm run data:generate
npm run typecheck
npm run build
```

`npm run data:generate` verifies the frozen source export hash and generates a
sanitized application projection. The generated bundle excludes evidence text
and all review-level identifiers because evidence remains restricted pending
privacy review.

## Model Status

- Aspect model: `tfidf-aspect-silver-v1`.
- Polarity: deterministic `lexical-polarity-v1` fallback without probability.
- Severity, facility gap, and feasibility: unavailable and renormalized away.
- Evaluation reference: weak-supervision silver labels, not human gold.
- Expert judgments: 0 of 25 prepared cases completed.
- Application mode: precomputed batch; the analyzer is a separate lexical sandbox.
