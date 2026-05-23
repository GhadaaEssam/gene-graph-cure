"""
Final API test — run this after starting the server with:
    uvicorn main:app --reload --port 8001
"""
import requests

BASE = "http://127.0.0.1:8001/api/v1"   # ADRS is on port 8001

# ── Test 1: Health check ──────────────────────────────────────────
print("Test 1 — Health check...")
resp = requests.get(f"{BASE}/adrs/health")
assert resp.status_code == 200, f"Health check failed: {resp.text}"
data = resp.json()
print(f"  Status:           {data['status']}")
print(f"  Drugs loaded:     {data['drugs_loaded']}")
print(f"  Genes loaded:     {data['genes_loaded']}")
print(f"  Pathways loaded:  {data['pathways_loaded']}")
print(f"  Graph edges:      {data['graph_edges']}")
print(f"  DB cache:         {data['db_cache']}")
assert data["status"] == "ok"
assert data["drugs_loaded"] > 5000

# ── Test 2: Recommendation endpoint ──────────────────────────────
print("\nTest 2 — Recommendation endpoint (EGFR-resistant patient)...")
payload = {
    "patient_id":     "test_patient_final",
    "resistant_drug": "Erlotinib",
    "delta_e": {
        "EGFR signaling":       0.82,
        "PI3K/MTOR signaling":  0.61,
        "ERK MAPK signaling":   0.45,
        "Cell cycle":           0.30,
        "Apoptosis regulation": 0.20
    },
    "core_genes": ["EGFR", "KRAS", "TP53", "PIK3CA"],
    "top_n":      5,
    "threshold":  0.5
}

resp = requests.post(f"{BASE}/adrs/recommend", json=payload)
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
data = resp.json()

print(f"\n  {'='*55}")
print(f"  Patient:      {data['patient_id']}")
print(f"  Resistant to: {data['resistant_drug']}")
print(f"  Cached:       {data['cached']}")
print(f"  {'='*55}")
print(f"  {'#':<4}{'Drug':<26}{'SD':>7}{'R':>7}{'C':>7}{'G':>7}")
print(f"  {'-'*55}")
for i, drug in enumerate(data["recommendations"], 1):
    print(
        f"  {i:<4}{drug['drug_name']:<26}"
        f"{drug['sd_score']:>7.4f}"
        f"{drug['reversal_score']:>7.4f}"
        f"{drug['pathway_coverage']:>7.4f}"
        f"{drug['gene_overlap']:>7.4f}"
    )

print(f"\n  LLM summary: {data['llm_context']['patient_summary']}")
print(f"  Gene hits:   {data['llm_context']['gene_hit_summary']}")

# Assertions
assert len(data["recommendations"]) == 5,          "Must return 5 drugs"
assert "Erlotinib" not in [d["drug_name"] for d in data["recommendations"]], \
    "Resistant drug must not appear in results"
scores = [d["sd_score"] for d in data["recommendations"]]
assert scores == sorted(scores, reverse=True),     "Must be sorted descending"
assert data["llm_context"] is not None,            "LLM context must exist"

# ── Test 3: Cache test (call same patient again) ──────────────────
print("\nTest 3 — Cache test (same patient, second call)...")
resp2 = requests.post(f"{BASE}/adrs/recommend", json=payload)
assert resp2.status_code == 200
data2 = resp2.json()
if data2["cached"]:
    print("  ✓ Result returned from cache (DB connected)")
else:
    print("  ℹ  Result recomputed (DB not connected — expected without PostgreSQL)")

# Verify results are identical
assert [d["drug_name"] for d in data["recommendations"]] == \
       [d["drug_name"] for d in data2["recommendations"]], \
    "Cached and fresh results must match"

print("\n✓ All API tests passed")
print(f"  Server: {BASE}")
print(f"  Docs:   http://127.0.0.1:8001/docs")