def build_prompt(
    prediction_label,
    confidence,
    top_genes,
    top_pathways,
    rag_context,
):

    genes_text = "\n".join(
        f"- {name} (score={score:.4f})"
        for name, score in top_genes
    )

    pathways_text = "\n".join(
        f"- {name} (weight={weight:.4f})"
        for name, weight in top_pathways
    )

    prompt = f"""
You are an expert biomedical AI assistant.

MODEL PREDICTION
----------------
Prediction: {prediction_label}

Confidence: {confidence:.4f}

TOP GENES
---------
{genes_text}

TOP PATHWAYS
------------
{pathways_text}

SCIENTIFIC EVIDENCE
-------------------
{rag_context}

TASK
----
Explain:

1. What the prediction means
2. Why these genes are important
3. Why these pathways are important
4. Possible biological mechanisms
5. Supporting literature evidence

Use only the supplied evidence.
Do not invent genes, pathways, or studies.
"""

    return prompt