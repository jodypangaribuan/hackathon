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

### `20260801-1024_indobert-silver-v1` — IndoBERT Aspect and Polarity Candidate

- Date/owner: 1 August 2026 / SIPATURE ML pipeline.
- Hypothesis: A pinned IndoBERT encoder can learn multilabel aspects and aspect-conditioned polarity from leakage-controlled silver train data.
- Data/annotation/split version: `silver-1.0.0` / `silver-split-1.0.0`; 922 train and 196 validation reviews; locked test unopened.
- Config and git commit: `training.yaml` SHA-256 `fd5c68b78e7b284e79e404b9562058fb7502018fb9d832d1f6b93cde525b6e4e`; commit `24f140cac79a7a7fb9e2910fe22987d78d0c5f34`.
- Hardware/runtime: Google Colab Tesla T4, Python 3.12.13, PyTorch 2.7.1, Transformers 4.53.2.
- Metrics artifact: `docs/evidence/indobert/20260801-1024_indobert-silver-v1/`.
- Result: Aspect validation Macro F1 0.4012 at temporary threshold 0.50; polarity validation Macro F1 0.7044; offline reload passed for both.
- Error analysis: Pending A8 threshold tuning and aggregate review of validation errors.
- Decision: Keep as the A7 candidate and proceed to A8 calibration; do not open locked test yet.
- Rationale and next action: Aspect loss and validation loss continued to decrease through epoch 4. Polarity validation loss flattened after epoch 3 while Macro F1 improved marginally. Severity was skipped because high support was 19 train, below the minimum of 20.

### `20260801_indobert-silver-v1_locked-test-v1` — Frozen IndoBERT Calibration and One-Shot Evaluation

- Date/owner: 1 August 2026 / SIPATURE ML pipeline.
- Hypothesis: Validation-only temperature scaling and per-aspect thresholds allow the A7 contextual model to outperform the learned TF-IDF aspect baseline on the locked silver test.
- Data/annotation/split version: `silver-1.0.0` / `silver-split-1.0.0`; 196 validation records for calibration and 202 locked-test records evaluated once.
- Config and git commit: calibration config canonical SHA-256 `4531b2c101900450e3cc245934eee00725e29c2c6647746b9c2ad2fa084cf0ff`; commit `9eaca4f2780cdb88d2381fa558dd9bd445297c9b`.
- Hardware/runtime: Google Colab Tesla T4, Python 3.12.13, PyTorch 2.7.1, Transformers 4.53.2.
- Metrics artifact: `docs/evidence/indobert/20260801_indobert-silver-v1_a8-evidence/`; evaluation metrics SHA-256 `923a000e43c9f6528ac53a5c3b99827cfd0ed55ec38db5f3c9a2564f3db0f9da`.
- Result: Validation tuning improved aspect Macro F1 from 0.4012 to 0.5535. Locked-test IndoBERT aspect Macro/Micro F1 was 0.5247/0.5241, below TF-IDF 0.7201/0.8040. Polarity Macro F1 was 0.7459 over 248 reference aspect instances. Overall micro Precision@Alert was 0.5886 over 175 predictions; ECE was 0.2021 and Brier 0.1258.
- Error analysis: Review-level FP/FN records and deterministic 50-case queues remain restricted in controlled Drive storage; manual linguistic and reputational-risk coding is pending.
- Decision: Reject the IndoBERT aspect head as the final aspect detector for this benchmark; keep TF-IDF as the current learned aspect candidate and retain IndoBERT polarity as a separate candidate.
- Rationale and next action: The contextual aspect model underperformed TF-IDF while requiring more compute. Do not retune from locked-test results. Complete manual restricted error audit, then define the A9 production contract using TF-IDF aspect detection and an explicitly versioned polarity decision.
