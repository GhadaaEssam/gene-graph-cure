import json
import logging
import networkx as nx
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def build_knowledge_graph(
    drugbank_index: Dict,
    gdsc_index: Dict
) -> nx.Graph:
    """
    Build a bipartite knowledge graph linking drugs to genes and pathways.
    Built ONCE at app startup and kept in memory.

    Nodes:
        - Drug nodes:    type='drug'
        - Gene nodes:    type='gene'
        - Pathway nodes: type='pathway'

    Edges:
        - Drug → Gene:    relation='targets'
        - Drug → Pathway: relation='affects'

    Args:
        drugbank_index: output of load_drugbank_index()
        gdsc_index:     output of load_gdsc_index()

    Returns:
        NetworkX Graph ready for querying
    """
    G = nx.Graph()

    # ── 1. Add all Drug nodes from DrugBank ───────────────────────
    logger.info("Building knowledge graph — adding DrugBank nodes...")
    for key, drug in drugbank_index.items():
        drug_name = drug["drug_name"]

        # Get IC50 from GDSC if available
        gdsc_entry = gdsc_index.get(key) or gdsc_index.get(drug_name.upper())
        mean_ic50  = gdsc_entry["mean_ic50"] if gdsc_entry else None
        mean_auc   = gdsc_entry["mean_auc"]  if gdsc_entry else None

        G.add_node(
            drug_name,
            type      = "drug",
            drug_id   = drug["drug_id"],
            mechanism = drug["mechanism"],
            mean_ic50 = mean_ic50,
            mean_auc  = mean_auc
        )

        # ── Drug → Gene edges ─────────────────────────────────────
        for gene in drug["targets"]:
            if not gene:
                continue
            # Add gene node if not exists
            if gene not in G:
                G.add_node(gene, type="gene")
            G.add_edge(drug_name, gene, relation="targets")

        # ── Drug → Pathway edges (DrugBank) ───────────────────────
        for pathway in drug["pathways"]:
            if not pathway:
                continue
            if pathway not in G:
                G.add_node(pathway, type="pathway")
            G.add_edge(drug_name, pathway, relation="affects")

    # ── 2. Add GDSC pathway edges (fills gaps DrugBank misses) ────
    logger.info("Adding GDSC pathway edges...")
    for key, gdsc_drug in gdsc_index.items():
        drug_name = gdsc_drug["drug_name"]
        pathway   = gdsc_drug.get("pathway")

        if not pathway or pathway == "Unknown":
            continue

        # Drug node may already exist from DrugBank or needs adding
        if drug_name not in G:
            G.add_node(
                drug_name,
                type      = "drug",
                drug_id   = "",
                mechanism = "",
                mean_ic50 = gdsc_drug.get("mean_ic50"),
                mean_auc  = gdsc_drug.get("mean_auc")
            )

        if pathway not in G:
            G.add_node(pathway, type="pathway")

        if not G.has_edge(drug_name, pathway):
            G.add_edge(drug_name, pathway, relation="affects")

        # ── GDSC gene targets ─────────────────────────────────────
        for gene in gdsc_drug.get("targets", []):
            if not gene:
                continue
            if gene not in G:
                G.add_node(gene, type="gene")
            if not G.has_edge(drug_name, gene):
                G.add_edge(drug_name, gene, relation="targets")

    # ── 3. Log summary ────────────────────────────────────────────
    drug_nodes    = [n for n, d in G.nodes(data=True) if d.get("type") == "drug"]
    gene_nodes    = [n for n, d in G.nodes(data=True) if d.get("type") == "gene"]
    pathway_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "pathway"]

    logger.info(
        f"Knowledge graph built: "
        f"{len(drug_nodes)} drugs | "
        f"{len(gene_nodes)} genes | "
        f"{len(pathway_nodes)} pathways | "
        f"{G.number_of_edges()} edges"
    )

    return G


def get_drug_neighbors(G: nx.Graph, drug_name: str) -> Dict:
    """
    Get all genes and pathways connected to a drug node.
    Used by scoring engine to compute coverage and overlap.

    Returns:
        { 'genes': [...], 'pathways': [...] }
    """
    if drug_name not in G:
        return {"genes": [], "pathways": []}

    genes    = []
    pathways = []

    for neighbor in G.neighbors(drug_name):
        node_type = G.nodes[neighbor].get("type")
        if node_type == "gene":
            genes.append(neighbor)
        elif node_type == "pathway":
            pathways.append(neighbor)

    return {"genes": genes, "pathways": pathways}


def query_candidates(
    G: nx.Graph,
    core_genes: list,
    dysregulated_pathways: list,
    resistant_drug: str
) -> list:
    """
    Find all drug nodes connected to any core gene or dysregulated pathway.
    This is the candidate selection step.

    Args:
        G:                     the knowledge graph
        core_genes:            resistance genes from GC-PGE
        dysregulated_pathways: standard pathway names from pathway_mapper
        resistant_drug:        exclude this drug from candidates

    Returns:
        List of candidate drug names
    """
    candidates = set()
    resistant_upper = resistant_drug.upper()

    # ── Find drugs connected to core genes ────────────────────────
    for gene in core_genes:
        if gene not in G:
            logger.warning(f"Gene '{gene}' not found in graph — will try DGIdb fallback")
            continue
        for neighbor in G.neighbors(gene):
            if G.nodes[neighbor].get("type") == "drug":
                candidates.add(neighbor)

    # ── Find drugs connected to dysregulated pathways ─────────────
    for pathway in dysregulated_pathways:
        if pathway not in G:
            logger.warning(f"Pathway '{pathway}' not found in graph")
            continue
        for neighbor in G.neighbors(pathway):
            if G.nodes[neighbor].get("type") == "drug":
                candidates.add(neighbor)

    # ── Remove the resistant drug itself ──────────────────────────
    candidates = {
        c for c in candidates
        if c.upper() != resistant_upper
    }

    logger.info(f"Candidate drugs found: {len(candidates)}")
    return list(candidates)


def load_graph_from_indexes(data_dir: str) -> nx.Graph:
    """
    Convenience: load both indexes and build graph in one call.
    Used in setup_data.py and app startup.
    """
    from backend.adrs.db_parser import load_drugbank_index, load_gdsc_index

    data_path      = Path(data_dir)
    drugbank_index = load_drugbank_index(str(data_path / "drugbank_index.json"))
    gdsc_index     = load_gdsc_index(str(data_path / "gdsc_index.json"))

    return build_knowledge_graph(drugbank_index, gdsc_index)