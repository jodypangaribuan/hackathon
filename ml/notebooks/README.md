# Colab Notebook Order

Run notebooks in this order. Stages whose logic lives entirely in the
`sipature_ml` package and the Makefile/CLI (rather than a notebook) are
marked "pipeline" and have no notebook file.

| Notebook | Runtime | Input | Required output | Status |
| --- | --- | --- | --- | --- |
| `01_data_inventory_and_eda.ipynb` | CPU | Raw CSV | Inventory, EDA figures, known issues | Done (run 2026-08-13) |
| `02_cleaning_and_entity_resolution.ipynb` | CPU | Raw CSV | Interim/processed Parquet, entity audit | Done (run 2026-08-13) |
| `03_annotation_sampling_and_silver.ipynb` | CPU | Canonical reviews | Sampling candidates + AI-assisted silver labels | Created (not yet run) |
| `04_annotation_quality_and_split.ipynb` | CPU | Silver labels | Gold labels, agreement, locked splits | Pipeline (`sipature-ml split-silver`) |
| `05_keyword_tfidf_baselines.ipynb` | CPU | Splits | Baseline artifacts and metrics | Pipeline (`sipature-ml train-baselines`) |
| `06_indobert_aspect_training.ipynb` | GPU | Splits | Aspect checkpoint and logs | Done (`20260801-1024_indobert-silver-v1`) |
| `07_polarity_severity_training.ipynb` | GPU | Aspect instances | Polarity/severity checkpoints | Stub |
| `08_calibration_and_evaluation.ipynb` | GPU/CPU | Validation/test | Thresholds, locked metrics, figures | Done (`20260801_indobert-silver-v1_locked-test-v1`) |
| `09_batch_inference_and_aggregation.ipynb` | GPU | All clean reviews | Predictions, destination signals | Pipeline (`infer-corpus` / `aggregate-destinations`) |
| `10_system_evaluation_and_export.ipynb` | CPU | Signals/expert review | System metrics and app export | Pipeline (`export-app`) |

## Executed runs (notebooks 01–02)

Notebooks `01` and `02` were executed on Google Colab CPU (Python 3.12.13,
pinned `requirements-colab.lock.txt`) against the raw CSVs staged in
`SIPATURE/data/raw` on Drive. Results match the existing reports
`docs/eda-report.md` and `docs/cleaning-entity-resolution-report.md`.

- `01`: 14 CSVs inventoried; 16 EDA figures generated; persisted to
  `SIPATURE/reports/` and `SIPATURE/figures/eda/`.
- `02`: cleaning reduced 22,302 raw reviews to 22,169 clean records
  (12,234 textual); entity resolution produced 388 canonical destinations
  (322 metadata anchors + 66 unresolved placeholders), 810 source links, and
  all clean reviews received a `destination_id`. Persisted to
  `SIPATURE/data/interim/`, `SIPATURE/data/processed/`, `SIPATURE/reports/`,
  and `SIPATURE/figures/cleaning-entity/`.

Notebook rules:

1. First cell mounts Drive and records runtime/package versions.
2. Parameters and paths are declared in one configuration cell.
3. Intermediate outputs are written to Drive after each expensive stage.
4. Reusable business logic is imported from `sipature_ml`, not duplicated across notebooks.
5. Test labels remain inaccessible until the experiment config is locked.
6. The notebook ends with output paths, hashes, and a run summary.
