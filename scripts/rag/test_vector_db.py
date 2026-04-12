"""
test_vector_db.py

This script connects to the already-built persistent Chroma database on your hard drive 
and performs a sample search query to verify retrieval accuracy and speed.
"""

import os
import logging
import torch

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# --- CRITICAL: Suppress ChromaDB Telemetry Warnings ---
os.environ["CHROMA_TELEMETRY_IMPL"] = "None"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

# --- Path Resolution ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))
VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "data", "vector_store")

def test_database():
    """Connects to the database and runs a sample query."""
    
    # 1. Verify the database actually exists on the hard drive
    if not os.path.exists(VECTOR_DB_DIR):
        print(f"❌ ERROR: Could not find database at {VECTOR_DB_DIR}")
        print("Did you run build_vector_db.py first?")
        return

    # 2. Hardware Detection
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Hardware detected: Using {device.upper()}")

    # 3. Load the EXACT SAME embedding model used to build the DB
    print("[*] Loading BGE-Small Embedding Model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': device}, 
        encode_kwargs={'normalize_embeddings': True}
    )

    # 4. Connect to the existing database
    # Note: We use Chroma() here, NOT Chroma.from_documents()
    print(f"[*] Connecting to database at: {VECTOR_DB_DIR}")
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR, 
        embedding_function=embeddings
    )
    print("✅ Database connected successfully!\n")

    # 5. Execute the Test Search
    query = "How does lactate influence immune resistance?"
    print(f"🔍 Searching for: '{query}'")
    print("-" * 50)

    # Retrieve the top 3 most relevant chunks
    results = vectorstore.similarity_search(query, k=3)

    if not results:
        print("⚠️ No results found. The database might be empty.")
    else:
        for i, res in enumerate(results):
            print(f"\n🎯 MATCH {i+1}:")
            print(f"Title:  {res.metadata.get('title', 'Unknown Title')}")
            print(f"PMID:   {res.metadata.get('pmid', 'Unknown PMID')}")
            # Print just the first 300 characters of the content so it doesn't flood the terminal
            print(f"Excerpt: {res.page_content[:300]}...")
            print("-" * 50)

if __name__ == "__main__":
    test_database()