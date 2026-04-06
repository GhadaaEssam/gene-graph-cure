# app/main.py
from fastapi import FastAPI
from app.api.v1 import predict, jobs, analyses

app = FastAPI()

app.include_router(predict.router)
app.include_router(jobs.router)
app.include_router(analyses.router)

# python -m uvicorn app.main:app --reload