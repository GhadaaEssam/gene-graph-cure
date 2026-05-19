import requests
import pandas as pd
import numpy as np
from backend.adrs.gcpge_adapter import translate_gcpge_to_adrs, PATHWAY_NAMES

# Verify pw_id loaded correctly
print(f"Pathway names loaded: {len(PATHWAY_NAMES)}")
print(f"First 3: {PATHWAY_NAMES[:3]}")
print(f"Index 8 (EGFR): {PATHWAY_NAMES[8]}")
print(f"Index 163 (MAPK): {PATHWAY_NAMES[163]}")

# Load REAL pw_w from the liver cancer results
# (use the CSV file values as a realistic simulation)
pw_w_df = pd.read_csv(
    "backend/adrs/data/pw_id.csv"
)  # just to get count — we simulate weights
np.random.seed(42)
pw_w_simulated = np.random.uniform(0.15, 0.30, 3090).tolist()
# Spike a few cancer-relevant pathways high
pw_w_simulated[163] = 0.85   # REACTOME_MAPK3_ERK1_ACTIVATION
pw_w_simulated[219] = 0.78   # REACTOME_CONSTITUTIVE_SIGNALING_BY_LIGAND_RESPONSIVE_EGFR
pw_w_simulated[196] = 0.72   # REACTOME_MAPK1_ERK2_ACTIVATION
pw_w_simulated[3043] = 0.69  # PID_PI3KCI_AKT_PATHWAY

# Simulates the UPDATED /predict response (new structured fields)
mock_gcpge_response = {
    # ── Debug fields (not used by ADRS) ───────────────────────────
    "loss_mutiGAT": 0.023,
    "loss_L1":      0.004,
    "out":          [1, 0, 1],
    "temp":         [[0.1]],
    "graph":        [[0.1, 0.8], [0.4, 0.2]],
    "pw_w":         [0.82, 0.61, 0.45] + [0.20] * 3087,  # still present
    "vimp_g":       [0.95, 0.88, 0.45, 0.30, 0.12],      # still present

    # ── NEW structured fields (used by updated adapter) ───────────
    "structured_core_pathways": [
        {"index": 8,   "name": "BIOCARTA_EGFR_SMRTE_PATHWAY",    "weight": 0.82},
        {"index": 219, "name": "REACTOME_PI3K_AKT_SIGNALING",     "weight": 0.61},
        {"index": 163, "name": "REACTOME_MAPK3_ERK1_ACTIVATION",  "weight": 0.45},
        {"index": 42,  "name": "BIOCARTA_CELL_CYCLE_PATHWAY",     "weight": 0.30},
        {"index": 77,  "name": "BIOCARTA_APOPTOSIS_PATHWAY",      "weight": 0.20},
    ],
    "structured_core_genes": [
        {"index": 12, "name": "EGFR",   "score": 0.95, "correlation": 0.84, "is_anchor": True},
        {"index": 33, "name": "KRAS",   "score": 0.88, "correlation": 0.79, "is_anchor": True},
        {"index": 7,  "name": "TP53",   "score": 0.72, "correlation": 0.65, "is_anchor": True},
        {"index": 91, "name": "PIK3CA", "score": 0.61, "correlation": 0.58, "is_anchor": False},
        {"index": 44, "name": "BRAF",   "score": 0.45, "correlation": 0.40, "is_anchor": False},
    ],
    "core_genes":    ["EGFR", "KRAS", "TP53", "PIK3CA", "BRAF"],
    "core_pathways": [
        "BIOCARTA_EGFR_SMRTE_PATHWAY",
        "REACTOME_PI3K_AKT_SIGNALING",
        "REACTOME_MAPK3_ERK1_ACTIVATION"
    ]
}

anchor_genes = ["EGFR", "KRAS", "TP53", "PIK3CA", "MAP3K7", "BRAF", "MET"]

print("\nTranslating GC-PGE response...")
adrs_input = translate_gcpge_to_adrs(
    gcpge_response = mock_gcpge_response,
    anchor_genes   = anchor_genes,
    patient_id     = "liver_patient_final_test",
    resistant_drug = "Sorafenib",
    top_n_drugs    = 5,
    top_n_pathways = 30
)

print(f"\nTop 5 pathways by ΔE score:")
top5_pw = sorted(adrs_input["delta_e"].items(), key=lambda x: -x[1])[:5]
for name, score in top5_pw:
    print(f"  {score:.4f}  {name}")

print(f"\nCore genes: {adrs_input['core_genes']}")

print("\nCalling ADRS endpoint...")
resp = requests.post(
    "http://127.0.0.1:8001/api/v1/adrs/recommend",
    json=adrs_input
)

assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
data = resp.json()

print(f"\n{'='*55}")
print(f"TOP 5 ALTERNATIVE DRUGS — Patient: {data['patient_id']}")
print(f"Resistant to: {data['resistant_drug']}")
print(f"{'='*55}")
print(f"{'#':<4}{'Drug':<26}{'SD':>7}{'R':>7}{'C':>7}{'G':>7}")
print(f"{'-'*55}")
for i, drug in enumerate(data["recommendations"], 1):
    print(
        f"{i:<4}{drug['drug_name']:<26}"
        f"{drug['sd_score']:>7.4f}"
        f"{drug['reversal_score']:>7.4f}"
        f"{drug['pathway_coverage']:>7.4f}"
        f"{drug['gene_overlap']:>7.4f}"
    )

print(f"\nLLM summary: {data['llm_context']['patient_summary']}")
print(f"Gene hits:   {data['llm_context']['gene_hit_summary']}")
print(f"\nTotal candidates scored: {data['meta']['total_candidates']}")
print(f"Pathways used: {data['meta']['dysregulated_pathways'][:3]}...")
print(f"\nAll final tests passed ✓")