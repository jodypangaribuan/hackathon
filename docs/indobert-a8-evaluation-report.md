# SIPATURE IndoBERT A8 Calibration and Evaluation Report

## Scope and One-Shot Control

Run `20260801_indobert-silver-v1_locked-test-v1` calibrated the A7 candidate on the 196-record validation split, froze model/configuration/temperature/threshold hashes, and then evaluated the 202-record locked test exactly once. `evaluation-state.json` records `completed` and `test_inference_passes=1`. Results measure agreement with AI-assisted weak-supervision silver labels, not human-gold performance.

The frozen test SHA-256 is `edf650024fc2f74c5f3eea1bc04c3b909c52884849067987196fd8b795bb43ff`. The evaluation manifest SHA-256 is `d58fd1c17af3c0e0c5de2b118fc70072b5a8190b2bf999082f35d3003975fc88`. The controlled execution audit recorded that all 11 evaluation artifacts matched their manifest hashes; the safe Git evidence deliberately excludes review-level artifacts, so those restricted hashes are not independently reverified from the repository alone.

## Validation Calibration

Temperature scaling selected `temperature=0.6` using validation only. Per-aspect detection and alert thresholds were also selected using validation only.

| Validation metric | Before/fixed threshold | After calibration/tuning |
| --- | ---: | ---: |
| Aspect Macro F1 | 0.4012 at threshold 0.50 | 0.5535 with per-aspect thresholds |
| Aspect Micro F1 | 0.4326 at threshold 0.50 | 0.5696 with per-aspect thresholds |
| Binary NLL | 0.4533 | 0.4236 |
| Positive-class ECE | 0.2706 | 0.2253 |
| Multilabel Brier | 0.1441 | 0.1388 |

The probability metrics all improved on validation. Alert precision reached the 0.80 validation target with at least five predictions for `cleanliness`, `parking`, `scenery`, `staff_service`, and `waste`. Other alert thresholds remain candidates whose validation target was not met and must not be presented as high-precision alerts.

## Locked Silver-Test Results

| Model/task | Macro F1 | Micro F1 |
| --- | ---: | ---: |
| Keyword aspect baseline | 0.9768 | 0.9783 |
| TF-IDF aspect baseline | 0.7201 | 0.8040 |
| IndoBERT aspect | 0.5247 | 0.5241 |
| IndoBERT aspect-conditioned polarity | 0.7459 | Not applicable |

IndoBERT aspect latency was 8.4693 ms per review on a Colab Tesla T4, excluding 1.6341 seconds of model loading. Polarity inference took 2.1275 seconds for 248 reference aspect instances. Locked-test positive-class ECE was 0.2021 and multilabel Brier was 0.1258.

Overall micro Precision@Alert was 0.5886 across 175 predicted alerts. Of the five aspects that met the validation alert target, locked-test precision was 0.7143 for `cleanliness`, 1.0000 for `parking`, 0.8889 for `scenery`, 1.0000 for `staff_service`, and 1.0000 for `waste`. The drop for `cleanliness` demonstrates that a validation target is not a guarantee on new data.

## Per-Aspect Results

| Aspect | F1 | Precision | Recall | Test support |
| --- | ---: | ---: | ---: | ---: |
| access | 0.5306 | 0.4194 | 0.7222 | 18 |
| cleanliness | 0.5667 | 0.5000 | 0.6538 | 26 |
| comfort | 0.3582 | 0.2553 | 0.6000 | 20 |
| crowding | 0.5714 | 0.5000 | 0.6667 | 6 |
| maintenance | 0.5517 | 0.4211 | 0.8000 | 10 |
| opening_hours | 0.0000 | 0.0000 | 0.0000 | 2 |
| parking | 0.8333 | 1.0000 | 0.7143 | 21 |
| price_transparency | 0.5634 | 0.5128 | 0.6250 | 32 |
| public_facilities | 0.3600 | 0.2813 | 0.5000 | 18 |
| safety | 0.5000 | 0.7500 | 0.3750 | 8 |
| sanitation | 0.4643 | 0.3514 | 0.6842 | 19 |
| scenery | 0.5833 | 0.7241 | 0.4884 | 43 |
| staff_service | 0.5882 | 0.5556 | 0.6250 | 16 |
| waste | 0.8750 | 1.0000 | 0.7778 | 9 |

`opening_hours` has only two test references, so F1 zero is not a stable prevalence-wide estimate. `parking` and `waste` were strongest, but `waste` also has limited support. All per-label results must be interpreted together with support.

## Polarity and Severity

Polarity Macro F1 was 0.7459 over 248 reference-annotated aspect instances. Its fixed-order confusion matrix for positive, negative, and neutral reference rows was:

```text
[[80, 10, 22],
 [ 8, 55, 13],
 [ 5,  4, 51]]
```

Polarity was evaluated on reference-annotated aspects rather than predicted aspects, isolating polarity classification from aspect detection errors. Severity remains `unavailable_no_model` because the A7 support gate did not produce a severity model; no severity performance is claimed.

## Decision and Remaining Work

Reject the IndoBERT aspect head as the final aspect detector for this silver benchmark because it underperformed TF-IDF by 0.1953 Macro F1 and 0.2799 Micro F1 while requiring substantially more compute. Keep TF-IDF as the current learned aspect model candidate. Keep the IndoBERT polarity head as a candidate because it provides a separate contextual task capability not supplied by the current TF-IDF aspect baseline.

The review-level FP/FN artifacts and deterministic 50-case queues remain in restricted Drive storage. Manual audit of negation, implicit language, typo, sarcasm, boundary/context, annotation errors, mixed language, and reputational risk is still pending. Locked-test results must not be used to retune this model or its thresholds.

## Evidence

Safe aggregate evidence is stored at `docs/evidence/indobert/20260801_indobert-silver-v1_a8-evidence/`. The source evidence ZIP SHA-256 is `069731af3e8e52761accc5416b50e3d7055aabdef2880eeebacc471f4fbc326b`. Review-level predictions and error cases are deliberately excluded from Git.
