import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from backend.adrs_old.graph_builder import load_graph_from_indexes, get_drug_neighbors, query_candidates
from backend.adrs_old.normalizer import normalize_delta_e
from backend.adrs_old.pathway_mapper import get_standard_pathways
import json

print("Building graph (takes ~30 seconds)...")
G = load_graph_from_indexes("backend/adrs/data")

# Basic size checks
drug_nodes    = [n for n, d in G.nodes(data=True) if d.get("type") == "drug"]
gene_nodes    = [n for n, d in G.nodes(data=True) if d.get("type") == "gene"]
pathway_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "pathway"]

print(f"\nGraph size:")
print(f"  Drugs:    {len(drug_nodes)}")
print(f"  Genes:    {len(gene_nodes)}")
print(f"  Pathways: {len(pathway_nodes)}")
print(f"  Edges:    {G.number_of_edges()}")

assert len(drug_nodes) > 5000,    "Expected 5000+ drug nodes"
assert len(gene_nodes) > 100,     "Expected 100+ gene nodes"
assert len(pathway_nodes) > 10,   "Expected 10+ pathway nodes"
assert G.number_of_edges() > 1000,"Expected 1000+ edges"

# Check Erlotinib neighbors
neighbors = get_drug_neighbors(G, "Erlotinib")
print(f"\nErlotinib neighbors:")
print(f"  Genes:    {neighbors['genes']}")
print(f"  Pathways: {neighbors['pathways']}")
assert "EGFR" in neighbors["genes"], "Erlotinib should target EGFR"

# Full pipeline test with mock input
with open("backend/adrs/tests/mock_gcpge_output.json") as f:
    mock = json.load(f)

delta_e_norm = normalize_delta_e(mock["delta_e"])
pathways     = get_standard_pathways(delta_e_norm, threshold=0.5)
candidates   = query_candidates(G, mock["core_genes"], pathways, mock["resistant_drug"])

print(f"\nCandidate drugs for test patient: {len(candidates)}")
print(f"  First 5: {candidates[:5]}")
assert len(candidates) >= 3, "Expected at least 3 candidate drugs"
assert "Erlotinib" not in candidates, "Resistant drug must be excluded"

print("\nAll graph tests passed")