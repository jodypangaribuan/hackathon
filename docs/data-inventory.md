# SIPATURE Data Inventory

**Snapshot:** 28 Juli 2026  
**Encoding yang berhasil:** `utf-8-sig`  
**Delimiter:** comma-separated CSV dengan quoting standar  
**Machine-readable inventory:** `ml/artifacts/reports/data_inventory.json`

Inventory saat ini terdiri dari 14 CSV. Seluruh CSV dapat dibaca tanpa decode/CSV error. Row count berikut adalah record di luar header fisik; semantic row count dapat berbeda pada file dengan embedded/multirow header.

| File ringkas | Rows | Cols | Fungsi | Masalah struktur utama |
| --- | ---: | ---: | --- | --- |
| Artikel Danau Toba | 6 | 5 | Konteks artikel | Bukan ground truth model |
| Attractions Info | 15 | 8 | Deskripsi/lokasi/jam/tiket/budaya | 1 second-level header; 14 data records |
| Info Seputar TOP 3 | 29 | 68 | Wide regional ecosystem data | Blank first row, 3 header rows, 25 data records |
| hotel-metadata | 36 | 12 | Hotel coordinates/facilities/price/rating | Blank IDs; category/time contamination |
| hotel-resto-v1 | 9 | 8 | Mixed supporting places | Heterogeneous field semantics |
| kuliner | 12 | 3 | Culinary descriptions | Blank IDs |
| prompt | 7 | 3 | Prompt examples | 2 blank rows + embedded header; 5 prompts |
| resto-hotel-v2 | 9.611 | 8 | Hotel/resto reviews | Missing text/date/type; decimal ratings |
| resto-metadata | 148 | 11 | Restaurant coordinates/rating/price | Facilities 4%; hours 1%; duplicate names |
| tempat-wisata-v1 | 96 | 9 | Attraction facilities/review/status | Unnamed displaced status; one exact duplicate |
| transportasi | 16 | 7 | Routes/fares/schedules | Blank IDs; mixed fare/schedule semantics |
| waktu operasional | 40 | 8 | Facilities/hours enrichment | Section rows; rating field mostly notes |
| wisata-metadata | 139 | 12 | Attraction coordinates/rating/status | Three all-blank columns; duplicate/coordinate issues |
| wisata-v2 | 12.691 | 7 | Attraction reviews | 6.322 blank text; relative dates; duplicates |

## Review Field Mapping

| Canonical field | `wisata-v2` | `resto-hotel-v2` | Handling |
| --- | --- | --- | --- |
| Place | `place-name` | `place-name` | Preserve raw + normalize later |
| Reviewer identity | `name`; blank `reviewer-id` | `name`; blank `reviewer-id` | Restricted; never public output |
| Rating | `reviewer-rating` | `reviewer-rating` | Parse full rating pattern only; preserve raw |
| Text | `review-text` | `review-text` | Whitespace-aware text/rating-only classification |
| Published time | `published-at` | `published-at` | Relative multilingual text; approximate parsing |
| Scrape date | `scraped-at-date` | `scraped-at-date` | Anchor for relative date where available |
| Trip context | N/A | `reviewer-type` | Sparse; preserve original before splitting |

## Metadata Field Mapping

| Canonical | Wisata metadata | Resto metadata | Hotel metadata |
| --- | --- | --- | --- |
| Name | `place-name` | `place-name` | `place-name` |
| Type | `place-type` | `place-type` | `place-type` |
| Coordinate | `lat-long` | `lat-long` | `lat-long` |
| Rating | `place-rating` | `place-rating` | `place-rating` |
| Facilities | Not present | `Fasilitas` | `Fasilitas` |
| Status | `status` | `status` | `status` |
| Hours | `operational-hour` | `opening-hours` | Check-in/out only, not comparable hours |
| Price/fee | `entry-fee` | `price-per-head` | `price-per-head` |
| Address | `address` | `address` | `address` |

## Source Hashes

Full SHA-256 for all 14 files is stored in `ml/artifacts/reports/eda_summary.json` and `data_inventory.json`. Hashes are used to identify the exact snapshot; they are not repeated manually here to avoid transcription errors.

## Restricted Fields

Reviewer display names, phone numbers/contact data embedded in free text, and trip context are treated as restricted. Public evidence must remove identity/contact patterns while preserving internal source provenance.

## Loader Classes Required

```text
standard_csv
review_csv
multirow_header_csv
leading_blank_embedded_header_csv
section_forward_fill_csv
```

One generic `read_csv(header=0)` pipeline is not semantically correct for all sources.
