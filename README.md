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
| `SIPATURE-Laporan-Analisis-Draft.md` | Evidence-backed report draft, updated as pipeline artifacts become available |

## Current Truth

- The web application currently contains a keyword + rating baseline for UI demonstration.
- A7 trained IndoBERT aspect and polarity candidates; A8 calibrated on validation and evaluated the locked silver test exactly once.
- IndoBERT aspect Macro F1 was 0.5247, below TF-IDF 0.7201; IndoBERT polarity Macro F1 was 0.7459 on reference-annotated aspects.
- Severity remains unavailable because the A7 class-support gate did not produce a model.
- A9 completed restricted full-corpus TF-IDF inference and produced an evidence-gated aggregate export; external expert review is out of scope (internal validation via sensitivity analysis and a team gold-annotation reference).
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
A8 execution and safe aggregate evidence are documented in `docs/indobert-a8-evaluation-report.md`. Results are silver-label agreement, not human-gold performance; review-level predictions and error cases remain restricted.

A9 execution is documented in `docs/a9-inference-priority-report.md`. Its generated review predictions, evidence, expert queue, and app export remain restricted under `ml/artifacts/a9/` and are not committed.
