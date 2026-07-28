# SIPATURE Reproducibility Runbook

## Supported Environments

- Local CPU development: Python 3.10+ using `ml/requirements-dev.lock.txt`.
- Google Colab GPU: pinned `ml/requirements-colab.lock.txt`.
- Final deployment: Docker/DGX image must record CUDA, driver, Python, model, and data versions.

## Local Setup

```bash
cd ml
make setup
make check
make doctor
```

`make setup` installs the exact tested CPU/dev lock and the local package without resolving a second dependency set.

## Data Inventory Gate

```bash
cd ml
make inventory DATASET_DIR=../Datasets
```

Outputs:

```text
ml/artifacts/reports/data_inventory.json
ml/artifacts/reports/data_inventory.csv
```

The inventory records filename, bytes, SHA-256, encoding, header, row count, column count, and read errors. It never modifies source files.

## Colab Bootstrap

After mounting Google Drive:

```python
from pathlib import Path
from sipature_ml.colab import bootstrap_drive

DRIVE_ROOT = Path("/content/drive/MyDrive/SIPATURE")
paths = bootstrap_drive(DRIVE_ROOT)
```

Equivalent CLI:

```bash
sipature-ml bootstrap-drive --root /content/drive/MyDrive/SIPATURE
```

Persistent layout:

```text
SIPATURE/
├── data/{raw,interim,processed,annotations,splits}/
├── models/
├── predictions/
├── metrics/
├── figures/
├── reports/
└── runs/
```

## Notebook Setup Contract

Every notebook starts with:

1. Drive mount.
2. Repository/package installation.
3. Pinned Colab dependency installation.
4. Config loading.
5. `set_global_seed(config["seed"])`.
6. Environment snapshot.
7. Explicit input/output paths.

Every notebook ends with:

1. Intermediate/final outputs written to Drive.
2. Source and output hashes.
3. Config/model/data versions.
4. Metric file paths.
5. Run summary and known failures.

## Intermediate Checkpoint Contract

| Stage | Persistent output before continuing |
| --- | --- |
| Inventory | `reports/data_inventory.*`, known issues |
| Cleaning | `data/interim/*.parquet`, cleaning manifest, quarantine |
| Entity resolution | `data/processed/*`, entity-link manifest |
| Annotation | sampling/gold/adjudication JSONL, agreement report |
| Split | train/validation/test JSONL, locked split manifest |
| Baselines | model/vectorizer, validation/test metrics, config |
| IndoBERT | best checkpoint, tokenizer, training state/logs |
| Calibration | per-label thresholds and calibration metrics |
| Evaluation | immutable locked-test metrics and figures |
| Inference | review predictions with model version |
| Aggregation | destination signals and scoring manifest |
| Export | schema-validated app JSON and export manifest |

Do not rely on Colab memory or notebook output cells as artifact storage.

## Pipeline Commands

```bash
sipature-ml stages
sipature-ml validate-config
sipature-ml doctor
sipature-ml snapshot-run --output artifacts/reports/run-environment.json
sipature-ml run inventory --dataset-dir ../Datasets
sipature-ml run eda --dataset-dir ../Datasets
sipature-ml run clean --dataset-dir ../Datasets
sipature-ml run resolve-entities
sipature-ml run clean
sipature-ml run resolve-entities
sipature-ml run sample-annotations
sipature-ml run split
sipature-ml run train-keyword
sipature-ml run train-tfidf
sipature-ml run train-indobert
sipature-ml run calibrate
sipature-ml run evaluate
sipature-ml run infer
sipature-ml run aggregate
sipature-ml run prioritize
sipature-ml run export-app
```

Only `inventory` is implemented at the A2 stage. Other commands intentionally fail fast until their corresponding TODO is implemented and tested. Declaring a command is not evidence that its stage has been completed.

## Run Identity

Use a stable run ID such as:

```text
YYYYMMDD-HHMM_<stage>_<short-git-commit>_<config-version>
```

Every run records:

- Git commit and dirty state.
- Python/platform/hardware.
- Package versions.
- Config hashes.
- Source/output hashes.
- Seed and deterministic settings.
- Start/end time and status.
- Metrics and error-analysis references.

## Locked Test Policy

- Split by destination and keep duplicate groups together.
- Tune preprocessing, hyperparameters, thresholds, and calibration on train/validation only.
- Open the locked test set after model/config/threshold freeze.
- Never overwrite locked-test metrics; version a new experiment.
- Report failed experiments and residual risks.

## Reproduction Checklist

- [ ] Correct Python/profile selected.
- [ ] Exact dependency lock installed.
- [ ] Config hashes match the original run.
- [ ] Source data hashes match.
- [ ] Seed and environment snapshot recorded.
- [ ] Intermediate manifests available.
- [ ] Model/tokenizer/threshold versions match.
- [ ] Metrics regenerate within documented tolerance.
- [ ] App export passes JSON schema and UI smoke tests.
