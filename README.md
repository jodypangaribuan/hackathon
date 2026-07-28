# SIPATURE Workspace

SIPATURE is an evidence-based early-warning and intervention-priority system for Lake Toba tourism quality.

## Workspace Map

| Path | Purpose |
| --- | --- |
| `Datasets/` | Organizer-provided source data; do not edit in place |
| `ml/` | Reproducible EDA, data engineering, training, evaluation, inference, export |
| `docs/` | Data, annotation, model, Responsible AI, integration, deployment docs |
| `sipature-app/` | Next.js decision-support product |
| `SIPATURE-Project-Charter.md` | Locked problem, users, scope, demo cases |
| `SIPATURE-Implementation-Plan.md` | End-to-end technical plan |
| `SIPATURE-Hackathon-TODO.md` | Preliminary/final execution tracker |
| `SIPATURE-Laporan-Analisis-Template.md` | Eight-chapter report template |

## Current Truth

- The web application currently contains a keyword + rating baseline for UI demonstration.
- Trained IndoBERT outputs and locked-test metrics do not exist yet.
- Do not present baseline scores as trained-model results.
- ML outputs replace baseline app data only after schema, metric, evidence, and smoke-test gates pass.

## Quick Checks

```bash
# Web app
cd sipature-app
npm run typecheck
npm run build

# ML package (after local setup)
cd ml
pip install -e ".[dev]"
pytest
sipature-ml stages
```
