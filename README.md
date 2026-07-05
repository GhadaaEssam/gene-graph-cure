# Gene Graph Cure

Gene Graph Cure is a full-stack research platform for predicting cancer drug resistance and recommending biologically informed alternative therapies. It combines graph-based machine learning, pathway and gene-expression signals, an alternative drug recommendation system, and interactive web/mobile interfaces for exploring analysis results.

The project is organized around two core capabilities:

- **GC-PGE prediction**: graph convolution and pathway/gene-expression modeling for drug-response analysis.
- **ADRS recommendation**: an Alternative Drug Recommendation System that ranks candidate therapies using DrugBank/GDSC-derived knowledge graphs, pathway evidence, and model output.

## Project Structure

```text
.
|-- backend/                 FastAPI API, database models, ML services, ADRS modules
|   |-- app/                 Integrated API application
|   |-- adrs/                Alternative drug recommendation logic
|   |-- gcpge/               GC-PGE model and preprocessing code
|   `-- scripts/             Data preparation and utility scripts
|-- frontend/                React web app built with Create React App
|-- mobile/genegraph-mobile/ Expo mobile app
|-- scripts/rag/             PubMed scraping and vector database utilities
|-- checks/                  Lightweight validation scripts
|-- infra/docker/            Docker Compose and infrastructure helpers
`-- requirements.txt         Root Python dependencies for ML/RAG workflows
```

## Features

- Upload and run gene-expression based drug-resistance analyses.
- Predict drug response using GC-PGE model components.
- Generate pathway-aware alternative drug recommendations.
- Explore graph visualizations of genes, drugs, and pathway relationships.
- Store users, sessions, analyses, reports, dashboard data, and prediction history in PostgreSQL.
- Use an AI assistant/RAG layer for biomedical explanation and report support.
- Access the system from both a web dashboard and an Expo mobile client.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, PostgreSQL
- **ML/Graph**: PyTorch, PyTorch Geometric, NetworkX, NumPy, Pandas, scikit-learn
- **RAG/Knowledge Base**: LangChain, ChromaDB, Biopython, sentence-transformers
- **Web**: React, React Router, Bootstrap, Cytoscape, Three.js
- **Mobile**: Expo, React Native, Expo Router

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- PostgreSQL
- CUDA-capable GPU recommended for the pinned PyTorch builds
- Optional: Ollama running locally for AI assistant generation at `http://localhost:11434`

> The backend requirements pin CUDA-specific PyTorch wheels. If you are using CPU-only Python or a different CUDA version, adjust the PyTorch packages before installing.

## Environment

Create a backend environment file at `backend/.env` when you need to override defaults:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/gc_pge_db
ADRS_DATA_DIR=adrs/data
```

Defaults currently used by the code:

- Main API database: `postgresql://postgres:post10900@localhost:5432/gc_pge_db`
- ADRS cache database: `postgresql://postgres:ghpostgres@localhost:5432/gc_pge_db`
- Frontend origin allowed by CORS: `http://localhost:3000`

For local development, using `DATABASE_URL` is the cleanest way to keep all backend database connections pointed at the same PostgreSQL instance.

## Backend Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

Start the integrated API:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Useful endpoints:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ADRS health: `http://127.0.0.1:8000/api/v1/adrs/health`
- ADRS recommendation: `POST http://127.0.0.1:8000/api/v1/adrs/recommend`

The legacy root-level `main.py` can run ADRS separately on port `8001`, but the preferred development path is the integrated backend app in `backend/app/main.py`.

## Web Frontend Setup

```powershell
cd frontend
npm install
npm start
```

The React web app runs at:

```text
http://localhost:3000
```

Production build:

```powershell
npm run build
```

## Mobile App Setup

```powershell
cd mobile\genegraph-mobile
npm install
npx expo start
```

The mobile API base URL is currently configured in:

```text
mobile/genegraph-mobile/services/api.js
```

Update it to match the host running the FastAPI backend, especially when testing on a physical device.

## RAG and Data Utilities

The `scripts/rag/` folder contains utilities for PubMed scraping and vector database construction:

```powershell
python scripts\rag\scrape_pubmed.py
python scripts\rag\build_vector_db.py
python scripts\rag\test_vector_db.py
```

Backend data preparation scripts live under `backend/scripts/`, including gene ID mapping, training-data generation, GEO median computation, and ADRS data setup.

## Checks and Tests

Run focused backend validation scripts from the repository root:

```powershell
python checks\check_models.py
python checks\check_api.py
python checks\check_graph.py
python checks\check_recommender.py
```

Run frontend tests:

```powershell
cd frontend
npm test
```

## API Areas

The integrated backend includes routes for:

- `POST /predict`
- `GET /jobs/{job_id}`
- `POST /analysis/run`
- `GET /analysis/{job_id}`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /dashboard/summary`
- `GET /dashboard/recent`
- `GET /dashboard/analyses`
- `GET /graph/{job_id}`
- `POST /chat/send`
- `GET /api/v1/adrs/health`
- `POST /api/v1/adrs/recommend`

## Development Notes

- Keep generated data, trained model artifacts, and local secrets out of Git.
- Prefer `backend/app/main.py` for full-system API development.
- Use `ADRS_DATA_DIR` when ADRS data files are stored outside the default location.
- The web app assumes the backend is reachable locally; mobile devices may need a LAN IP address instead of `localhost`.

## Status

This repository is an active graduation/research project. Expect model artifacts, biomedical datasets, and deployment configuration to vary between local machines. The README favors reproducible local development and clearly marks the pieces that are environment-dependent.
