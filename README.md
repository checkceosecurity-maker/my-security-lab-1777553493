# AG2 Platform

Dashboard + FastAPI + SQLAlchemy database + JWT login.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.index:app --reload
```

Open `http://localhost:8000`, then use `demo@ag2.local` / `demo123`.

Set `DATABASE_URL` to a PostgreSQL connection string for production. SQLite is used by default locally. Set a strong `SECRET_KEY` and exact `FRONTEND_ORIGIN` in deployment settings. The API creates its tables automatically on startup; use migrations before production schema changes.
