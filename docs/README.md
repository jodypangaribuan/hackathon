# SIPATURE Documentation

Authoritative documentation index for the data, model, product, evaluation, and deployment lifecycle.

| Document | Purpose | Owner | Status |
| --- | --- | --- | --- |
| `data-dictionary.md` | Field definitions, types, examples, missing-value semantics | Data/ML | Draft |
| `known-data-issues.md` | Known defects, impact, handling, residual risk | Data/ML | Draft |
| `annotation-guideline.md` | Taxonomy and human-labeling rules | Data/ML + Research | Draft |
| `model-card.md` | Intended use, metrics, limitations, license, risks | Data/ML | Draft |
| `responsible-ai.md` | Privacy, bias, human oversight, misuse safeguards | Research | Draft |
| `app-integration-contract.md` | ML-to-Next.js export and versioning contract | ML + Engineering | Draft |
| `deployment-runbook.md` | Offline Docker/DGX deployment and rollback | Engineering | Draft |
| `experiment-log.md` | Append-only experiment and decision history | Data/ML | Active |
| `restricted-data-policy.md` | Git, secret, dataset, and artifact handling policy | Engineering + Data | Active |
| `reproducibility-runbook.md` | Environment, Drive, commands, checkpoints, and locked-test runbook | Data/ML | Active |

Related planning documents at workspace root:

- `SIPATURE-Project-Charter.md`
- `SIPATURE-Implementation-Plan.md`
- `SIPATURE-Hackathon-TODO.md`
- `SIPATURE-Laporan-Analisis-Template.md`

Documentation rules:

- Mark assumptions, targets, and measured results explicitly.
- Link claims to an artifact, source row, metric file, or experiment ID.
- Never edit historical experiment results; append a new version.
- Do not include reviewer identities, institution identity, secrets, or restricted raw data.
