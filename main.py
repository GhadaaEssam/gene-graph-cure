"""
Gene Graph Cure — ADRS Server
Alternative Drug Recommendation System

Run command (ALWAYS use port 8001 — GC-PGE uses port 8000):
    uvicorn main:app --reload --port 8001

Swagger docs:  http://127.0.0.1:8001/docs
Health check:  http://127.0.0.1:8001/api/v1/adrs/health
Recommend:     http://127.0.0.1:8001/api/v1/adrs/recommend
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


logger = logging.getLogger(__name__)

# ── Data directory (configurable via environment variable) ─────────
DATA_DIR = Path(os.getenv("ADRS_DATA_DIR", "backend/adrs/data"))

# ── Port note ─────────────────────────────────────────────────────
# GC-PGE server  → port 8000  (teammates' prediction model)
# ADRS server    → port 8001  (this file — drug recommendations)
# Never run both on the same port.


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs at startup before the server accepts any requests.
    Loads all indexes into memory and builds the knowledge graph.
    Also connects to PostgreSQL if available (not required to run).
    """
    logger.info("══════════════════════════════════════════════════")
    logger.info("  ADRS startup — loading indexes and graph")
    logger.info("══════════════════════════════════════════════════")

    from backend.adrs_old.db_parser import load_drugbank_index, load_gdsc_index
    from backend.adrs_old.graph_builder import build_knowledge_graph

    # ── Load data indexes ─────────────────────────────────────────
    try:
        logger.info("Loading DrugBank index...")
        drugbank_index = load_drugbank_index(str(DATA_DIR / "drugbank_index.json"))

        logger.info("Loading GDSC index...")
        gdsc_index = load_gdsc_index(str(DATA_DIR / "gdsc_index.json"))

        logger.info("Building knowledge graph...")
        graph = build_knowledge_graph(drugbank_index, gdsc_index)

        # Store on app state — accessible in every request handler
        app.state.drugbank_index = drugbank_index
        app.state.gdsc_index     = gdsc_index
        app.state.graph          = graph

        drug_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "drug"]
        logger.info(
            f"Graph ready: {len(drug_nodes)} drugs | "
            f"{graph.number_of_edges()} edges"
        )

    except FileNotFoundError as e:
        logger.error(
            f"Data file not found: {e}\n"
            f"Make sure you have run: python -m backend.adrs.setup_data"
        )
        raise
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise

    # ── Connect to PostgreSQL (optional — ADRS works without it) ──
    # If DB is not available, the system runs normally but without caching.
    # Cached results are stored in DB so the same patient+drug combo
    # returns instantly on the second call instead of re-computing.
    try:
        from backend.adrs_old.db_tables import create_tables, get_session_factory
        import backend.adrs_old.api as adrs_api

        logger.info("Connecting to PostgreSQL...")
        create_tables()                                    # creates tables if they don't exist
        adrs_api._SessionFactory = get_session_factory()  # wire session into API
        logger.info("PostgreSQL connected — caching enabled")

    except Exception as e:
        logger.warning(
            f"PostgreSQL not available ({e.__class__.__name__}: {e})\n"
            f"Running WITHOUT database cache — all features still work."
        )
        # _SessionFactory stays None — api.py handles this gracefully

    logger.info("══════════════════════════════════════════════════")
    logger.info("  ADRS startup complete — listening on port 8001")
    logger.info("  Docs:   http://127.0.0.1:8001/docs")
    logger.info("  Health: http://127.0.0.1:8001/api/v1/adrs/health")
    logger.info("══════════════════════════════════════════════════")

    yield  # ← server runs here, handling requests

    logger.info("ADRS shutting down...")


# ── Create FastAPI app ────────────────────────────────────────────
app = FastAPI(
    title       = "Gene Graph Cure — ADRS",
    description = (
        "Alternative Drug Recommendation System. "
        "Receives GC-PGE model output (pw_w + vimp_g) and returns "
        "top-N ranked alternative drugs for drug-resistant cancer patients."
    ),
    version     = "1.0.0",
    lifespan    = lifespan
)

# ── CORS — allows frontend and other services to call this API ────
# allow_origins=["*"] means any server can call us.
# In production you would restrict this to specific domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"]
)

# ── Register ADRS router ──────────────────────────────────────────
# All ADRS endpoints will be at /api/v1/adrs/...
from backend.adrs_old.api import router as adrs_router
app.include_router(adrs_router, prefix="/api/v1")


# ── Root endpoint ─────────────────────────────────────────────────
@app.get("/", tags=["Status"])
async def root():
    """Quick check that the ADRS server is running."""
    return {
        "service": "Gene Graph Cure — ADRS",
        "status":  "running",
        "port":    8001,
        "docs":    "http://127.0.0.1:8001/docs",
        "health":  "http://127.0.0.1:8001/api/v1/adrs/health",
        "note":    "GC-PGE prediction server runs on port 8000"
    }