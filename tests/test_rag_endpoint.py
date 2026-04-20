import os
import requests
import json

# 1. Point to your local FastAPI server
url = "http://localhost:8000/predict"

# 2. Dynamically build the absolute path to the data folder
# This finds the 'tests' folder, goes up one level, and goes into 'data/model_outputs'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "model_outputs")

print("Loading files...")
# 3. Use the dynamic DATA_DIR for all files
files = {
    "geo_features": open(os.path.join(DATA_DIR, "1_Hepatocellular carcinoma sorafenib resistance result_test_rank.csv"), "rb"),
    "anchor_genes": open(os.path.join(DATA_DIR, "2_pubmed_result.csv"), "rb"),
    "node_features": open(os.path.join(DATA_DIR, "3_data_x_all.csv"), "rb"),
    "ppi_edges": open(os.path.join(DATA_DIR, "4_ppi_link_hcc_sorafineb_400.csv"), "rb"),
    "homolog_edges": open(os.path.join(DATA_DIR, "5_homolog_hepatocellular carcinoma sorafenib.csv"), "rb"),
}

try:
    print("Sending request to /predict endpoint...")
    response = requests.post(url, files=files)

    if response.status_code == 200:
        print("\n✅ --- PREDICTION SUCCESSFUL ---")
        data = response.json()
        
        # Check standard model outputs
        print(f"Top 3 Model Predictions (out): {data['out'][:3]}")
        print(f"Total Genes Scored (vimp_g): {len(data['vimp_g'])}")
        
        # --- TEST THE RAG INTEGRATION ---
        print("\n🔍 --- RAG EVIDENCE RETRIEVED ---")
        evidence_list = data.get("rag_evidence", [])
        
        if not evidence_list:
            print("⚠️ No RAG evidence returned. Check server logs.")
        else:
            for i, paper in enumerate(evidence_list):
                print(f"\nPaper {i+1}:")
                print(f"Title: {paper.get('title')}")
                print(f"PMID:  {paper.get('pmid')}")
                print(f"Excerpt: {paper.get('excerpt')}...")
                
        # Optional: Save full output to inspect later
        json_save_path = os.path.join(SCRIPT_DIR, "full_api_response.json")
        with open(json_save_path, "w") as f:
            json.dump(data, f, indent=4)
            print(f"\n📁 Saved full JSON response to {json_save_path}")

    else:
        print(f"\n❌ Error {response.status_code}: {response.text}")

finally:
    # Always close your files!
    for f in files.values():
        f.close()