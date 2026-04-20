import os
import logging
import torch
import numpy as np
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from pathlib import Path

# Suppress ChromaDB Telemetry
os.environ["CHROMA_TELEMETRY_IMPL"] = "None"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

class RAGService:
    def __init__(self):
        # Resolve absolute path to the vector database (go up 4 levels to the main repo root)
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.db_path = str(self.project_root / "data" / "vector_store")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.vectorstore = None
        self._init_db()

    def _init_db(self):
        """Connects to the persistent vector database."""
        if not os.path.exists(self.db_path):
            logging.warning(f"Database not found at {self.db_path}. RAG will be disabled.")
            return

        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': self.device}, 
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore = Chroma(
            persist_directory=self.db_path, 
            embedding_function=embeddings
        )

    def generate_evidence(self, prediction_result: dict, anchor_genes_df: pd.DataFrame):
        """
        Takes the raw JSON output from the model, finds the top genes/pathways,
        and queries the database.
        """
        if not self.vectorstore:
            return [{"title": "RAG Disabled", "excerpt": "Vector database not found."}]

        # 1. Extract the gene importances from the model output
        vimp_g = prediction_result.get('vimp_g', [])
        
        # 2. Find the indices of the top 3 highest scores
        # np.argsort sorts ascending, so we take the last 3 and reverse them
        top_indices = np.argsort(vimp_g)[-3:][::-1]
        
        # 3. Map indices back to gene names
        # Assuming the first column of anchor_genes_df holds the names
        gene_names = anchor_genes_df.iloc[:, 0].tolist()
        
        top_genes = []
        for idx in top_indices:
            if idx < len(gene_names):
                top_genes.append(str(gene_names[idx]))

        if not top_genes:
            return [{"title": "Notice", "excerpt": "Could not map genes for query."}]

        # 4. Formulate the Query
        genes_str = ", ".join(top_genes)
        query = f"How do the genes {genes_str} influence drug resistance in cancer?"
        
        # 5. Search the Database
        results = self.vectorstore.similarity_search(query, k=3)
        
        evidence = []
        for res in results:
            evidence.append({
                "title": res.metadata.get('title', 'Unknown'),
                "pmid": res.metadata.get('pmid', 'Unknown'),
                "excerpt": res.page_content[:300] # Limiting excerpt length for the API response
            })
            
        return evidence