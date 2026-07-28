# Experiment Log

Append one section per experiment. Do not rewrite failed experiments.

## Experiment Template

### `[EXPERIMENT_ID]` — `[TITLE]`

- Date/owner: `[VALUE]`
- Hypothesis: `[VALUE]`
- Data/annotation/split version: `[VALUE]`
- Config and git commit: `[VALUE]`
- Hardware/runtime: `[VALUE]`
- Metrics artifact: `[PATH]`
- Result: `[VALUE]`
- Error analysis: `[PATH/SUMMARY]`
- Decision: Keep / Reject / Iterate
- Rationale and next action: `[VALUE]`

## Actual Experiments

### `silver-baselines-1.0.0` — Destination-Grouped Keyword and TF-IDF Baselines

- Date/owner: 28 July 2026 / Data-ML pipeline.
- Hypothesis: Combined word+character TF-IDF improves validation silver agreement over either representation alone while preserving destination/repeated-text leakage controls.
- Data/annotation/split version: `silver-1.0.0` / `silver-split-1.0.0`; 922 train, 196 validation, 202 locked test records.
- Config and git commit: `ml/configs/training.yaml`; dirty workspace recorded, no commit created.
- Hardware/runtime: Local CPU, Python 3.10, scikit-learn 1.7.2.
- Metrics artifact: `ml/artifacts/metrics/{keyword,tfidf}-silver-v1-test-metrics.json`.
- Result: Combined word+char validation Macro F1 0.8117; locked silver-test Keyword Macro F1 0.9768 and TF-IDF Macro F1 0.7201.
- Error analysis: `ml/artifacts/reports/baseline_silver_test_errors.csv`; 97 TF-IDF aspect disagreements, including 57 on `review_recommended` records.
- Decision: Keep TF-IDF as classical baseline; treat keyword as a circular rule-reconstruction ceiling.
- Rationale and next action: Train A7 only on train/validation; do not claim human-gold performance or retune using locked test.
