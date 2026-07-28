# SIPATURE Annotation Guideline

**Version:** `0.1.0-draft`  
**Taxonomy source:** `ml/configs/taxonomy.yaml`

> This is a drafting scaffold. The guideline is not approved until pilot annotation and adjudication are complete.

## Unit of Annotation

One textual review linked to one canonical destination. A review may contain multiple aspects. Polarity is assigned per aspect. Severity is assigned only to negative aspects.

## Output Example

```json
{
  "review_id": "review_0001",
  "destination_id": "dest_001",
  "text": "Pemandangan indah tetapi toiletnya kotor.",
  "labels": [
    {"aspect": "scenery", "polarity": "positive", "severity": null},
    {"aspect": "sanitation", "polarity": "negative", "severity": "high"}
  ],
  "annotator_id": "A1",
  "annotation_version": "v1.0"
}
```

## General Rules

1. Label all supported aspects, not only the dominant aspect.
2. Evaluate polarity in the clause referring to that aspect.
3. Do not infer an issue absent from the text.
4. Preserve mixed sentiment: positive scenery does not cancel negative sanitation.
5. Rating may provide context but never overrides explicit text.
6. Mark ambiguous cases for adjudication rather than guessing.
7. Do not include reviewer identity in annotation exports.

## Aspect Definitions

For every aspect complete:

### `[ASPECT]`

**Definition:** `[DEFINITION]`  
**In scope:** `[IN SCOPE]`  
**Out of scope:** `[OUT OF SCOPE]`  
**Positive example:** `[EXAMPLE]`  
**Negative example:** `[EXAMPLE]`  
**Neutral example:** `[EXAMPLE]`  
**Boundary with other labels:** `[BOUNDARY]`

## Polarity Rules

`[DEFINE POSITIVE, NEGATIVE, NEUTRAL, NEGATION, CONTRAST, SARCASM, AND IMPLICIT COMPLAINT RULES.]`

## Severity Rules

`[DEFINE LOW/MEDIUM/HIGH USING OPERATIONAL IMPACT AND TEXTUAL EVIDENCE, NOT RATING ALONE.]`

## Adjudication

Record disagreement type, annotator labels, final label, rationale, adjudicator, date, and guideline change reference.
