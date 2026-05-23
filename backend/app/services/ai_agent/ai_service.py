from .parser import load_results
from .prompt_builder import build_prompt
from .llm_client import generate_text
from app.services.rag_service import RAGService

import pandas as pd
import numpy as np


# =========================
# 🔹 Extract Top Genes from Graph
# =========================
def get_top_genes_from_graph(graph, gene_names, k=5):
    graph = np.array(graph)

    # Gene importance = total connections
    importance = graph.sum(axis=1)

    top_idx = importance.argsort()[-k:][::-1]

    return [(gene_names[i], float(importance[i])) for i in top_idx]


# =========================
# 🔹 Extract Top Pathways (No Names Available)
# =========================

def load_pathway_names(base_path):
    df = pd.read_csv(f"{base_path}/pw_id.csv")
    return df["pwid"].tolist()

def get_top_pathways(weights, pathway_names, k=5):
    weights = np.array(weights)

    idx = weights.argsort()[-k:][::-1]

    return [
        (pathway_names[i], float(weights[i]))
        for i in idx if i < len(pathway_names)
    ]


# =========================
# 🔹 Convert Graph → vimp_g (for RAG)
# =========================
def build_vimp_from_graph(graph):
    graph = np.array(graph)
    importance = graph.sum(axis=1)
    return importance.tolist()


# =========================
# 🔹 Format RAG Evidence for LLM
# =========================
def format_evidence(evidence):
        text = ""

        for e in evidence:
            title = e.get("title", "Unknown")
            pmid = e.get("pmid", "N/A")
            excerpt = e.get("excerpt", "")

            text += f"""
    Title: {title}
    PMID: {pmid}
    Summary: {excerpt}
    """

        return text

# =========================
# 🔹 MAIN AI FUNCTION
# =========================
def run_ai(base_path):

    result = load_results(base_path)

    # genes
    anchor_df = pd.read_csv(f"{base_path}/test_anchor.csv", header=None)
    gene_names = [f"Gene_{gid}" for gid in anchor_df.iloc[:, 0].tolist()]

    # pathways
    pathway_names = load_pathway_names(base_path)

    # extract
    top_genes = get_top_genes_from_graph(result["graph"], gene_names)

    top_pathways = get_top_pathways(
        result["pathway_weights"],
        pathway_names
    )

    # RAG
    rag = RAGService()
    vimp_g = build_vimp_from_graph(result["graph"])

    evidence = rag.generate_evidence(
        {"vimp_g": vimp_g},
        anchor_df
    )

    rag_context = format_evidence(evidence)

    # LLM
    prompt = build_prompt(result, top_pathways, top_genes, rag_context)
    explanation = generate_text(prompt)

    return {
        "prediction": result["prediction"],
        "confidence": result["probability"],
        "top_genes": top_genes,
        "top_pathways": top_pathways,
        "evidence": evidence,
        "explanation": explanation
    }
    
# =========================
# 🔹 LIVE CHAT FROM ANALYSIS
# =========================

def ask_ai_from_analysis(question: str, analysis_result: dict):

    # -------------------------
    # Extract important features
    # -------------------------

    top_genes = []
    top_pathways = []

    # genes
    if "graph" in analysis_result and "gene_names" in analysis_result:
        top_genes = get_top_genes_from_graph(
            analysis_result["graph"],
            analysis_result["gene_names"]
        )

    # pathways
    if "pw_w" in analysis_result and "pathway_names" in analysis_result:
        top_pathways = get_top_pathways(
            analysis_result["pw_w"],
            analysis_result["pathway_names"]
        )

    # -------------------------
    # Build RAG evidence
    # -------------------------

    rag_context = ""

    try:
        if "graph" in analysis_result and "anchor_df" in analysis_result:

            rag = RAGService()

            vimp_g = build_vimp_from_graph(
                analysis_result["graph"]
            )

            evidence = rag.generate_evidence(
                {"vimp_g": vimp_g},
                analysis_result["anchor_df"]
            )

            rag_context = format_evidence(evidence)

    except Exception as e:
        print("RAG ERROR:", e)

    # -------------------------
    # Build final prompt
    # -------------------------

    prompt = f"""
You are an expert biomedical AI assistant.

Patient analysis summary:

Prediction:
{analysis_result.get("prediction")}

Confidence:
{analysis_result.get("confidence")}

Top Pathways:
{top_pathways}

Top Genes:
{top_genes}

Scientific Evidence:
{rag_context}

User Question:
{question}

Provide a medically accurate explanation in clear language.
"""

    # -------------------------
    # Generate response
    # -------------------------

    response = generate_text(prompt)

    return response