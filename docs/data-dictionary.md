# Data Dictionary

**Dataset version:** `[VERSION]`  
**Generated from:** `[SOURCE MANIFEST]`  
**Last updated:** `[DATE]`

> Complete this document from the data-inventory pipeline. Do not infer field meaning without source evidence.

## Source Files

| Source ID | Filename | Snapshot date | SHA-256 | Encoding | Purpose |
| --- | --- | --- | --- | --- | --- |
| `[ID]` | `[FILE]` | `[DATE]` | `[HASH]` | `[ENCODING]` | `[PURPOSE]` |

## Canonical Review Schema

| Field | Type | Nullable | Definition | Example | Missing semantics | Source |
| --- | --- | --- | --- | --- | --- | --- |
| `review_id` | string | No | Stable ID within dataset version | `review_0001` | N/A | Generated |
| `destination_id` | string | No | Canonical destination reference | `dest_001` | N/A | Entity resolution |
| `raw_review_text` | string | Yes | Unmodified source text | `[TEXT]` | Rating-only record | Review CSV |
| `normalized_review_text` | string | Yes | Deterministically normalized text | `[TEXT]` | Rating-only record | Pipeline |
| `rating` | float | Yes | Normalized rating 0–5 | `4.5` | Source missing/invalid | Review CSV |
| `published_at` | datetime | Yes | Normalized publication date | `[DATE]` | Unknown/unparseable | Review CSV |
| `source_file` | string | No | Origin file | `[FILE]` | N/A | Pipeline |
| `source_row_id` | string | No | Source row identity | `[ROW]` | N/A | Pipeline |
| `duplicate_group_id` | string | Yes | Near/repeated duplicate group | `[ID]` | Unique/not grouped | Pipeline |

## Canonical Destination Schema

| Field | Type | Nullable | Definition | Example | Missing semantics | Source |
| --- | --- | --- | --- | --- | --- | --- |
| `destination_id` | string | No | Stable canonical ID | `dest_001` | N/A | Pipeline |
| `canonical_name` | string | No | Preferred display name | `[NAME]` | N/A | Metadata |
| `aliases` | array | Yes | Source name variants | `[LIST]` | No known aliases | Entity resolution |
| `latitude` | float | Yes | WGS84 latitude | `2.35` | Not geolocated | Metadata |
| `longitude` | float | Yes | WGS84 longitude | `99.07` | Not geolocated | Metadata |
| `category` | string | Yes | Canonical place type | `wisata` | Unknown | Metadata |
| `data_confidence` | enum | No | Data sufficiency state | `medium` | N/A | Aggregation |

## Prediction and Signal Schema

`[ADD REVIEW PREDICTION, DESTINATION-ASPECT SIGNAL, HEALTH, PRIORITY, AND EVIDENCE FIELDS AFTER IMPLEMENTATION.]`

## Controlled Vocabularies

Reference `ml/configs/taxonomy.yaml`, `split.yaml`, and `scoring.yaml`. Record version changes here.
