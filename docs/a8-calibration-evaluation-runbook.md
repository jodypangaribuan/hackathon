# A8 Calibration and Locked Evaluation Runbook

**Status:** implementation ready; execution pending.

A8 has two strictly ordered phases. The locked test must not be uploaded, copied, mounted into the runtime split directory, inspected, or read until the validation calibration artifact exists, has been inspected, and is frozen. Labels remain AI-assisted silver references unless a separately versioned gold split is supplied.

## Colab Setup

1. Start a Colab GPU runtime and mount Drive.
2. Clone or update the repository at `/content/hackathon`.
3. Keep the full A7 run in Drive. Each aspect/polarity model must include the manifest-hashed local reload set: `config.json`, `model.safetensors`, `tokenizer_config.json`, `special_tokens_map.json`, and `vocab.txt`.
4. Run `python -m pip uninstall -y torchvision` before installing `ml/requirements-colab.lock.txt`. This avoids incompatible optional torchvision registrations in some Colab images.
5. Install the package with `python -m pip install --no-deps -e /content/hackathon/ml`.

## Phase 1: Calibration

1. Copy only `split_manifest_silver_v1.json` and its hash-locked validation file from controlled Drive paths into a temporary split directory. Do not place the test file there.
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

The calibration runner reads only the validation manifest entry. It verifies the validation hash, A7 manifest, and every manifest-declared final local reload file for both models. The historical A7 full training YAML hash is recorded but is not compared to the current full YAML because A8 adds a new section. The current canonical `indobert` section and A8 calibration section are frozen separately. A8 requires CUDA by default and reports aspect inference, polarity inference, and excluded model-loading latency separately.

## Phase 2: Locked Test

1. Only after Phase 1 is inspected and frozen and the exact notebook confirmation phrase is entered, copy the locked test file from its controlled Drive path into the split directory. Do not use browser upload or inspect its contents.
2. Choose one evaluation ID and output directory. This ID is the sole authorized attempt and must never be changed to evade a failed attempt.
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

Before resolving the test entry, the runner verifies the exact frozen split-manifest hash, manifest validation hash, sorted taxonomy labels, phase/test-read fields, calibration/config/A7/model hashes, every calibration artifact hash, baseline compatibility, and plotting dependencies. It then creates `evaluation-state.json` with status `started_before_test_access` before reading the test. The test is read exactly once for combined hashing and parsing, and the inference function is called exactly once. Polarity is evaluated on reference-annotated aspects, not predicted aspects, so aspect detection errors do not contaminate the polarity task score.

If hashing, parsing, inference, plotting, or artifact writing fails after the state marker is created, do not rerun with the same or a fresh output ID. Preserve the incomplete directory and document a methodological incident, including the state marker and traceback. A rerun requires an explicit governance decision; silently choosing a new directory would violate the one-shot policy.

## Outputs and Interpretation

The completed output contains aspect Macro/Micro/per-label F1, per-label and overall micro Precision@Alert with validation `target_met` status, positive-class ECE, multilabel Brier, separate aspect/polarity latency, polarity Macro F1/confusion matrix, compact compatible baseline metrics, a reliability diagram, all aspect FP/FN cases, and deterministic FP/FN audit queues capped at 50 each.

Inspect that `evaluation-state.json` says `completed`, `test_inference_passes` equals `1`, the state and manifest test hashes agree, and every file except `manifest.json` appears in `manifest.json`'s `artifact_hashes`. Preserve incomplete state markers as incident evidence.

Severity is reported as `unavailable_no_model` because A7's class-support gate did not produce a severity model. Do not infer or claim severity performance.

Error records contain empty manual fields for negation, linguistic category, reputational risk, and notes. A8 does not automatically classify linguistic error causes. Reviewers must fill those fields manually and preserve the original aggregate files.
