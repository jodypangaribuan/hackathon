# SIPATURE Responsible AI

## Intended Decision Boundary

SIPATURE recommends where evidence suggests a human should inspect first. It does not confirm real-world conditions and does not make autonomous operational decisions.

## Safeguards

- Remove reviewer names, profile identifiers, and links from product outputs.
- Use verbatim evidence only; never generate supporting quotes.
- Display confidence, support, freshness, and missing-data state.
- Hide or downgrade alerts below evidence/confidence thresholds.
- Distinguish no detected issue from insufficient data.
- Use Bayesian smoothing to reduce popularity/sample-size bias.
- Let managers verify, reject, and record reasons.
- Label simulation as scenario analysis, not causal prediction.

## Risk Register

| Risk | Harm | Mitigation | Monitoring metric | Owner |
| --- | --- | --- | --- | --- |
| False high-severity alert | Reputational harm | High-precision threshold + evidence | Alert precision | ML |
| Popularity bias | Smaller places ignored/overrated | Smoothing + sufficiency state | Coverage by volume band | ML |
| Stale review | Outdated action | Freshness display/weight | Alert age | Product |
| False entity merge | Wrong evidence assigned | Conservative matching | False-merge rate | Data |
| `[RISK]` | `[HARM]` | `[MITIGATION]` | `[METRIC]` | `[OWNER]` |

## Human Oversight Workflow

```text
New -> Verification Planned -> Verified
-> Intervention Planned -> Resolved / Rejected
```

`[DEFINE WHO MAY CHANGE STATUS, REQUIRED EVIDENCE, AND REJECTION REASONS.]`
