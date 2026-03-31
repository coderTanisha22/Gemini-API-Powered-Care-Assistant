# Gemini API Powered Intelligent Care Assistant

Full-stack intelligent care monitoring prototype built for role-based review of activity patterns.

This repository currently includes:
- FastAPI backend with live in-memory IoT activity simulation
- Rule-based anomaly detection and alert management workflow
- Optional Gemini-generated explanations with safe fallback responses
- React + Vite frontend dashboard for caregiver, supervisor, and family views

## Project Snapshot

### What Is Working Now
- Backend service starts with a FastAPI lifespan hook and automatically starts the simulator.
- Activity events are generated continuously with scenario changes (`normal routine`, `inactivity`, `irregular behavior`).
- Anomaly engine detects:
  - prolonged inactivity
  - activity pattern deviation (drop/spike)
  - activity variability
  - missing routine event
- Alerts are generated, listed, and actioned (`approve` / `reject`).
- Supervisor demo alert can be seeded from API/UI.
- AI explanation pipeline works in both modes:
  - live Gemini mode when enabled and configured
  - deterministic fallback mode when disabled/unavailable
- Frontend dashboard consumes backend APIs for activity, status, alerts, and insight.
- Role-aware behavior is implemented (`caregiver`, `supervisor`, `family`).

### What Is Partially Implemented / Scaffolded
- `backend/app/db/*`, many files in `backend/app/models/*`, and several files in `backend/app/schemas/*` are present but mostly empty scaffolds.
- `backend/app/pipelines/pipeline.py` and `backend/app/utils/helpers.py` are placeholders.
- `docker/Dockerfile` and `docker/docker-compose.yml` are present but currently empty.
- Frontend sidebar includes links for `/alerts`, `/activity`, `/settings`, but only `/` is fully implemented.
- Frontend API base URL is hardcoded in components (`http://127.0.0.1:8000`).

## Architecture And Flow

### Runtime Flow
1. `backend/main.py` exposes app from `backend/app/main.py`.
2. On startup, FastAPI lifespan starts the simulator and logs Gemini status.
3. Simulator writes synthetic activity events into an in-memory rolling window.
4. `alert_service.py` pulls recent events and runs anomaly detection (`anamoly.py`).
5. Alerts and explanation payloads are assembled (Gemini live or fallback).
6. Frontend polls/selectively fetches backend endpoints and renders role-based views.

### Backend Core Modules
- `backend/app/main.py`: FastAPI app setup, CORS, lifespan startup/shutdown.
- `backend/app/api/router.py`: active API routes used by frontend.
- `backend/app/services/simulator.py`: event generator and simulator control.
- `backend/app/services/behaviour.py`: expected activity profiles by time of day.
- `backend/app/services/anamoly.py`: anomaly detection logic (note filename typo kept as-is in code).
- `backend/app/services/alert_service.py`: alert composition, dashboard response, action state.
- `backend/app/services/gemini_client.py`: Gemini integration, prompting, parsing, fallback handling, status.
- `backend/app/models/schemas.py`: small set of active Pydantic models.
- `backend/app/schemas/iot.py`: IoT schema model.

### Frontend Core Modules
- `frontend/src/pages/Index.tsx`: main dashboard composition and status polling.
- `frontend/src/components/dashboard/ActivityChart.tsx`: chart from `/activity` data.
- `frontend/src/components/dashboard/AlertsPanel.tsx`: alert list + approve/reject + demo seed.
- `frontend/src/components/dashboard/AIExplanation.tsx`: insight card from `/insight`.
- `frontend/src/components/dashboard/StatusSummary.tsx`: top-level state summary.
- `frontend/src/components/dashboard/ActivityTimeline.tsx`: static timeline visualization.
- `frontend/src/components/dashboard/FamilyView.tsx`: simplified family-facing view.
- `frontend/src/components/layout/*`: app shell, sidebar, navbar.
- `frontend/src/contexts/RoleContext.tsx`: role state and role switcher context.

## Repository Layout (Detailed)

```text
backend/
  main.py                      # entrypoint importing app.main:app
  app/
    main.py                    # FastAPI app + lifespan + CORS
    api/
      router.py                # active routes
      alerts.py                # scaffold (empty)
      ingestion.py             # scaffold (empty)
    services/
      simulator.py             # synthetic IoT event stream
      behaviour.py             # expected behavior windows
      anamoly.py               # anomaly detection rules
      alert_service.py         # alert/dashboard composition
      gemini_client.py         # Gemini + fallback explanation layer
      processing.py            # scaffold (empty)
    db/                        # scaffold (empty files)
    models/                    # mostly scaffold; schemas.py has active models
    schemas/                   # mostly scaffold; iot.py active
    pipelines/                 # scaffold (empty)
    utils/                     # scaffold (empty)

frontend/
  src/
    pages/
      Index.tsx                # implemented dashboard route
      NotFound.tsx             # fallback route
    components/
      dashboard/               # dashboard widgets and cards
      layout/                  # sidebar/navbar/layout shell
      ui/                      # UI primitives used by app
    contexts/RoleContext.tsx   # role switching context
    hooks/                     # helper hooks
    lib/utils.ts               # className merge helper
    test/                      # Vitest setup + basic example test
  vite.config.ts               # Vite dev server config (port 8080)
  vitest.config.ts             # test configuration

docker/
  Dockerfile                   # placeholder (empty)
  docker-compose.yml           # placeholder (empty)
```

## API Endpoints (Current)

- `GET /activity?role=caregiver|supervisor|family`
- `GET /alerts?role=caregiver|supervisor|family`
- `GET /insight?role=caregiver|supervisor|family`
- `GET /dashboard?role=caregiver|supervisor|family`
- `POST /alerts/action`
  - body: `{ "alert_id": <int>, "action": "approve" | "reject" }`
- `POST /alerts/demo/seed?role=supervisor`
- `POST /simulate/start`
- `POST /simulate/stop`
- `GET /simulate/status`
- `GET /gemini/status`

## Environment Variables

Create `.env` at repository root for Gemini mode:

```env
GEMINI_ENABLED=true
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT_SECONDS=6
```

If `GEMINI_ENABLED=false`, explanations are served from fallback logic.

## Local Setup

### Backend

From repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: `http://127.0.0.1:8000`

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:8080`

## Current Risks / Improvement Targets

1. Replace hardcoded frontend API URLs with `VITE_API_BASE_URL`.
2. Implement actual route pages for `/alerts`, `/activity`, and `/settings`.
3. Add persistent storage layer for events and alert actions.
4. Fill scaffolded backend modules (`db`, `pipelines`, `schemas`) with integrated logic.
5. Add stronger automated tests (backend service tests + frontend behavior tests).
6. Complete Docker definitions for reproducible local/dev deployment.

## Note

This is currently a demo build for the proposal. Active development is in progress.

