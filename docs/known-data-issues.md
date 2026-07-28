# Known Data Issues

**Dataset version:** `[VERSION]`  
**Last updated:** `[DATE]`

| Issue ID | Source/field | Description | Count/rate | Impact | Handling | Residual risk | Status |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| KDI-001 | Review text | Rating-only records have no text | `[N/%]` | Cannot train text model | Separate pool | Coverage bias | Open |
| KDI-002 | Rating | Decimal comma and mixed types | `[N/%]` | Parsing error | Normalize + quarantine | Invalid edge cases | Open |
| KDI-003 | Place name | No universal cross-file ID | `[N]` | Duplicate/split entities | Entity resolution | False merge | Open |
| KDI-004 | Coordinates | Missing/invalid/outlier points | `[N/%]` | Incomplete map/gap analysis | Validate + insufficient state | Coverage bias | Open |
| `[ID]` | `[SOURCE]` | `[DESCRIPTION]` | `[N]` | `[IMPACT]` | `[HANDLING]` | `[RISK]` | `[STATUS]` |

Severity definitions:

- Critical: can invalidate core model/evidence claims.
- High: materially changes metrics/ranking.
- Medium: affects subset/feature reliability.
- Low: presentation or minor consistency issue.
