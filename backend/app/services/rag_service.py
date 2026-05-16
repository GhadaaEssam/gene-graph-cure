import os
import logging
import torch
import numpy as np
import pandas as pd
import re
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

    def generate_evidence(
        self,
        prediction_result: dict,
        anchor_genes_df: pd.DataFrame,
        node_features_df: pd.DataFrame = None,
        cancer_type: str = None,
        drug: str = None,
        top_k: int = 5,
    ):
        """
        Takes the raw JSON output from the model, finds the top genes/pathways,
        and queries the database with cancer/drug/model-context-aware prompts.
        """
        if not self.vectorstore:
            return [{"title": "RAG Disabled", "excerpt": "Vector database not found."}]

        top_genes = self._extract_top_genes(prediction_result, anchor_genes_df, limit=5)
        top_pathways = self._extract_top_pathways(prediction_result, node_features_df, limit=5)
        is_multiomics = any(
            key in prediction_result
            for key in ("out_multiomics", "out_multiomics_probabilities")
        )

        if not top_genes and not top_pathways:
            return [{"title": "Notice", "excerpt": "Could not map genes or pathways for query."}]

        queries = self._build_queries(
            top_genes=top_genes,
            top_pathways=top_pathways,
            cancer_type=cancer_type,
            drug=drug,
            is_multiomics=is_multiomics,
        )

        evidence = []
        seen_pmids = set()
        for query_type, query in queries:
            results = self.vectorstore.similarity_search(query, k=top_k)
            for res in results:
                pmid = res.metadata.get("pmid", "Unknown")
                if pmid in seen_pmids:
                    continue
                seen_pmids.add(pmid)
                evidence.append({
                    "title": res.metadata.get("title", "Unknown"),
                    "pmid": pmid,
                    "source": res.metadata.get("source", ""),
                    "journal": res.metadata.get("journal", ""),
                    "year": str(res.metadata.get("year", "")),
                    "query_type": query_type,
                    "matched_query": query,
                    "excerpt": res.page_content[:500],
                })

        return evidence[:top_k]

    def _extract_top_genes(self, prediction_result: dict, anchor_genes_df: pd.DataFrame, limit: int):
        scores = prediction_result.get("vimp_g") or prediction_result.get("cor") or []
        if not scores:
            return []

        top_indices = np.argsort(scores)[-limit:][::-1]
        gene_names = self._gene_names_from_anchor(anchor_genes_df)
        top_genes = []
        for idx in top_indices:
            if idx < len(gene_names):
                gene = str(gene_names[idx]).strip()
                if gene and gene not in top_genes:
                    top_genes.append(gene)

        return top_genes

    def _gene_names_from_anchor(self, anchor_genes_df: pd.DataFrame):
        for column in ("gene", "gene_name", "symbol", "Gene", "GeneSymbol"):
            if column in anchor_genes_df.columns:
                return anchor_genes_df[column].tolist()

        # Some exports include an unnamed index column before the real gene
        # column. Prefer the first non-index, non-label text-like column.
        ignored = {"id", "result_num", "Unnamed: 0", ""}
        for column in anchor_genes_df.columns:
            if str(column) in ignored:
                continue
            return anchor_genes_df[column].tolist()

        return anchor_genes_df.iloc[:, 0].tolist()

    def _extract_top_pathways(self, prediction_result: dict, node_features_df: pd.DataFrame, limit: int):
        if node_features_df is None or "pw_w" not in prediction_result:
            return []

        pathway_scores = prediction_result.get("pw_w") or []
        if not pathway_scores:
            return []

        pathway_names = list(node_features_df.columns[1:])
        top_indices = np.argsort(pathway_scores)[-limit:][::-1]
        top_pathways = []
        for idx in top_indices:
            if idx < len(pathway_names):
                pathway = self._clean_pathway_name(pathway_names[idx])
                if pathway and pathway not in top_pathways:
                    top_pathways.append(pathway)

        return top_pathways

    def _clean_pathway_name(self, pathway_name: str):
        pathway = str(pathway_name)
        pathway = re.sub(r"^(KEGG|REACTOME|BIOCARTA|PID|NABA|SA|SIG)_", "", pathway)
        pathway = pathway.replace("_", " ").strip()
        return pathway

    def _build_queries(
        self,
        top_genes,
        top_pathways,
        cancer_type: str = None,
        drug: str = None,
        is_multiomics: bool = False,
    ):
        cancer_text = cancer_type.strip() if cancer_type else "cancer"
        drug_text = drug.strip() if drug else "therapy"
        genes_text = ", ".join(top_genes) if top_genes else "model-selected genes"
        pathways_text = ", ".join(top_pathways) if top_pathways else "model-selected pathways"

        queries = [
            (
                "gene_drug_resistance",
                (
                    f"In {cancer_text} treated with {drug_text}, what evidence links "
                    f"{genes_text} to drug resistance, treatment response, prognosis, "
                    "or predictive biomarkers?"
                ),
            ),
            (
                "pathway_drug_resistance",
                (
                    f"In {cancer_text} treated with {drug_text}, how do the pathways "
                    f"{pathways_text} contribute to resistance, sensitivity, tumor "
                    "progression, immune evasion, or treatment response?"
                ),
            ),
        ]

        if is_multiomics:
            queries.append((
                "multiomics_mechanism",
                (
                    f"Multi-omics evidence in {cancer_text} treated with {drug_text}: "
                    f"integrated transcriptomics, DNA methylation, copy number variation, "
                    f"mutation or SNV data involving {genes_text} and {pathways_text} "
                    "for therapy resistance or response prediction."
                ),
            ))

        return queries
