from backend.adrs_old.models import ADRSRequest, ADRSResponse, DrugRecommendation, ErrorResponse
from datetime import datetime

# Test 1 — valid request
req = ADRSRequest(
    patient_id     = "patient_001",
    resistant_drug = "Erlotinib",
    delta_e        = {"EGFR signaling": 0.82, "PI3K/MTOR signaling": 0.61},
    core_genes     = ["EGFR", "KRAS"],
    top_n          = 5,
    threshold      = 0.5
)
print("Request valid:", req.patient_id, req.resistant_drug)
assert req.top_n == 5
assert req.threshold == 0.5

# Test 2 — drug recommendation
drug = DrugRecommendation(
    drug_name           = "Osimertinib",
    sd_score            = 0.6135,
    reversal_score      = 0.9712,
    pathway_coverage    = 0.5,
    gene_overlap        = 0.25,
    weights_used        = "standard (0.4R + 0.3C + 0.3G)",
    targeted_genes      = ["EGFR"],
    targeted_pathways   = ["EGFR signaling"],
    mechanism_of_action = "Inhibits EGFR tyrosine kinase",
    mean_ic50_uM        = 0.012
)
print("Drug valid:", drug.drug_name, drug.sd_score)
assert 0.0 <= drug.sd_score <= 1.0

# Test 3 — full response
resp = ADRSResponse(
    patient_id      = "patient_001",
    resistant_drug  = "Erlotinib",
    recommendations = [drug],
    cached          = False
)
print("Response valid:", resp.patient_id, "cached=", resp.cached)
assert resp.timestamp is not None

# Test 4 — error response
err = ErrorResponse(
    error = "No suitable alternative drugs found.",
    code  = "NO_PATHWAY_MATCH"
)
print("Error valid:", err.code)
assert err.code == "NO_PATHWAY_MATCH"

# Test 5 — JSON serialization works
json_out = resp.model_dump_json()
assert "Osimertinib" in json_out
print("JSON serialization works")

print("\nAll model tests passed")