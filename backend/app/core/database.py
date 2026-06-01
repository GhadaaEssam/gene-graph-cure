import importlib
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------
# OPTIONAL dotenv SUPPORT
# ---------------------------------------------------
load_dotenv = None

try:
    dotenv = importlib.import_module("dotenv")
    load_dotenv = dotenv.load_dotenv
except ImportError:
    pass

if load_dotenv is not None:
    load_dotenv(
        Path(__file__).resolve().parents[1] / ".env"
    )

# ---------------------------------------------------
# DATABASE URL
# ---------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1422004@localhost:5432/gc_pge_db"
)

# ---------------------------------------------------
# SQLALCHEMY ENGINE
# ---------------------------------------------------
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# ---------------------------------------------------
# DATABASE SESSION
# ---------------------------------------------------
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()