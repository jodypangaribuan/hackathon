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
| KDI-006 | Two review files | Physical exact duplicate excess records | 83 physical; 89 after NFKC/whitespace normalization | Duplicate weighting and leakage | Stable group IDs; normalized technical duplicates excluded before split | Legitimate repeated generic comments remain separate | Mitigated v0.1 |
| KDI-007 | Two review files | Empty rating and review text | 44 | No usable model/rating signal | Quarantined/excluded with provenance | Source semantics unknown | Mitigated v0.1 |
| KDI-008 | `resto-hotel-v2.csv` | Noninteger individual-review-like ratings | 8 | Mixed source semantics | Preserve raw; do not round; inspect rows | May be aggregate/shifted fields | Open |
| KDI-009 | Review time | Missing scrape dates and relative multilingual publication text | 3,243 scrape dates missing | Freshness uncertainty | 18,923 approximate estimates with precision/status; no imputation without anchor | Many dates remain approximate | Partially mitigated v0.1 |
| KDI-010 | Metadata | Sparse facilities/hours across sources | Facilities: wisata 0%, resto 4%; hours: resto 1% | False facility-gap inference | Integrate sources; unknown != absent | External/field validation needed | Open |
| KDI-011 | Coordinates | Shared coordinate pairs across metadata records | 4 records involved | Potential duplicate/wrong entity location | Anchor clustering requires same kind/name and <=500 m; reviewed merge retained | Other shared coordinates still require field validation | Partially mitigated v0.1 |
| KDI-013 | Entity resolution | Similar numbered properties can false-merge | 1 reviewed fuzzy false merge | Evidence assigned to wrong business | Human-reviewed override; unresolved preferred | Unreviewed exact links retain residual risk | Mitigated in reviewed set |
| KDI-014 | Entity resolution | Exact place name can refer to multiple locations | `Bukit Simargulang Ombun` | Name-only review cannot be geographically assigned | Manual-review placeholder; no forced merge | Requires source/location evidence | Open/manual review |
| KDI-012 | Place coverage | Exact-name textual review coverage is highly imbalanced | 100/343 names have 0–4 texts | Popularity and uncertainty bias | Sufficiency bands, smoothing, group split | Exact names may merge later | Open |
| `[ID]` | `[SOURCE]` | `[DESCRIPTION]` | `[N]` | `[IMPACT]` | `[HANDLING]` | `[RISK]` | `[STATUS]` |

Severity definitions:

- Critical: can invalidate core model/evidence claims.
- High: materially changes metrics/ranking.
- Medium: affects subset/feature reliability.
- Low: presentation or minor consistency issue.
