import importlib
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

load_dotenv = None
try:
    dotenv = importlib.import_module("dotenv")
    load_dotenv = dotenv.load_dotenv
except ImportError:
    pass

if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:ghpostgres@localhost:5432/gc_pge_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()