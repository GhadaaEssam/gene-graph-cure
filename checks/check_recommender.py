import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from backend.adrs.graph_builder import load_graph_from_indexes
from backend.adrs.db_parser import load_gdsc_index
from backend.adrs.recommender import rank_drugs
import json

print("Loading graph and indexes...")
G          = load_graph_from_indexes("backend/adrs/data")
gdsc_index = load_gdsc_index("backend/adrs/data/gdsc_index.json")

with open("backend/adrs/tests/mock_gcpge_output.json") as f:
    mock = json.load(f)

print("\nRunning full ADRS pipeline...")
result = rank_drugs(
    G             = G,
    gdsc_index    = gdsc_index,
    delta_e       = mock["delta_e"],
    core_genes    = mock["core_genes"],
    resistant_drug= mock["resistant_drug"],
    top_n         = 5
)

# ── Print results ─────────────────────────────────────────────────
print(f"\nTop 5 recommendations for patient resistant to {mock['resistant_drug']}:")
print(f"{'Rank':<6}{'Drug':<25}{'SD':>6}{'R':>6}{'C':>6}{'G':>6}")
print("-" * 55)
for i, drug in enumerate(result["recommendations"], 1):
    print(
        f"{i:<6}{drug['drug_name']:<25}"
        f"{drug['sd_score']:>6}"
        f"{drug['reversal_score']:>6}"
        f"{drug['pathway_coverage']:>6}"
        f"{drug['gene_overlap']:>6}"
    )

print(f"\nLLM Context:")
print(f"  Patient summary: {result['llm_context']['patient_summary']}")
print(f"  Gene hits: {result['llm_context']['gene_hit_summary']}")

print(f"\nMeta:")
print(f"  Total candidates scored: {result['meta']['total_candidates']}")
print(f"  Dysregulated pathways:   {result['meta']['dysregulated_pathways']}")

# ── Assertions ────────────────────────────────────────────────────
assert len(result["recommendations"]) == 5, "Must return exactly 5 drugs"
assert result["llm_context"] is not None,   "LLM context must exist"

scores = [d["sd_score"] for d in result["recommendations"]]
assert scores == sorted(scores, reverse=True), "Must be sorted descending"

names = [d["drug_name"] for d in result["recommendations"]]
assert mock["resistant_drug"] not in names, "Resistant drug must not appear"

for drug in result["recommendations"]:
    assert 0.0 <= drug["sd_score"] <= 1.0,       "SD score out of range"
    assert 0.0 <= drug["reversal_score"] <= 1.0,  "Reversal out of range"
    assert 0.0 <= drug["pathway_coverage"] <= 1.0,"Coverage out of range"
    assert 0.0 <= drug["gene_overlap"] <= 1.0,    "Overlap out of range"

print("\nAll recommender tests passed")