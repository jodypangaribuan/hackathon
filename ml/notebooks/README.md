# Colab Notebook Order

Create and run notebooks in this order:

| Notebook | Runtime | Input | Required output |
| --- | --- | --- | --- |
| `01_data_inventory_and_eda.ipynb` | CPU | Raw CSV | Inventory, EDA figures, known issues |
| `02_cleaning_and_entity_resolution.ipynb` | CPU | Raw CSV | Interim/processed Parquet, entity audit |
| `03_annotation_sampling.ipynb` | CPU | Canonical reviews | Sampling candidates |
| `04_annotation_quality_and_split.ipynb` | CPU | Human labels | Gold labels, agreement, locked splits |
| `05_keyword_tfidf_baselines.ipynb` | CPU | Splits | Baseline artifacts and metrics |
| `06_indobert_aspect_training.ipynb` | GPU | Splits | Aspect checkpoint and logs |
| `07_polarity_severity_training.ipynb` | GPU | Aspect instances | Polarity/severity checkpoints |
| `08_calibration_and_evaluation.ipynb` | GPU/CPU | Validation/test | Thresholds, locked metrics, figures |
| `09_batch_inference_and_aggregation.ipynb` | GPU | All clean reviews | Predictions, destination signals |
| `10_system_evaluation_and_export.ipynb` | CPU | Signals/expert review | System metrics and app export |

Notebook rules:

1. First cell mounts Drive and records runtime/package versions.
2. Parameters and paths are declared in one configuration cell.
3. Intermediate outputs are written to Drive after each expensive stage.
4. Reusable business logic is imported from `sipature_ml`, not duplicated across notebooks.
5. Test labels remain inaccessible until the experiment config is locked.
6. The notebook ends with output paths, hashes, and a run summary.
