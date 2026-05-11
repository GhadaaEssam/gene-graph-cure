# app/main.py
from fastapi import FastAPI
from app.core.database import engine 
from app.db.models import Base 
from app.api.v1 import predict, jobs, analyses


app = FastAPI()

app.include_router(predict.router)
app.include_router(jobs.router)
app.include_router(analyses.router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Gene Graph Cure API is running"}