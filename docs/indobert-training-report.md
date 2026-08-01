# SIPATURE IndoBERT A7 Training Report

## Scope

Run `20260801-1024_indobert-silver-v1` trained candidate aspect and polarity models on the hash-verified silver train split and selected checkpoints using validation Macro F1. It did not read the locked test split. Results measure agreement with AI-assisted silver labels, not human-gold performance.

## Model And Runtime

| Item | Value |
| --- | --- |
| Base model | `indobenchmark/indobert-base-p1` |
| Revision | `c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2` |
| License | MIT metadata on the upstream model card |
| Architecture | BERT base, 12 layers, hidden size 768, 12 attention heads |
| Approximate parameters | 124.5 million; aspect head artifact has 124,452,110 parameters |
| Tokenizer | `BertTokenizer` WordPiece |
| Tokenizer/model vocabulary | 30,521 tokenizer entries; 50,000 model embedding rows |
| Runtime | Google Colab Tesla T4 |
| Environment | Python 3.12.13, PyTorch 2.7.1, Transformers 4.53.2 |
| Git commit | `24f140cac79a7a7fb9e2910fe22987d78d0c5f34`, clean |

The upstream tokenizer/model vocabulary mismatch is safe for this run because generated token IDs remain below the model embedding capacity. It is documented as upstream artifact metadata rather than silently normalized.

## Data Controls

| Split | Records | SHA-256 |
| --- | ---: | --- |
| Train | 922 | `31c31803be592a3c91576f42abbc3fcf562d2f82c126b2856848e88639ab3fc4` |
| Validation | 196 | `7c2f5f911ea33c6854ad1adc21e41a58befb6b24b31cb5ef2b8e03b7b771477c` |

The runner verified both hashes against `split_manifest_silver_v1.json`. The summary records `test_read=false`; locked-test access remains prohibited until A8 configuration and thresholds are frozen.

## Sequence Length

`max_length=192` covers 896 of 922 train reviews (97.18%) and 192 of 196 validation reviews (97.96%) without truncation. Train P95 is 139 tokens and validation P95 is 130 tokens. The setting retains nearly all reviews while controlling T4 memory and runtime.

## Validation Results

| Task | Epoch 1 Macro F1 | Best Macro F1 | Best epoch | Validation loss | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: |
| Multilabel aspect | 0.2822 | 0.4012 | 4 | 0.7824 | 100.10 s |
| Aspect-conditioned polarity | 0.6453 | 0.7044 | 4 | 0.6962 | 126.55 s |

Aspect uses weighted BCE and a temporary fixed threshold of 0.50 for checkpoint selection. This is not the final aspect score: A8 must tune per-label thresholds using validation before one controlled locked-test evaluation. Polarity uses weighted cross-entropy over positive, negative, and neutral.

Aspect train and validation loss decreased through epoch 4 while validation Macro F1 increased. Polarity validation loss flattened after epoch 3 and rose slightly at epoch 4, while Macro F1 improved marginally from 0.7039 to 0.7044. No additional epochs are justified before A8 analysis.

## Severity Decision

Severity was not trained. The support gate required at least 20 train and 5 validation instances for every class. High severity had 19 train and 6 validation instances, so the runner recorded `skipped_insufficient_support`. Lowering the gate only to produce an artifact would weaken the methodology.

## Artifact Verification

- Aspect model: `model.safetensors`, 497,831,984 bytes.
- Polarity model: `model.safetensors`, 497,798,148 bytes.
- Full run directory remains in controlled Google Drive storage.
- The run manifest contains 65 artifact hashes; all 65 were verified after training.
- Offline reload passed with `local_files_only=true` for aspect output shape 1 x 14 and polarity output shape 1 x 3.
- Evidence ZIP SHA-256: `f34a2e74ce55b68c006eaa759e33e4c66aeff03dd3b3d9bd1b6dd5c94ccd9d99`.
- Small evidence files are preserved at `docs/evidence/indobert/20260801-1024_indobert-silver-v1/`; large weights remain outside Git.

## Limitations And Next Step

- Labels are silver and may reproduce weak-supervision errors.
- Aspect threshold 0.50 is temporary and likely suboptimal for rare labels.
- No severity model exists because support was insufficient.
- Focal loss, oversampling, learning curves, calibration, and locked-test evaluation were not run.
- A8 must tune thresholds on validation, freeze model/configuration, evaluate locked test once, and perform per-label error analysis before release claims.
