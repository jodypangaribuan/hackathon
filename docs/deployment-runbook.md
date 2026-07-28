# SIPATURE Deployment Runbook

**Target:** Local Docker and DGX B200  
**Status:** Draft

## Preconditions

- Confirm OS, CUDA, driver, container runtime, network, storage, and allowed ports.
- Model/tokenizer and generated data are locally available.
- No container downloads model artifacts during startup.
- Secrets are provided through environment/runtime facilities.

## Services

```text
sipature-web -> Next.js
sipature-api -> FastAPI + inference
sipature-db  -> PostgreSQL/PostGIS or SQLite fallback
```

## Deployment

```text
[BUILD COMMAND]
[START COMMAND]
[DATABASE SEED COMMAND]
[HEALTH CHECK COMMAND]
[INFERENCE FIXTURE COMMAND]
[ROUTE SMOKE TEST COMMAND]
```

## Verification

- GPU detected.
- Health/readiness checks pass.
- Inference fixture matches expected schema.
- App routes and evidence links load.
- Offline map/data fallback works.
- p50/p95 latency and memory are recorded.

## Rollback

`[PREVIOUS IMAGE/ARTIFACT VERSION, ROLLBACK COMMANDS, DATA COMPATIBILITY CHECK.]`
