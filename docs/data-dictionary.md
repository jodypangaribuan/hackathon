# Data Dictionary

**Dataset version:** `eda-v0.1.0`
**Generated from:** `ml/artifacts/reports/eda_summary.json`
**Last updated:** 1 Agustus 2026

Field definitions below cover canonical cleaning/entity outputs and the A9 production contract. Raw source values remain preserved in restricted storage.

## Source Files

| Source ID | Filename | Snapshot date | SHA-256 | Encoding | Purpose |
| --- | --- | --- | --- | --- | --- |
| REV-WISATA | `wisata-v2.csv` | Snapshot source | See manifest | UTF-8 BOM | Attraction reviews |
| REV-SERVICE | `resto-hotel-v2.csv` | Snapshot source | See manifest | UTF-8 BOM | Hotel/restaurant reviews |
| META-WISATA | `wisata-metadata.csv` | Snapshot source | See manifest | UTF-8 BOM | Attraction metadata |
| META-RESTO | `resto-metadata.csv` | Snapshot source | See manifest | UTF-8 BOM | Restaurant metadata |
| META-HOTEL | `hotel-metadata.csv` | Snapshot source | See manifest | UTF-8 BOM | Hotel metadata |

## Canonical Review Schema

| Field | Type | Nullable | Definition | Example | Missing semantics | Source |
| --- | --- | --- | --- | --- | --- | --- |
| `review_id` | string | No | Stable ID within dataset version | `review_0001` | N/A | Generated |
| `destination_id` | string | No | Canonical destination reference | `dest_001` | N/A | Entity resolution |
| `raw_review_text` | string | Yes | Unmodified source text | `[TEXT]` | Rating-only record | Review CSV |
| `normalized_review_text` | string | Yes | Deterministically normalized text | `[TEXT]` | Rating-only record | Pipeline |
| `rating` | float | Yes | Normalized rating 0–5 | `4.5` | Source missing/invalid | Review CSV |
| `published_at_raw` | string | Yes | Original relative publication text | `2 tahun lalu` | Source missing | Review CSV |
| `published_at_estimate` | date | Yes | Conservative estimate anchored to scrape date | `2023-07` | Missing/unparseable | Pipeline |
| `published_at_precision` | enum | Yes | Precision/uncertainty of estimate | `month` | Unavailable | Pipeline |
| `scraped_at` | date | Yes | Source scrape snapshot date | `2025-07-29` | Source missing | Review CSV |
| `source_file` | string | No | Origin file | `[FILE]` | N/A | Pipeline |
| `source_row_id` | string | No | Source row identity | `[ROW]` | N/A | Pipeline |
| `duplicate_group_id` | string | Yes | Near/repeated duplicate group | `[ID]` | Unique/not grouped | Pipeline |
| `review_kind` | enum | No | `text_and_rating`, `text_only`, `rating_only`, `empty_record` | `text_and_rating` | N/A | Pipeline |
| `reviewer_name_raw_restricted` | string | Yes | Original display name, restricted access | `[REDACTED]` | Source missing | Review CSV |

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
| `coordinate_raw` | string | Yes | Original coordinate pair | `2.35, 99.07` | Source missing | Metadata |
| `coordinate_parse_status` | enum | No | Parse/region validation result | `valid` | N/A | Pipeline |
| `status_raw` | string | Yes | Source operating status | `beroperasi` | Unknown | Metadata |
| `facilities_raw` | string | Yes | Source facility text | `Toilet, parkir` | Unknown, not absent | Metadata/supporting data |

## Prediction and Signal Schema

| Entity/field | Type | Missing semantics | Definition |
| --- | --- | --- | --- |
| Review prediction `predictions` | array | Empty means no aspect crossed its threshold | TF-IDF aspect probability, lexical polarity, explicit severity-unavailable status |
| Signal `mention_count` | integer | Zero/absent signal is not evidence of good condition | Number of detected aspect mentions |
| Signal `negative_count` | integer | N/A | Lexical-negative mentions among detected aspects |
| Signal `severe_count` | null | No supported severity model | Never coerced to zero |
| Signal `smoothed_complaint_rate` | float 0–1 | Insufficient support remains labeled | Bayesian-smoothed weighted negative rate |
| Signal `data_confidence` | enum | `insufficient` is not healthy | `high`, `medium`, `low`, or `insufficient` |
| Priority `priority_score` | float 0–1/null | Null when insufficient | Renormalized sum of available transparent components |
| Priority `priority_components` | object | Missing components omitted and documented | Values, original/effective weights, and contributions |
| Evidence `text` | string | Empty evidence blocks actionable priority | Anonymous verbatim span; full provenance remains restricted |
| Destination `health_score` | float 0–100/null | Null when insufficient | Inverse mean smoothed complaint rate over usable issues |

## Controlled Vocabularies

Reference `ml/configs/taxonomy.yaml`, `split.yaml`, and `scoring.yaml`. Record version changes here.
