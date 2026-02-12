from fastapi import FastAPI

app = FastAPI(title="Gene Graph Cure Backend")

@app.get("/")
def health_check():
    return {"status": "Backend running"}
