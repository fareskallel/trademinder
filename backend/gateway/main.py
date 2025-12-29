import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings

app = FastAPI(
    title="TraderMind Gateway",
    description="Public API gateway for TraderMind OS.",
    version="0.4.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ORCH_BASE = f"http://{settings.orchestrator_host}:{settings.orchestrator_port}"


async def forward(request: Request, path: str) -> JSONResponse:
    url = f"{ORCH_BASE}{path}"
    body = await request.body()

    async with httpx.AsyncClient(timeout=40.0) as client:
        try:
            resp = await client.request(
                request.method,
                url,
                content=body,
                headers={
                    k: v
                    for k, v in request.headers.items()
                    if k.lower() != "host"
                },
                params=request.query_params,
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Orchestrator at {url} unreachable: {e}",
            )

    content_type = resp.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    else:
        return JSONResponse(status_code=resp.status_code, content=resp.text)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway"}


# ---------------------------------------------------------
# FEEDBACK — Proxy
# ---------------------------------------------------------

@app.api_route("/feedback/analyze", methods=["POST"])
async def gw_feedback_analyze(request: Request):
    return await forward(request, "/feedback/analyze")


@app.api_route("/feedback/save", methods=["POST"])
async def gw_feedback_save(request: Request):
    return await forward(request, "/feedback/save")


@app.api_route("/feedback", methods=["GET"])
async def gw_feedback_list(request: Request):
    return await forward(request, "/feedback")


@app.api_route("/feedback/{entry_id}", methods=["GET"])
async def gw_feedback_get(request: Request, entry_id: int):
    return await forward(request, f"/feedback/{entry_id}")


# ---------------------------------------------------------
# RULES — Proxy
# ---------------------------------------------------------

@app.api_route("/rules", methods=["GET", "POST"])
async def gw_rules_root(request: Request):
    return await forward(request, "/rules")


@app.api_route("/rules/{subpath:path}", methods=["GET", "PUT", "PATCH", "DELETE"])
async def gw_rules_subpath(request: Request, subpath: str):
    return await forward(request, f"/rules/{subpath}")
