# app/main.py
from fastapi import FastAPI
from app.core.database import engine 
from app.db.models import Base 
from app.api.v1 import predict, jobs, analyses , auth , chat , dashboard , graph


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(jobs.router)
app.include_router(analyses.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(graph.router)






Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Gene Graph Cure API is running"}