# SIPATURE ML

Reproducible data and model pipeline for SIPATURE. Colab notebooks orchestrate exploration and GPU training; importable Python modules contain reusable logic.

## Pipeline stages

```text
raw CSV -> ingest -> clean -> entity resolution -> annotation sampling/silver labels
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
| `data/annotations/` | Restricted samples, silver labels, uncertainty queue; optional human artifacts |
| `data/splits/` | Locked train/validation/test manifests |
| `notebooks/` | Ordered Colab workflow |
| `src/sipature_ml/` | Importable pipeline package |
| `tests/` | Unit/schema/leakage tests |
| `artifacts/` | Models, metrics, figures, reports |

## Local setup

```bash
cd ml
make setup
make check
make inventory DATASET_DIR=../Datasets
make eda DATASET_DIR=../Datasets
make clean-data DATASET_DIR=../Datasets
make resolve-entities
make annotation-sample
make silver-annotate
make split-silver
make baselines
# GPU/Colab only; downloads the pinned model and trains
make train-indobert
```

Python 3.10 or newer is required. Google Colab's current Python runtime is compatible.

Install training dependencies only in Colab/GPU environments:

```bash
pip install -r requirements-colab.lock.txt
pip install --no-deps -e .
```

## Reproducible commands

```bash
make stages       # list the 15 declared stages, including EDA
make doctor       # print environment, package, Git, config metadata
make snapshot     # persist the current run environment
make inventory    # run source inventory
make split-silver # create locked destination/repeated-text-safe splits
make baselines    # train/evaluate keyword and TF-IDF against silver
make train-indobert # GPU train/validation only; locked test remains unopened
```

Full local/Colab instructions and intermediate checkpoint rules are in `../docs/reproducibility-runbook.md`.

## Rules

- Never edit organizer CSVs in place.
- Never tune against the locked test split.
- Every output must carry source/config/model version metadata.
- Do not commit raw data, model weights, predictions, or secrets.
- Do not call baseline outputs trained-model predictions.
- The Next.js app consumes exported product data through `contracts/app-export.schema.json`.

Current status: A1-A6 are complete. A7 run `20260801-1024_indobert-silver-v1` trained aspect and polarity candidates on Colab train/validation data and passed offline reload; severity was skipped by its support gate. A8 calibration/evaluation code, tests, CLI, notebook, and runbook are implementation ready, but calibration and locked-test execution remain pending. See `../docs/a8-calibration-evaluation-runbook.md`.
