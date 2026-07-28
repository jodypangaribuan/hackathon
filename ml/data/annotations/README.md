# Annotation Data

Restricted AI-assisted silver annotation workspace. Optional human/gold artifacts use separate versions and are not part of the active A5 run.

Active outputs:

```text
silver-v1.0.0.jsonl
silver-v1.0.0.manifest.json
silver-disagreement-queue.jsonl
silver-pass-strict.jsonl
silver-pass-balanced.jsonl
silver-pass-recall.jsonl
```

Do not store reviewer names or personal identifiers. These outputs are weak-supervision silver labels, not human annotations or gold labels. Vote agreement is not calibrated probability or inter-annotator agreement.
