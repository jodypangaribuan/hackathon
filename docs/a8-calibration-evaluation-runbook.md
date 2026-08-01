# A8 Calibration and Locked Evaluation Runbook

**Status:** implementation ready; execution pending.

A8 has two strictly ordered phases. The locked test must not be uploaded, copied, mounted into the runtime split directory, inspected, or read until the validation calibration artifact exists, has been inspected, and is frozen. Labels remain AI-assisted silver references unless a separately versioned gold split is supplied.

## Colab Setup

1. Start a Colab GPU runtime and mount Drive.
2. Clone or update the repository at `/content/hackathon`.
3. Keep the full A7 run in Drive. It must include `manifest.json`, `aspect/model/model.safetensors`, `polarity/model/model.safetensors`, tokenizers, and model configs.
4. Run `python -m pip uninstall -y torchvision` before installing `ml/requirements-colab.lock.txt`. This avoids incompatible optional torchvision registrations in some Colab images.
5. Install the package with `python -m pip install --no-deps -e /content/hackathon/ml`.

## Phase 1: Calibration

1. Create a temporary split directory containing only `split_manifest_silver_v1.json` and its hash-locked validation file. Do not place the test file there.
2. Set a new immutable calibration output directory in Drive.
3. Run notebook `ml/notebooks/08_calibration_and_evaluation.ipynb` through the calibration cell, or run:

```bash
sipature-ml calibrate-indobert \
  --split-dir /content/a8-splits \
  --model-run-dir /content/drive/MyDrive/SIPATURE/runs/A7_RUN_ID \
  --output-dir /content/drive/MyDrive/SIPATURE/calibration/A8_CALIBRATION_ID
```

4. Inspect `calibration.json`, `manifest.json`, validation calibration metrics, thresholds, model hashes, and the plot.
5. Record the calibration and manifest SHA-256 values. Freeze the directory and do not modify it.
6. Pause for explicit human confirmation. Thresholds, temperature, model, and configuration are now fixed.

The calibration runner reads only the validation manifest entry. It verifies the validation hash, A7 manifest, and final aspect/polarity model hashes. The historical A7 full training YAML hash is recorded but is not compared to the current full YAML because A8 adds a new section. The current canonical `indobert` section and A8 calibration section are frozen separately.

## Phase 2: Locked Test

1. Only after Phase 1 is inspected and frozen, copy the locked test file into the split directory.
2. Choose a new evaluation output directory. Never reuse one from a prior attempt.
3. Run the notebook's separate evaluation cell once, or run:

```bash
sipature-ml evaluate-indobert \
  --split-dir /content/a8-splits \
  --model-run-dir /content/drive/MyDrive/SIPATURE/runs/A7_RUN_ID \
  --calibration /content/drive/MyDrive/SIPATURE/calibration/A8_CALIBRATION_ID \
  --output-dir /content/drive/MyDrive/SIPATURE/evaluation/A8_EVALUATION_ID \
  --baseline-metrics-dir /content/hackathon/ml/artifacts/metrics \
  --baseline-figure-dir /content/hackathon/docs/figures/eda
```

The runner verifies the locked manifest, test hash, calibration hash, frozen configuration hashes, A7 manifest hash, and final model hashes before inference. It performs exactly one test inference call. Polarity is evaluated on reference-annotated aspects, not predicted aspects, so aspect detection errors do not contaminate the polarity task score.

## Outputs and Interpretation

The immutable output contains aspect Macro/Micro/per-label F1, Precision@Alert, ECE, multilabel Brier, latency, polarity Macro F1/confusion matrix, optional baseline inputs, plots, all aspect FP/FN cases, and deterministic FP/FN audit queues capped at 50 each.

Severity is reported as `unavailable_no_model` because A7's class-support gate did not produce a severity model. Do not infer or claim severity performance.

Error records contain empty manual fields for negation, linguistic category, reputational risk, and notes. A8 does not automatically classify linguistic error causes. Reviewers must fill those fields manually and preserve the original aggregate files.
