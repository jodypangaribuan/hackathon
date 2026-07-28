# SIPATURE Leakage-Safe Split and Baseline Report

**Split version:** `silver-split-1.0.0`  
**Experiment version:** `silver-baselines-1.0.0`  
**Reference:** AI-assisted weak-supervision silver labels  
**Status:** A6 completed; not human-gold evaluation

## Scope

A6 evaluates multilabel aspect detection on frozen `silver-1.0.0`. Every result in this report measures **agreement with silver labels**, not generalization against independent human ground truth. Keyword and silver rules share taxonomy vocabulary, so keyword scores are structurally circular and must not be interpreted as real-world accuracy.

## Leakage-Safe Split

All 1.320 records were joined one-to-one with canonical review metadata. The join verifies `review_id`, `destination_id`, and review text before adding technical duplicate and normalized repeated-text group IDs.

| Split | Records | Destinations | Empty-label records |
| --- | ---: | ---: | ---: |
| Train | 922 | 187 | 348 |
| Validation | 196 | 40 | 73 |
| Locked test | 202 | 40 | 76 |

Destination ratios are exactly 70,04% / 14,98% / 14,98%. Record ratios differ slightly because destinations vary in review count. All 14 aspects occur in validation and test; test support ranges from 2 for `opening_hours` to 43 for `scenery`.

Leakage controls:

- Destination overlap across splits: 0.
- Technical duplicate-group overlap across splits: 0.
- Normalized exact repeated-text overlap across splits: 0.
- Review ID overlap across splits: 0.
- Direct technical duplicate groups spanning destinations: 0.
- Cross-destination normalized repeated-text groups grouped together: 23.
- Multi-destination connected components after repeated-text grouping: 10.

`duplicate_group_id` is a technical exact fingerprint and does not detect semantic paraphrases. Normalized repeated-text grouping catches identical text across destinations but still does not prove semantic near-duplicate coverage.

## Baselines

The keyword baseline uses a transparent aspect lexicon, local polarity cues, contrast clauses, intensity terms, and severity rules. It is implemented independently from the silver generator but uses the same taxonomy vocabulary.

The TF-IDF baseline compares three prespecified representations on validation only:

| Representation | Validation Macro F1 vs silver |
| --- | ---: |
| Word unigram/bigram | 0,7780 |
| Character 3–5 gram | 0,7314 |
| Word + character | 0,8117 |

The selected model is combined word+character TF-IDF with One-vs-Rest Logistic Regression, `class_weight="balanced"`, `C=1.0`, and `max_iter=2000`. Per-aspect thresholds were selected only on validation from the configured candidate set. The test artifact was read only after representation and thresholds were fixed.

![TF-IDF validation selection](figures/eda/36_tfidf_validation_selection.png)

**Gambar 1. Pemilihan TF-IDF representation pada validation split.** Combined word+character features menghasilkan Macro F1 silver-agreement tertinggi.

## Locked Silver-Test Results

| Metric | Keyword | TF-IDF word+char |
| --- | ---: | ---: |
| Macro F1 | 0,9768 | 0,7201 |
| Micro F1 | 0,9783 | 0,8040 |
| Exact Match | 0,9455 | 0,7079 |
| Hamming Loss | 0,0039 | 0,0343 |
| Latency ms/review | 1,8953 | 0,1101 |

![Baseline comparison](figures/eda/34_baseline_silver_test_comparison.png)

**Gambar 2. Perbandingan baseline pada locked silver test.** Nilai adalah agreement terhadap weak-supervision reference.

Keyword Macro F1 yang sangat tinggi terutama menunjukkan kedekatan dengan fungsi pembentuk silver labels. Nilai tersebut bukan bukti bahwa keyword baseline memahami review atau mendeteksi kondisi aktual. TF-IDF lebih independen dari runtime rules, tetapi masih belajar dari silver targets yang dihasilkan secara leksikal.

![Per-aspect F1](figures/eda/35_baseline_per_aspect_f1.png)

**Gambar 3. Per-aspect F1 pada locked silver test.** TF-IDF paling lemah pada `opening_hours` (F1 0 dengan support 2), `crowding` (0,5000), dan `public_facilities` (0,6061). Support kecil membuat rare-label metrics tidak stabil.

TF-IDF memperoleh Macro F1 0,7474 pada 79 `consensus` test records dan 0,6551 pada 47 `review_recommended` records. Dari 97 aspect-level disagreement TF-IDF, 57 berada pada `review_recommended`, 36 pada `consensus`, dan 4 pada `no_supported_aspect`. Status-stratified Macro F1 untuk all-zero `no_supported_aspect` records bernilai nol secara definisi dan sebaiknya dibaca bersama Exact Match/Hamming Loss, bukan sebagai quality score mandiri.

## Artifacts

```text
ml/data/splits/train_silver_v1.jsonl
ml/data/splits/validation_silver_v1.jsonl
ml/data/splits/test_silver_v1.jsonl
ml/data/splits/split_manifest_silver_v1.json
ml/artifacts/models/keyword-silver-v1/
ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib
ml/artifacts/metrics/keyword-silver-v1-test-metrics.json
ml/artifacts/metrics/tfidf-silver-v1-test-metrics.json
ml/artifacts/reports/baseline_silver_test_errors.csv
```

Split/model/metric/error artifacts are restricted and Git-ignored. The split manifest records source/config/taxonomy hashes, destination lists, distributions, output hashes, and zero-leakage checks. TF-IDF serialization was reloaded successfully and produced a `(5, 14)` probability matrix.

## Reproduction and Locking

```bash
cd ml
make split-silver
make baselines
```

The split command refuses to overwrite an existing locked manifest. The baseline command refuses to run without a locked manifest, verifies each split hash, and fails if locked-test metric filenames already exist. A new split/experiment version is required for any rerun that changes data, model, thresholds, or test evaluation.

## Limitations

- Silver labels are not human gold and contain correlated lexical bias.
- Keyword-vs-silver evaluation is circular despite independent baseline code.
- `no_supported_aspect` means no rule-supported label, not proven absence of aspects.
- Pilot/main records informed weak-rule development, so this is a retrospective silver benchmark rather than an untouched evaluation of the labelling function.
- Rare aspects have unstable test estimates, especially `opening_hours` with support 2.
- Exact repeated-text grouping does not capture semantic paraphrases.
- Polarity and severity are emitted by the keyword rules but are not evaluated as independent A6 model tasks.
