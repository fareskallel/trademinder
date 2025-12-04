# backend/rules_service/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import Base, engine
import rules_service.models  # noqa: F401  # ensure TradingRule is registered

from rules_service.routers import rules as rules_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic (if needed later)


app = FastAPI(
    title="TraderMind Rules Service",
    description="Service for managing trader-defined trading rules.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "rules"}


app.include_router(rules_router.router)
