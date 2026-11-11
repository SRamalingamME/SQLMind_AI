import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.utils import embedding_functions
from src.reflect_schema import reflect_database_schema

# Persistent ChromaDB location
CHROMA_DATA_PATH = "data/chroma_db"
COLLECTION_NAME = "schema_collection"

def get_embedding_function():
    """Module 3.2: Configures local HuggingFace all-MiniLM-L6-v2 embeddings."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

def initialize_vector_store():
    """Module 3.1: Initializes persistent local ChromaDB client and collection."""
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    embedding_func = get_embedding_function()
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def ingest_schema_chunks():
    """Module 3.3: Chunks schema metadata per table and ingests into ChromaDB."""
    schema_metadata = reflect_database_schema()
    collection = initialize_vector_store()
    
    documents = []
    metadatas = []
    ids = []

    for table_name, details in schema_metadata.items():
        # Build text chunk representation per table
        cols_desc = ", ".join([f"{col['name']} ({col['type']})" for col in details["columns"]])
        chunk_text = f"Table name: {table_name}. Columns: {cols_desc}."
        
        if details["foreign_keys"]:
            fk_desc = "; ".join([
                f"FK {', '.join(fk['constrained_columns'])} connects to {fk['referred_table']}({', '.join(fk['referred_columns'])})"
                for fk in details["foreign_keys"]
            ])
            chunk_text += f" Foreign Keys: {fk_desc}."
            
        documents.append(chunk_text)
        metadatas.append({"table_name": table_name})
        ids.append(f"table_{table_name}")

    # Insert/Upsert into ChromaDB
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully ingested {len(documents)} table schema chunks into ChromaDB.")

def retrieve_relevant_schema(query: str, n_results: int = 2) -> list[str]:
    """Module 3.4: Retrieves top-k matching table chunks given a natural language query."""
    collection = initialize_vector_store()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    retrieved_chunks = results["documents"][0] if results["documents"] else []
    return retrieved_chunks

if __name__ == "__main__":
    print("--- Phase 3: Ingesting Database Schema into ChromaDB ---")
    ingest_schema_chunks()
    
    print("\n--- Testing RAG Semantic Search ---")
    sample_query = "How many customers ordered 'Product X'?"
    retrieved_context = retrieve_relevant_schema(sample_query, n_results=3)
    
    print(f"\nUser Query: '{sample_query}'")
    print("\nRetrieved Schema Context:")
    for idx, chunk in enumerate(retrieved_context, 1):
        print(f"{idx}. {chunk}")