# IndoBERT A7 Training Runbook

## Status And Scope

The A7 implementation is ready for a Colab GPU run but has not been trained. No IndoBERT weights, validation metrics, checkpoint claims, or reload claims exist until the steps below complete successfully. The training labels are AI-assisted silver references, not human gold.

The selected encoder is `indobenchmark/indobert-base-p1` at immutable revision `c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2`: MIT license, approximately 124.5M parameters, and `BertTokenizer` WordPiece tokenization. The revision is pinned in `ml/configs/training.yaml` and enforced by code.

## Locked Test Prohibition

A7 may read only `train_silver_v1.jsonl`, `validation_silver_v1.jsonl`, and `split_manifest_silver_v1.json`. Do not inspect, load, tokenize, summarize, or evaluate `test_silver_v1.jsonl` in notebooks 06 or 07. The package verifies train and validation hashes from the manifest and deliberately does not resolve the test path. Test access belongs to A8 only, after model and thresholds are frozen.

## Exact Colab Steps

1. Open Google Colab, select **Runtime > Change runtime type > T4 GPU** or a stronger GPU, and verify it with `!nvidia-smi`.
2. Mount Drive and clone or update the exact repository commit.

```python
from google.colab import drive
drive.mount("/content/drive")
```

```bash
%cd /content
!git clone <REPOSITORY_URL> hackathon
%cd /content/hackathon/ml
!git rev-parse HEAD
```

3. Install the locked GPU profile and package. Restart the runtime if Colab requests it, then remount Drive and return to the same directory.

```bash
!python -m pip install -r requirements-colab.lock.txt
!python -m pip install --no-deps -e .
```

4. Copy the three split control/input files from Drive into `/content/hackathon/ml/data/splits/`. Do not copy the test JSONL into the Colab working directory for A7.
5. Record and inspect the environment without downloading the model yet.

```bash
!sipature-ml doctor
!sipature-ml validate-config
```

6. Set a unique persistent run ID and execute the package runner. This is the first step that downloads the pinned model and starts training.

```bash
RUN_ID=YYYYMMDD-HHMM_indobert-silver-v1_<short-commit>
!sipature-ml train-indobert --split-dir data/splits --artifact-dir /content/drive/MyDrive/SIPATURE --run-id "$RUN_ID"
```

Equivalent stage command, using repository-default paths, is `sipature-ml run train-indobert`. `make train-indobert` is also available. Prefer the explicit command above in Colab so artifacts persist directly to Drive.

7. Inspect `/content/drive/MyDrive/SIPATURE/runs/$RUN_ID/summary.json` and `manifest.json`. A successful task directory contains `model/`, tokenizer files, trainer state/checkpoints, `trainer-log.json`, `metrics.json`, and `training-history.png`.
8. Inspect `token-length-coverage.json`. The configured length of 192 was selected provisionally from the train/validation word-length EDA (P95 103 words and P99 210 words); the tokenizer report is the authoritative check. If coverage is inadequate, change the config and start a new run ID rather than modifying an existing run.
9. Confirm each trained task has `offline_reload_smoke.<task>.passed: true` and `local_files_only: true` in `summary.json`. This proves reload only for that produced artifact and run.
10. Copy the full run directory to controlled artifact storage if Drive is not the final location. Preserve directory names and verify every copied file against `manifest.json` hashes before deleting any source copy.

## Task Construction

- Aspect: one review becomes a 14-label binary target; loss is BCE with train-only positive class weights.
- Polarity: every annotated aspect becomes `[ASPECT] <aspect> [REVIEW] <text>` and uses weighted cross entropy over positive, negative, and neutral.
- Severity: only negative aspect labels become conditioned examples; nonnegative labels never enter this dataset. It uses weighted cross entropy over low, medium, and high.
- Best checkpoint: every task selects `eval_macro_f1` on validation, with epoch evaluation/saving and configured early stopping.

## Severity Gate

Severity training occurs only when every low/medium/high class has at least the configured train and validation support. Current defaults are 20 train and 5 validation instances per class. `summary.json` records exact support and the decision. If unsupported, the runner records `skipped_insufficient_support`; do not lower the gate merely to claim a trained severity model. Revisit label granularity or data collection explicitly.

## After A7

Do not report locked-test performance from this run. Freeze the chosen run, model configuration, and validation-derived thresholds first. Then follow A8 for one controlled locked-test evaluation, schema validation of emitted predictions, calibration, and error analysis.
