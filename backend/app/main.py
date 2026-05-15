import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine
from app.db.models import Base
from app.api.v1 import predict, jobs, analyses
from app.api.v1.adrs import router as adrs_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("ADRS_DATA_DIR", "adrs/data"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Gene Graph Cure API...")

    # ── ADRS startup ──────────────────────────────────────────────
    from adrs.db_parser import load_drugbank_index, load_gdsc_index
    from adrs.graph_builder import build_knowledge_graph

    try:
        logger.info("Loading DrugBank index...")
        drugbank_index = load_drugbank_index(str(DATA_DIR / "drugbank_index.json"))

        logger.info("Loading GDSC index...")
        gdsc_index = load_gdsc_index(str(DATA_DIR / "gdsc_index.json"))

        logger.info("Building knowledge graph...")
        graph = build_knowledge_graph(drugbank_index, gdsc_index)

        app.state.drugbank_index = drugbank_index
        app.state.gdsc_index     = gdsc_index
        app.state.graph          = graph

        drug_nodes = [n for n, d in graph.nodes(data=True) if d.get("type") == "drug"]
        logger.info(f"ADRS graph ready: {len(drug_nodes)} drugs | {graph.number_of_edges()} edges")

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e} — run: python adrs/setup_data.py")
        raise
    except Exception as e:
        logger.error(f"ADRS startup failed: {e}", exc_info=True)
        raise

    # ── PostgreSQL cache (optional) ───────────────────────────────
    try:
        from app.db.models.adrs_db_tables import create_tables, get_session_factory, Base as ADRSBase, get_engine
        logger.info("Connecting to PostgreSQL...")
        create_tables()
        ADRSBase.metadata.create_all(bind=get_engine())
        app.state.adrs_session_factory = get_session_factory()
        logger.info("PostgreSQL connected — caching enabled")
    except Exception as e:
        logger.warning(f"PostgreSQL unavailable ({e.__class__.__name__}: {e}) — running without cache")
        app.state.adrs_session_factory = None

    yield
    logger.info("Shutting down.")


app = FastAPI(title="Gene Graph Cure API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(adrs_router, prefix="/api/v1")
app.include_router(predict.router)
app.include_router(jobs.router)
app.include_router(analyses.router)

Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Status"])
def root():
    return {"message": "Gene Graph Cure API is running"}