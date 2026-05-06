from fastapi import APIRouter
from app.services.ai_agent.ai_service import run_ai_analysis

router = APIRouter()

@router.get("/ai-analysis")
def ai_analysis():

    pathway_names = [...]  # load from file
    gene_names = [...]     # load from file

    result = run_ai_analysis(
        base_path="path_to_output_files",
        pathway_names=pathway_names,
        gene_names=gene_names,
        rag_context=None  # integrate later
    )

    return result