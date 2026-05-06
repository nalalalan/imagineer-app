# Imagineer Position System

Adaptive AO Labs system for moving Alan toward WDI R&D mechanical Imagineering roles, with Principal R&D Imagineer as the north-star profile.

## What It Does

- Serves the public dashboard for `imagineer.aolabs.io`.
- Serves a reviewer-ready proof packet at `proof-packet.html`.
- Tracks target-role fit, evidence, experiments, journal entries, and guardrails.
- Exposes monitoring endpoints:
  - `GET /health`
  - `GET /api/imagineer/ops-check`
  - `GET /api/imagineer/research-journal`
  - `GET /api/imagineer/paper-outline`
  - `GET /api/imagineer/weekly-paper`
  - `POST /api/imagineer/events`
  - `POST /api/imagineer/daily-cycle`
  - `POST /api/imagineer/weekly-paper/run`
- Ships a paper PDF at `imagineer-autonomous-position-system.pdf`, with source in `manuscripts/imagineer_nature_style/main.tex`.
- Uses `OPENAI_API_KEY` when present for the daily planner; otherwise falls back to deterministic weakest-signal planning.

## Local Run

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Runtime state defaults to `.runtime/imagineer_state.json`. Set `IMAGINEER_STATE_PATH` for persistent storage on a deployed host.
