import os
import json
import time
from urllib.error import HTTPError
from Bio import Entrez

# --- Configuration ---
# NCBI requires an email to avoid IP bans
Entrez.email = "cds.shahdhassan23794@alexu.edu.eg"  

# Path Resolution: Automatically saves to your protected data folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw_documents")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pubmed_foundation.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Core Functions ---
def fetch_pubmed_data(query: str, max_papers: int) -> list:
    """Searches PubMed and downloads abstracts as a JSON-ready list."""
    print(f"[*] Step 1: Searching PubMed for up to {max_papers} papers...")
    
    try:
        search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_papers)
        search_results = Entrez.read(search_handle)
        search_handle.close()
    except HTTPError as e:
        print(f"[!] Network error during search: {e}")
        return []

    pmid_list = search_results.get("IdList", [])
    total_found = len(pmid_list)
    print(f"[*] Found {total_found} relevant papers. Starting download in batches...")

    papers_dataset = []
    batch_size = 100 

    # Step 2: Fetch the actual text for the IDs
    for i in range(0, total_found, batch_size):
        batch_ids = pmid_list[i : i + batch_size]
        print(f"    -> Fetching batch {i} to {i + len(batch_ids)}...")
        
        try:
            fetch_handle = Entrez.efetch(db="pubmed", id=batch_ids, retmode="xml")
            records = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            # Step 3: Extract and clean the data
            for article in records.get('PubmedArticle', []):
                try:
                    medline = article['MedlineCitation']
                    pmid = medline['PMID']
                    title = medline['Article']['ArticleTitle']
                    
                    abstract_list = medline['Article'].get('Abstract', {}).get('AbstractText', [])
                    abstract_text = " ".join([str(text) for text in abstract_list])
                    
                    if abstract_text.strip():
                        papers_dataset.append({
                            "id": str(pmid),
                            "title": str(title),
                            "content": abstract_text,
                            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })
                except KeyError:
                    continue
                    
        except HTTPError as e:
            print(f"[!] Error fetching batch: {e}. Skipping...")
            
        # Mandatory pause to respect NCBI server limits
        time.sleep(1.5)

    return papers_dataset

# --- Execution ---
if __name__ == "__main__":
    # The optimized query from your notebook tests
    PROJECT_QUERY = """
    ("Drug Resistance, Neoplasm"[MeSH Terms] OR "drug resistance"[Title/Abstract] OR "chemoresistance"[Title/Abstract] OR "therapy resistance"[Title/Abstract] OR "treatment failure"[Title/Abstract] OR "drug sensitivity"[Title/Abstract]) 
    AND 
    ("sorafenib"[Title/Abstract] OR "cisplatin"[Title/Abstract] OR "immunotherapy"[Title/Abstract] OR "immune checkpoint inhibitor*"[Title/Abstract] OR "PD-1"[Title/Abstract] OR "PD-L1"[Title/Abstract] OR "CTLA-4"[Title/Abstract]) 
    AND 
    ("Carcinoma, Hepatocellular"[MeSH Terms] OR "liver cancer"[Title/Abstract] OR "hepatocellular carcinoma"[Title/Abstract] OR "HCC"[Title/Abstract] OR "Ovarian Neoplasms"[MeSH Terms] OR "ovarian cancer"[Title/Abstract] OR "ovarian carcinoma"[Title/Abstract] OR "Melanoma"[MeSH Terms]) 
    AND 
    ("Gene Expression"[MeSH Terms] OR "Gene Expression Profiling"[MeSH Terms] OR "mRNA"[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "transcriptom*"[Title/Abstract] OR "signaling pathway*"[Title/Abstract] OR "gene signature"[Title/Abstract] OR "biomarker"[Title/Abstract] OR "core gene*"[Title/Abstract])
    """
    
    # Set to 5000 to safely capture all ~2000 results
    final_data = fetch_pubmed_data(PROJECT_QUERY, max_papers=5000)
    
    # Save the data
    if final_data:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(final_data, file, indent=4)
        print(f"\n[+] Success! Saved {len(final_data)} high-quality abstracts to:")
        print(f"    {OUTPUT_FILE}")
    else:
        print("\n[-] No data was retrieved. Check your internet connection.")