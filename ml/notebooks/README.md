# Colab Notebook Order

Run notebooks in this order. Stages whose logic lives entirely in the
`sipature_ml` package and the Makefile/CLI (rather than a notebook) are
marked "pipeline" and have no notebook file.

| Notebook | Runtime | Input | Required output | Status |
| --- | --- | --- | --- | --- |
| `01_data_inventory_and_eda.ipynb` | CPU | Raw CSV | Inventory, EDA figures, known issues | Done (run 2026-08-13) |
| `02_cleaning_and_entity_resolution.ipynb` | CPU | Raw CSV | Interim/processed Parquet, entity audit | Done (run 2026-08-13) |
| `03_annotation_sampling_and_silver.ipynb` | CPU | Canonical reviews | Sampling candidates + AI-assisted silver labels | Done (run 2026-08-13) |
| `04_split.ipynb` | CPU | Silver labels + canonical reviews | Locked leakage-safe train/validation/test | Done (run 2026-08-13) |
| `05_keyword_tfidf_baselines.ipynb` | CPU | Splits | Baseline artifacts and metrics | Done (run 2026-08-13) |
| `06_indobert_aspect_training.ipynb` | GPU | Splits | Aspect checkpoint and logs | Done (run `20260813-1050_indobert-silver-v1`) |
| `07_calibration_and_evaluation.ipynb` | GPU/CPU | Validation/test | Thresholds, locked metrics, figures | Done (run `20260813-1050_indobert-silver-v1_locked-test-v1`) |
| `08_batch_inference_and_aggregation.ipynb` | CPU | All clean reviews | Predictions, destination signals | Created (not yet run) |
| `09_system_evaluation_and_export.ipynb` | CPU | Signals/expert review | System metrics and app export | Pipeline (`export-app`) |

## Executed runs (notebooks 01–05)

Notebooks `01`–`05` were executed on Google Colab CPU (Python 3.12.13,
pinned `requirements-colab.lock.txt`) against the raw CSVs staged in
`SIPATURE/data/raw` on Drive. Results match the existing reports
`docs/eda-report.md`, `docs/cleaning-entity-resolution-report.md`,
`docs/taxonomy-annotation-report.md`, and
`docs/leakage-safe-split-baseline-report.md`.

- `01`: 14 CSVs inventoried; 16 EDA figures generated; persisted to
  `SIPATURE/reports/` and `SIPATURE/figures/eda/`.
- `02`: cleaning reduced 22,302 raw reviews to 22,169 clean records
  (12,234 textual); entity resolution produced 388 canonical destinations
  (322 metadata anchors + 66 unresolved placeholders), 810 source links, and
  all clean reviews received a `destination_id`. Persisted to
  `SIPATURE/data/interim/`, `SIPATURE/data/processed/`, `SIPATURE/reports/`,
  and `SIPATURE/figures/cleaning-entity/`.
- `03`: sampled 120 pilot + 1,200 main reviews (240 double-annotated, 262
  destinations, 0 overlap) from the 12,234-review text pool; produced
  AI-assisted silver labels `silver-v1.0.0.jsonl` (1,320 records: 489
  consensus / 497 no-supported-aspect / 334 review-recommended, mean pass
  agreement 0.8827) plus 11 figures. Persisted to `SIPATURE/data/annotations/`,
  `SIPATURE/reports/`, and `SIPATURE/figures/annotation/`.
- `04`: created and locked the leakage-safe split `silver-split-1.0.0`
  (922 train / 196 validation / 202 test; 187/40/40 destinations; all
  leakage checks 0; 219 components, 10 multi-destination, 23 cross-destination
  repeated-text groups). Persisted to `SIPATURE/data/splits/` and
  `SIPATURE/reports/`; the test split remains locked until A8.
- `05`: trained keyword + TF-IDF baselines on train, selected `word_char`
  representation on validation, and evaluated the locked silver test once —
  Keyword Macro F1 0.9768 / Micro 0.9783; TF-IDF Macro F1 0.7201 / Micro
  0.8040. Persisted metrics, `tfidf-aspect-silver-v1/model.joblib`, and 3
  figures to `SIPATURE/metrics/`, `SIPATURE/models/`, `SIPATURE/reports/`,
  and `SIPATURE/figures/baselines/`.
- `06`: (GPU, Tesla T4) trained IndoBERT on train/validation only (test not
  read) — aspect validation Macro F1 0.4012, polarity validation Macro F1
  0.7044, severity skipped by support gate (high 19 < 20), offline reload
  passed. Run `20260813-1050_indobert-silver-v1` persisted to
  `SIPATURE/runs/` plus an evidence bundle; results match the prior A7 run
  `20260801-1024_indobert-silver-v1`.
- `07`: (GPU, Tesla T4) A8 calibration + one-shot locked evaluation on run
  `20260813-1050_indobert-silver-v1`. Calibration froze temperature 0.6 on
  validation only (test not read). Locked test evaluated exactly once: aspect
  Macro F1 0.5247 / Micro 0.5241, polarity Macro F1 0.7459 (248), ECE 0.2021,
  Brier 0.1258; severity `unavailable_no_model`. Persisted to
  `SIPATURE/calibration/`, `SIPATURE/evaluation/`, and `SIPATURE/evidence/`;
  results match the prior A8 run `20260801_indobert-silver-v1_locked-test-v1`.

Notebook rules:

1. First cell mounts Drive and records runtime/package versions.
2. Parameters and paths are declared in one configuration cell.
3. Intermediate outputs are written to Drive after each expensive stage.
4. Reusable business logic is imported from `sipature_ml`, not duplicated across notebooks.
5. Test labels remain inaccessible until the experiment config is locked.
6. The notebook ends with output paths, hashes, and a run summary.
