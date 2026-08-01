# IndoBERT A7 Training Runbook

## Status And Scope

Run `20260801-1024_indobert-silver-v1` completed on a Colab Tesla T4. The aspect and polarity artifacts passed offline reload, while severity was correctly skipped by its support gate. This is a train/validation candidate, not a released model: thresholds and locked-test evaluation remain reserved for A8. The training labels are AI-assisted silver references, not human gold.

The selected encoder is `indobenchmark/indobert-base-p1` at immutable revision `c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2`: MIT license, approximately 124.5M parameters, and `BertTokenizer` WordPiece tokenization. The revision is pinned in `ml/configs/training.yaml` and enforced by code.

The pinned upstream artifact has a notable metadata mismatch: `vocab.txt` exposes 30,521 tokenizer entries, while `config.json` allocates 50,000 embedding rows. Token IDs observed from the tokenizer remain within the model embedding capacity. The model supports 512 positions; SIPATURE uses 192 tokens, covering 97.18% of train and 97.96% of validation records without truncation.

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

Colab may provide a `torchvision` build incompatible with the pinned PyTorch version, producing `operator torchvision::nms does not exist` while importing BERT. SIPATURE is text-only and does not use `torchvision`; remove it and restart the session if present:

```bash
!python -m pip uninstall -y torchvision
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

## Completed Run

- Run ID: `20260801-1024_indobert-silver-v1`.
- Git commit: `24f140cac79a7a7fb9e2910fe22987d78d0c5f34` with a clean worktree.
- Environment: Google Colab, Tesla T4, Python 3.12.13, PyTorch 2.7.1, Transformers 4.53.2.
- Aspect validation Macro F1: 0.4012 at the temporary 0.50 threshold.
- Polarity validation Macro F1: 0.7044.
- Severity: skipped; high support was 19 train and 6 validation against minima of 20 and 5.
- Offline reload: passed for aspect (1 x 14 logits) and polarity (1 x 3 logits), with `local_files_only=true`.
- Locked test: not read.
- Evidence: `docs/evidence/indobert/20260801-1024_indobert-silver-v1/`.
