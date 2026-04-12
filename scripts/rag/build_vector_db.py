"""
build_vector_db.py

This script processes raw medical abstracts, splits them into manageable text chunks, 
generates dense vector embeddings using a HuggingFace model, and stores them in a 
persistent ChromaDB database for rapid semantic retrieval.

It dynamically detects hardware to utilize GPU acceleration via PyTorch if available.
"""

import os
import json
import shutil
import logging
import torch

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# --- System Configuration ---
# Suppress ChromaDB telemetry to ensure clean terminal output and avoid background thread errors
os.environ["CHROMA_TELEMETRY_IMPL"] = "None"
os.environ["ANONYMIZED_TELEMETRY"] = "False"
logging.getLogger("chromadb.telemetry.posthog").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

# --- Directory Configuration ---
# Dynamically resolve absolute paths relative to this script's location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))

INPUT_JSON = os.path.join(PROJECT_ROOT, "data", "raw_documents", "pubmed_foundation.json")
VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "data", "vector_store")


def load_and_process_data(json_path: str) -> list:
    """
    Reads the JSON file containing medical abstracts and converts them into 
    LangChain Document objects with appropriate metadata.
    """
    print("[*] Step 1: Loading JSON data...")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Source file not found at: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    documents = []
    for item in raw_data:
        doc = Document(
            page_content=item["content"],
            metadata={
                "title": item["title"],
                "source": item["source_url"],
                "pmid": item["id"]
            }
        )
        documents.append(doc)
    
    print(f"    -> Successfully loaded {len(documents)} medical abstracts.")
    return documents


def build_database():
    """
    Main execution pipeline: cleans the existing database directory, chunks the text,
    initializes the embedding model on the optimal hardware, and builds the Chroma database.
    """
    # 1. Directory Initialization
    if os.path.exists(VECTOR_DB_DIR):
        print("[*] Found existing database. Cleaning directory to prevent data duplication...")
        shutil.rmtree(VECTOR_DB_DIR)

    # 2. Data Loading
    docs = load_and_process_data(INPUT_JSON)

    # 3. Text Chunking
    print("[*] Step 2: Chunking text for embedding...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"    -> Generated {len(chunks)} text chunks.")

    # 4. Hardware Detection & Model Initialization
    print("[*] Step 3: Initializing Embedding Model (BAAI/bge-small-en-v1.5)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"    -> Hardware assigned: {device.upper()}")

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': device}, 
        encode_kwargs={'normalize_embeddings': True}
    )

    # 5. Database Construction
    print("[*] Step 4: Building persistent Chroma Vector Database...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    
    print("\n[+] Pipeline Complete! Vector Database successfully built and saved.")
    print(f"    -> Location: {VECTOR_DB_DIR}")


if __name__ == "__main__":
    build_database()