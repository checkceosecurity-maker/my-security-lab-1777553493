from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="AG2 Platform API", version="1.0.0")

# Keep the API usable from a separately hosted static frontend. Restrict this in
# production with the FRONTEND_ORIGIN environment variable.
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin] if frontend_origin != "*" else ["*"],
    allow_credentials=frontend_origin != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)

now = lambda: datetime.now(timezone.utc).isoformat()

agents: list[dict[str, Any]] = [
    {"id": "agent-security-analyst", "name": "Security Analyst", "status": "running", "description": "วิเครา��ห์เหตุการณ์ด้านความปลอดภัย", "updated_at": now()},
    {"id": "agent-threat-report", "name": "Threat Reporter", "status": "idle", "description": "สร้างรายงานภัยคุกคามประจำวัน", "updated_at": now()},
]
tasks: list[dict[str, Any]] = [
    {"id": "task-daily-report", "name": "Daily threat report", "status": "completed", "agent_id": "agent-threat-report", "updated_at": now()},
]
tools = [
    {"id": "tool-http", "name": "HTTP Client", "category": "connector", "status": "installed"},
    {"id": "tool-browser", "name": "Browser", "category": "automation", "status": "installed"},
]
members = [{"id": "member-owner", "name": "Workspace owner", "role": "admin", "status": "active"}]


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)


class TaskCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    agent_id: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ag2-platform-api", "time": now()}


@app.get("/api/agents")
def list_agents() -> dict[str, Any]:
    return {"items": agents, "total": len(agents)}


@app.post("/api/agents", status_code=status.HTTP_201_CREATED)
def create_agent(payload: AgentCreate) -> dict[str, Any]:
    agent = {"id": f"agent-{uuid4().hex[:10]}", "name": payload.name, "description": payload.description, "status": "idle", "updated_at": now()}
    agents.append(agent)
    return agent


@app.get("/api/agents/{agent_id}")
def get_agent(agent_id: str) -> dict[str, Any]:
    for agent in agents:
        if agent["id"] == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")


@app.get("/api/tasks")
def list_tasks() -> dict[str, Any]:
    return {"items": tasks, "total": len(tasks)}


@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict[str, Any]:
    if payload.agent_id and not any(a["id"] == payload.agent_id for a in agents):
        raise HTTPException(status_code=400, detail="Unknown agent_id")
    task = {"id": f"task-{uuid4().hex[:10]}", "name": payload.name, "agent_id": payload.agent_id, "status": "queued", "updated_at": now()}
    tasks.append(task)
    return task


@app.get("/api/tools")
def list_tools() -> dict[str, Any]:
    return {"items": tools, "total": len(tools)}


@app.get("/api/members")
def list_members() -> dict[str, Any]:
    return {"items": members, "total": len(members)}


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    # Safe local fallback. Connect a model provider here when credentials and a
    # persistent conversation store are available.
    return {"reply": f"ได้รับข้อความแล้วครับ: {payload.message}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.index:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
