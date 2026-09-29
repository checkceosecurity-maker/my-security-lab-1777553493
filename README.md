# AG2 Platform

This repository now includes a small FastAPI API layer for the static dashboard.
It provides working demo endpoints for agents, tasks, tools, members, health, and chat.
The data is intentionally in-memory for the prototype; restart/redeploy resets it.

## Run locally

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn api.index:app --reload
```

Open the API docs at `http://localhost:8000/docs`.

## Endpoints

- `GET /api/health`
- `GET|POST /api/agents`
- `GET|POST /api/tasks`
- `GET /api/tools`
- `GET /api/members`
- `POST /api/chat`

## Production gaps

Authentication, a persistent database, job workers, and a real model provider still need
separate configuration before this is used with sensitive or production data. Set
`FRONTEND_ORIGIN` to the exact frontend origin when deploying.
