# Known Data Issues

**Dataset version:** `[VERSION]`  
**Last updated:** `[DATE]`

| Issue ID | Source/field | Description | Count/rate | Impact | Handling | Residual risk | Status |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| KDI-001 | Review text | Rating-only records have no text | `[N/%]` | Cannot train text model | Separate pool | Coverage bias | Open |
| KDI-002 | Rating | Decimal comma and mixed types | `[N/%]` | Parsing error | Normalize + quarantine | Invalid edge cases | Open |
| KDI-003 | Place name | No universal cross-file ID | `[N]` | Duplicate/split entities | Entity resolution | False merge | Open |
| KDI-004 | Coordinates | Missing/invalid/outlier points | `[N/%]` | Incomplete map/gap analysis | Validate + insufficient state | Coverage bias | Open |
| KDI-005 | Source manifest | Current `Datasets/` inventory has 14 CSV while the baseline corpus records `generatedFrom` 15 files | 1 discrepancy | Baseline output may use a different snapshot/input set | Compare archive, baseline script inputs, filenames, and hashes | Reproducibility mismatch until resolved | Open |
| KDI-006 | Two review files | Exact duplicate excess records | 83 | Duplicate weighting and leakage | Preserve group IDs; deduplicate technically before split | Legitimate repeated generic comments | Open |
| KDI-007 | Two review files | Empty rating and review text | 44 | No usable model/rating signal | Quarantine with provenance | Source semantics unknown | Open |
| KDI-008 | `resto-hotel-v2.csv` | Noninteger individual-review-like ratings | 8 | Mixed source semantics | Preserve raw; do not round; inspect rows | May be aggregate/shifted fields | Open |
| KDI-009 | Review time | Missing scrape dates and relative multilingual publication text | 3,243 scrape dates missing | Freshness uncertainty | Interval/precision-aware parsing | Many dates remain approximate | Open |
| KDI-010 | Metadata | Sparse facilities/hours across sources | Facilities: wisata 0%, resto 4%; hours: resto 1% | False facility-gap inference | Integrate sources; unknown != absent | External/field validation needed | Open |
| KDI-011 | Coordinates | Shared coordinate pairs across metadata records | 4 records involved | Potential duplicate/wrong entity location | Address/name audit during resolution | Some co-located entities may be legitimate | Open |
| KDI-012 | Place coverage | Exact-name textual review coverage is highly imbalanced | 100/343 names have 0–4 texts | Popularity and uncertainty bias | Sufficiency bands, smoothing, group split | Exact names may merge later | Open |
| `[ID]` | `[SOURCE]` | `[DESCRIPTION]` | `[N]` | `[IMPACT]` | `[HANDLING]` | `[RISK]` | `[STATUS]` |

Severity definitions:

- Critical: can invalidate core model/evidence claims.
- High: materially changes metrics/ranking.
- Medium: affects subset/feature reliability.
- Low: presentation or minor consistency issue.
