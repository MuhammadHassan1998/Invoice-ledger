from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.v1 import auth as auth_v1
from app.routers.v1 import invoices as invoices_v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run any pending migrations against the operational SQLite DB on startup.
    # The DuckDB analytics store is managed by dbt; we never touch it here.
    cfg = Config(str(Path(__file__).parent / "alembic.ini"))
    command.upgrade(cfg, "head")
    yield


app = FastAPI(
    title="Invoice Ledger API",
    version="1.0.0",
    description="Serves processed invoice data from the dbt mart layer.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(auth_v1.router, prefix="/api/v1")
app.include_router(invoices_v1.router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}
