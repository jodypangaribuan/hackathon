# SIPATURE ML

Reproducible data and model pipeline for SIPATURE. Colab notebooks orchestrate exploration and GPU training; importable Python modules contain reusable logic.

## Pipeline stages

```text
raw CSV -> ingest -> clean -> entity resolution -> annotation sampling
-> destination-group split -> keyword/TF-IDF baselines -> IndoBERT
-> threshold calibration -> locked test evaluation -> batch inference
-> destination aggregation -> intervention priority -> app export
```

## Layout

| Path | Purpose |
| --- | --- |
| `configs/` | Versioned pipeline, taxonomy, split, training, scoring configs |
| `data/raw/` | Immutable organizer input snapshots or Drive mount instructions |
| `data/interim/` | Cleaned but not canonical data |
| `data/processed/` | Canonical destinations/reviews and model-ready data |
| `data/annotations/` | Samples, gold labels, adjudication records |
| `data/splits/` | Locked train/validation/test manifests |
| `notebooks/` | Ordered Colab workflow |
| `src/sipature_ml/` | Importable pipeline package |
| `tests/` | Unit/schema/leakage tests |
| `artifacts/` | Models, metrics, figures, reports |

## Local setup

```bash
cd ml
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Python 3.10 or newer is required. Google Colab's current Python runtime is compatible.

Install training dependencies only in Colab/GPU environments:

```bash
pip install -e ".[train]"
```

## Rules

- Never edit organizer CSVs in place.
- Never tune against the locked test split.
- Every output must carry source/config/model version metadata.
- Do not commit raw data, model weights, predictions, or secrets.
- Do not call baseline outputs trained-model predictions.
- The Next.js app consumes exported product data through `contracts/app-export.schema.json`.

Current status: project structure and contracts exist; pipeline stages remain to be implemented and validated.
