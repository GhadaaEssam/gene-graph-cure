from fastapi import APIRouter

router = APIRouter(prefix="/graph", tags=["Visualization"])

@router.get("/{job_id}")
async def get_graph(job_id: str):
    # هنا بنرجع هيكل البيانات اللي مكتبة react-force-graph مستنياه
    return {
        "nodes": [
            {"id": "TP53", "type": "gene", "highlight": True},
            {"id": "KRAS", "type": "gene", "highlight": True},
            {"id": "EGFR", "type": "gene", "highlight": False},
            {"id": "BRCA1", "type": "gene", "highlight": False},
            {"id": "MAPK Pathway", "type": "pathway"}
        ],
        "links": [
            {"source": "TP53", "target": "MAPK Pathway"},
            {"source": "KRAS", "target": "MAPK Pathway"},
            {"source": "EGFR", "target": "KRAS"},
            {"source": "BRCA1", "target": "TP53"}
        ]
    }