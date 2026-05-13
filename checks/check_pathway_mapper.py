from backend.adrs_old.normalizer import normalize_delta_e
from backend.adrs_old.pathway_mapper import get_standard_pathways, extract_dysregulated_pathways
import json

# Load mock input
with open("backend/adrs/tests/mock_gcpge_output.json") as f:
    mock = json.load(f)

# Step 1: normalize
delta_e_norm = normalize_delta_e(mock["delta_e"])
print("Normalized ΔE:", delta_e_norm)

# Step 2: extract dysregulated (threshold 0.5)
dysregulated = extract_dysregulated_pathways(delta_e_norm, threshold=0.5)
print("\nDysregulated pathways:", dysregulated)

# Step 3: map to standard names
standard = get_standard_pathways(delta_e_norm, threshold=0.5)
print("\nStandard names:", standard)

# Assertions
assert len(standard) > 0, "Should have at least 1 dysregulated pathway"
assert "EGFR signaling" in standard, "EGFR signaling should be in results"
assert "PI3K/MTOR signaling" in standard, "PI3K should be in results"
assert "Apoptosis regulation" not in standard, "Apoptosis score=0.0 should be filtered out"

print("\nAll pathway mapper tests passed")