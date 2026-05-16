import os
import json
import time
from typing import Iterable, List
from urllib.error import HTTPError
from Bio import Entrez

# --- Configuration ---
# NCBI requires an email to avoid IP bans
Entrez.email = os.environ.get("NCBI_EMAIL", "cds.shahdhassan23794@alexu.edu.eg")
Entrez.api_key = os.environ.get("NCBI_API_KEY")

# Path Resolution: Automatically saves to your protected data folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw_documents")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pubmed_foundation.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Query Design ---
RESISTANCE_TERMS = [
    '"Drug Resistance, Neoplasm"[MeSH Terms]',
    '"drug resistance"[Title/Abstract]',
    '"chemoresistance"[Title/Abstract]',
    '"therapy resistance"[Title/Abstract]',
    '"treatment resistance"[Title/Abstract]',
    '"treatment failure"[Title/Abstract]',
    '"drug sensitivity"[Title/Abstract]',
    '"therapy response"[Title/Abstract]',
    '"treatment response"[Title/Abstract]',
    '"predictive biomarker"[Title/Abstract]',
]

CANCER_TERMS = [
    '"Neoplasms"[MeSH Terms]',
    '"Carcinoma, Hepatocellular"[MeSH Terms]',
    '"hepatocellular carcinoma"[Title/Abstract]',
    '"liver cancer"[Title/Abstract]',
    '"HCC"[Title/Abstract]',
    '"Breast Neoplasms"[MeSH Terms]',
    '"breast cancer"[Title/Abstract]',
    '"BRCA"[Title/Abstract]',
    '"Ovarian Neoplasms"[MeSH Terms]',
    '"ovarian cancer"[Title/Abstract]',
    '"Melanoma"[MeSH Terms]',
    '"melanoma"[Title/Abstract]',
    '"Lung Neoplasms"[MeSH Terms]',
    '"lung cancer"[Title/Abstract]',
    '"non-small cell lung cancer"[Title/Abstract]',
    '"NSCLC"[Title/Abstract]',
    '"Colorectal Neoplasms"[MeSH Terms]',
    '"colorectal cancer"[Title/Abstract]',
]

DRUG_TERMS = [
    '"sorafenib"[Title/Abstract]',
    '"cisplatin"[Title/Abstract]',
    '"carboplatin"[Title/Abstract]',
    '"paclitaxel"[Title/Abstract]',
    '"doxorubicin"[Title/Abstract]',
    '"tamoxifen"[Title/Abstract]',
    '"trastuzumab"[Title/Abstract]',
    '"olaparib"[Title/Abstract]',
    '"immunotherapy"[Title/Abstract]',
    '"immune checkpoint inhibitor*"[Title/Abstract]',
    '"PD-1"[Title/Abstract]',
    '"PD-L1"[Title/Abstract]',
    '"CTLA-4"[Title/Abstract]',
    '"anti-PD-1"[Title/Abstract]',
    '"anti-PD-L1"[Title/Abstract]',
]

MOLECULAR_TERMS = [
    '"Gene Expression"[MeSH Terms]',
    '"Gene Expression Profiling"[MeSH Terms]',
    '"mRNA"[Title/Abstract]',
    '"RNA-seq"[Title/Abstract]',
    '"RNA sequencing"[Title/Abstract]',
    '"transcriptom*"[Title/Abstract]',
    '"gene signature"[Title/Abstract]',
    '"biomarker"[Title/Abstract]',
    '"core gene*"[Title/Abstract]',
    '"signaling pathway*"[Title/Abstract]',
    '"pathway activation"[Title/Abstract]',
    '"pathway enrichment"[Title/Abstract]',
    '"network analysis"[Title/Abstract]',
]

MULTIOMICS_TERMS = [
    '"multi-omics"[Title/Abstract]',
    '"multiomics"[Title/Abstract]',
    '"integrative omics"[Title/Abstract]',
    '"multi omics"[Title/Abstract]',
    '"genomics"[Title/Abstract]',
    '"epigenomics"[Title/Abstract]',
    '"DNA methylation"[Title/Abstract]',
    '"methylation"[Title/Abstract]',
    '"copy number variation"[Title/Abstract]',
    '"copy number alteration"[Title/Abstract]',
    '"CNV"[Title/Abstract]',
    '"SNV"[Title/Abstract]',
    '"single nucleotide variant"[Title/Abstract]',
    '"mutation profile"[Title/Abstract]',
    '"proteomics"[Title/Abstract]',
    '"metabolomics"[Title/Abstract]',
]

SEED_GENE_TERMS = [
    "TP53", "EGFR", "ERBB2", "BRCA1", "BRCA2", "PTEN", "PIK3CA",
    "KRAS", "BRAF", "MET", "VEGFA", "MYC", "CD274", "CTNNB1",
    "MTOR", "AKT1", "MAPK1", "ESR1", "ABCB1", "ALDH1A1",
]

SEED_PATHWAY_TERMS = [
    "MAPK signaling", "PI3K AKT mTOR", "p53 signaling", "Wnt beta catenin",
    "TGF beta signaling", "VEGF signaling", "EGFR signaling", "HER2 signaling",
    "JAK STAT signaling", "NF-kappaB signaling", "apoptosis", "DNA repair",
    "epithelial mesenchymal transition", "immune checkpoint", "hypoxia",
    "autophagy", "ABC transporters", "focal adhesion", "ECM receptor",
]


def _or_block(terms: Iterable[str]) -> str:
    return "(" + " OR ".join(terms) + ")"


def _title_abstract_terms(terms: Iterable[str]) -> List[str]:
    return [f'"{term}"[Title/Abstract]' for term in terms if str(term).strip()]


def build_project_query(
    cancer_terms: Iterable[str] = CANCER_TERMS,
    drug_terms: Iterable[str] = DRUG_TERMS,
    seed_gene_terms: Iterable[str] = SEED_GENE_TERMS,
    seed_pathway_terms: Iterable[str] = SEED_PATHWAY_TERMS,
) -> str:
    """
    Builds a high-recall PubMed foundation query for GC-PGE/RAG.

    Retrieval will later inject exact model genes/pathways. The foundation corpus
    should therefore be broad enough to contain cancer-drug resistance,
    transcriptomic/pathway, and multi-omics mechanism papers.
    """
    gene_block = _title_abstract_terms(seed_gene_terms)
    pathway_block = _title_abstract_terms(seed_pathway_terms)
    molecular_block = MOLECULAR_TERMS + MULTIOMICS_TERMS + gene_block + pathway_block

    query = " AND ".join([
        _or_block(RESISTANCE_TERMS),
        _or_block(cancer_terms),
        _or_block(drug_terms),
        _or_block(molecular_block),
        'hasabstract[text]',
        'english[lang]',
    ])
    return query


def _article_year(article: dict) -> str:
    journal_issue = article.get("Journal", {}).get("JournalIssue", {})
    pub_date = journal_issue.get("PubDate", {})
    return str(pub_date.get("Year", ""))


def _extract_mesh_terms(medline: dict) -> str:
    headings = medline.get("MeshHeadingList", [])
    terms = []
    for heading in headings:
        descriptor = heading.get("DescriptorName")
        if descriptor:
            terms.append(str(descriptor))
    return "; ".join(terms)


def _extract_keywords(medline: dict) -> str:
    keywords = []
    for keyword_list in medline.get("KeywordList", []):
        keywords.extend(str(keyword) for keyword in keyword_list)
    return "; ".join(keywords)


def _extract_publication_types(article: dict) -> str:
    publication_types = article.get("PublicationTypeList", [])
    return "; ".join(str(publication_type) for publication_type in publication_types)


# --- Core Functions ---
def fetch_pubmed_data(query: str, max_papers: int) -> list:
    """Searches PubMed and downloads abstracts as a JSON-ready list."""
    print(f"[*] Step 1: Searching PubMed for up to {max_papers} papers...")
    
    try:
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_papers,
            sort="relevance"
        )
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
                    article_data = medline['Article']
                    pmid = str(medline['PMID'])
                    title = str(article_data['ArticleTitle'])
                    
                    abstract_list = article_data.get('Abstract', {}).get('AbstractText', [])
                    abstract_text = " ".join([str(text) for text in abstract_list])
                    
                    if abstract_text.strip():
                        papers_dataset.append({
                            "id": pmid,
                            "title": title,
                            "abstract": abstract_text,
                            "content": f"Title: {title}\nAbstract: {abstract_text}",
                            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            "journal": str(article_data.get("Journal", {}).get("Title", "")),
                            "year": _article_year(article_data),
                            "publication_types": _extract_publication_types(article_data),
                            "mesh_terms": _extract_mesh_terms(medline),
                            "keywords": _extract_keywords(medline),
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
    PROJECT_QUERY = build_project_query()
    print("[*] Foundation query:")
    print(PROJECT_QUERY)
    
    max_papers = int(os.environ.get("PUBMED_MAX_PAPERS", "5000"))
    final_data = fetch_pubmed_data(PROJECT_QUERY, max_papers=max_papers)
    
    # Save the data
    if final_data:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(final_data, file, indent=4)
        print(f"\n[+] Success! Saved {len(final_data)} high-quality abstracts to:")
        print(f"    {OUTPUT_FILE}")
    else:
        print("\n[-] No data was retrieved. Check your internet connection.")
