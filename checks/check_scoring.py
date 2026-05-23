import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from backend.adrs_old.graph_builder import load_graph_from_indexes, query_candidates
from backend.adrs_old.normalizer import normalize_delta_e
from backend.adrs_old.pathway_mapper import get_standard_pathways
from backend.adrs_old.scoring import (
    compute_reversal_score,
    compute_pathway_coverage,
    compute_gene_overlap,
    compute_sd_score
)
from backend.adrs_old.db_parser import load_gdsc_index
import json

# ── Load everything ───────────────────────────────────────────────
print("Loading graph and indexes...")
G          = load_graph_from_indexes("backend/adrs/data")
gdsc_index = load_gdsc_index("backend/adrs/data/gdsc_index.json")

with open("backend/adrs/tests/mock_gcpge_output.json") as f:
    mock = json.load(f)

# ── Run pipeline up to candidates ────────────────────────────────
delta_e_norm = normalize_delta_e(mock["delta_e"])
pathways     = get_standard_pathways(delta_e_norm, threshold=0.5)
candidates   = query_candidates(G, mock["core_genes"], pathways, mock["resistant_drug"])

print(f"Candidates: {len(candidates)}")

# ── Build IC50 lookup for all candidates ─────────────────────────
all_ic50s = {}
for drug in candidates:
    entry = gdsc_index.get(drug.upper())
    all_ic50s[drug] = entry["mean_ic50"] if entry else None

# ── Score 3 specific drugs ────────────────────────────────────────
test_drugs = [c for c in candidates if c in ["Dacomitinib", "Afatinib", "AZD2014", "Wortmannin", candidates[0]]]
test_drugs = test_drugs[:3] if len(test_drugs) >= 3 else candidates[:3]

print(f"\nScoring {len(test_drugs)} drugs:")
for drug in test_drugs:
    reversal  = compute_reversal_score(drug, gdsc_index, all_ic50s)
    coverage  = compute_pathway_coverage(drug, pathways, G)
    overlap   = compute_gene_overlap(drug, mock["core_genes"], G)
    result    = compute_sd_score(
        drug, reversal, coverage, overlap,
        mock["core_genes"], pathways, G, gdsc_index
    )
    print(f"\n  {drug}:")
    print(f"    SD={result['sd_score']} | R={result['reversal_score']} | C={result['pathway_coverage']} | G={result['gene_overlap']}")
    print(f"    Targets: {result['targeted_genes']}")
    print(f"    Pathways: {result['targeted_pathways']}")
    print(f"    Weights: {result['weights_used']}")

# ── Assertions ────────────────────────────────────────────────────
drug      = candidates[0]
reversal  = compute_reversal_score(drug, gdsc_index, all_ic50s)
assert 0.0 <= reversal <= 1.0, "Reversal must be in [0,1]"

coverage = compute_pathway_coverage(drug, pathways, G)
assert 0.0 <= coverage <= 1.0, "Coverage must be in [0,1]"

overlap = compute_gene_overlap(drug, mock["core_genes"], G)
assert 0.0 <= overlap <= 1.0, "Overlap must be in [0,1]"

print("\nAll scoring tests passed")