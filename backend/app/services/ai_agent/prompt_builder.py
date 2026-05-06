def build_prompt(result, top_pathways, top_genes, rag_context):
    """
    Builds a structured, clinical-grade prompt for the LLM.
    Forces the model to use GC-PGE outputs + RAG evidence.
    """

    # =========================
    # 🔹 Format prediction
    # =========================
    prediction_label = "Resistant" if result["prediction"] == 1 else "Sensitive"
    confidence = round(float(result["probability"]), 4)

    # =========================
    # 🔹 Format genes
    # =========================
    genes_text = "\n".join([f"- {g[0]} (importance: {round(g[1], 3)})" for g in top_genes])

    # =========================
    # 🔹 Format pathways
    # =========================
    pathways_text = "\n".join([f"- {p[0]} (weight: {round(p[1], 3)})" for p in top_pathways])

    # =========================
    # 🔹 Final Prompt
    # =========================
    prompt = f"""
You are an AI medical assistant specialized in oncology and drug resistance.

Your task is to generate a clear, clinically meaningful explanation of a tumor drug resistance prediction using model outputs and scientific evidence.

-----------------------------
🔬 MODEL PREDICTION
-----------------------------
- Drug Response: {prediction_label}
- Confidence Score: {confidence}

-----------------------------
🧬 KEY GENES (from model)
-----------------------------
{genes_text}

-----------------------------
🧪 IMPORTANT PATHWAYS
-----------------------------
{pathways_text}

-----------------------------
📚 SCIENTIFIC EVIDENCE
-----------------------------
{rag_context}

-----------------------------
🧠 INSTRUCTIONS
-----------------------------
Generate a structured explanation with the following sections:

1. Prediction Summary  
   - Clearly state whether the tumor is resistant or sensitive  
   - Mention the confidence level  

2. Key Molecular Drivers  
   - Explain the role of the listed genes  
   - Focus on how they contribute to drug resistance  

3. Pathway-Level Interpretation  
   - Explain how the pathways influence tumor behavior  
   - Link pathways to resistance mechanisms  

4. Biological Mechanism  
   - Provide a coherent explanation of WHY resistance occurs  
   - Integrate genes + pathways together  

5. Supporting Evidence  
   - Use the provided scientific evidence (PMIDs if available)  
   - Do NOT invent studies  

-----------------------------
⚠️ RULES
-----------------------------
- Use ONLY the provided genes, pathways, and evidence  
- Do NOT hallucinate gene names or mechanisms  
- Keep explanation concise but informative  
- Use professional medical language  
- Avoid unnecessary repetition  
- If you are unsure about the biological function of a pathway,
do NOT assume its role. Only describe it in general terms.

-----------------------------
🎯 OUTPUT FORMAT
-----------------------------
Write in well-structured paragraphs with clear section headers.

"""

    return prompt