# SIPATURE

AI early-warning and intervention system for sustainable tourism quality around Lake Toba.

The app transforms organizer-provided tourism reviews and destination metadata into explainable
issue signals, destination evidence, and prioritized field-verification targets. Review-derived
signals are reports requiring human verification, not scientific measurements or public verdicts.

## Run

```bash
npm install
npm run dev
```

Open `http://localhost:3100`.

## Routes

| Route | Feature |
| --- | --- |
| `/` | Regional overview, intelligence map, filters, top priorities |
| `/destinasi/[id]` | Destination score, issue evidence, infrastructure gaps, local simulator |
| `/intervensi` | Regional intervention and field-verification queue |
| `/simulator` | Destination-selectable intervention scenario simulator |
| `/analyzer` | Live review aspect/sentiment analyzer |
| `/metode` | Scoring method, data audit, limitations, responsible AI |
| `/umkm` | Supporting local-service opportunities derived from evidence |

## Commands

```bash
npm run typecheck
npm run build
python3 scripts/gen_seed.py src/data
```

## Current model status

The UI uses a transparent keyword + rating baseline generated from the organizer dataset. It is a
stand-in for the planned evaluated IndoBERT aspect, polarity, and severity model. Actual model
metrics must be reported honestly before replacing the baseline.
