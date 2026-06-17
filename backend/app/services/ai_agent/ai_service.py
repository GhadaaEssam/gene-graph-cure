import logging

from app.services.rag_service import RAGService

from .extractor import (
    extract_top_genes,
    extract_top_pathways,
)

from .prompt_builder import build_prompt
from .llm_client import generate_text


logger = logging.getLogger(__name__)

rag_service = RAGService()


def format_evidence(evidence):

    text = ""

    for item in evidence:

        text += f"""
Title: {item.get("title")}

PMID: {item.get("pmid")}

Summary:
{item.get("excerpt")}
"""

    return text


def run_ai_analysis(
    analysis_result: dict,
    cancer_type: str | None = None,
    drug: str | None = None,
):

    top_genes = extract_top_genes(analysis_result)

    top_pathways = extract_top_pathways(analysis_result)

    evidence = analysis_result.get("rag_evidence")

    if not evidence:

        evidence = rag_service.generate_evidence(
            prediction_result=analysis_result,
            anchor_genes_df=None,
            node_features_df=None,
            cancer_type=cancer_type,
            drug=drug,
        )

    rag_context = format_evidence(evidence)

    prediction = analysis_result.get("prediction")

    if isinstance(prediction, list):
        prediction = prediction[0]

    prediction_label = (
        "Resistant"
        if prediction == 1
        else "Sensitive"
    )

    confidence = 0.0

    probs = analysis_result.get("out_probabilities")
    if probs:
        if isinstance(probs[0], list):
            confidence = max(probs[0])     # nested: [[0.1, 0.9]] → 0.9
        else:
            confidence = max(probs)        # flat:   [0.1, 0.9]   → 0.9

    prompt = build_prompt(
        prediction_label=prediction_label,
        confidence=confidence,
        top_genes=top_genes,
        top_pathways=top_pathways,
        rag_context=rag_context,
    )

    explanation = generate_text(prompt)

    return {
        "prediction": prediction_label,
        "confidence": confidence,
        "top_genes": top_genes,
        "top_pathways": top_pathways,
        "evidence": evidence,
        "explanation": explanation,
    }


def ask_ai(
    question: str,
    analysis_result: dict,
):

    prompt = f"""
You are an expert biomedical AI assistant.

Analysis Result:

{analysis_result}

User Question:

{question}

Answer using the analysis result and scientific evidence.
"""

    return generate_text(prompt)