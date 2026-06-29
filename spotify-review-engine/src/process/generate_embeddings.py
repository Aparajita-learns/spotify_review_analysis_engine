"""
src/process/generate_embeddings.py
----------------------------------
Phase 6 — Vector embeddings.
Uses sentence-transformers to compute embeddings for clean_documents
and saves them to the embeddings table in Supabase.
"""

from src.db.repository import get_client
from src.utils.logging import get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)

# Use a small, fast local model matching 384 dimensions
MODEL_NAME = 'all-MiniLM-L6-v2'
model = None

def get_model():
    global model
    if model is None:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)
    return model

def generate_embeddings(batch_size: int = 100):
    """
    Finds clean_documents that don't have an embedding yet and computes one.
    """
    logger.info("Starting embedding generation...")
    client = get_client()
    
    # We want to find clean_documents whose ID is NOT in the embeddings table
    # Supabase REST doesn't natively do LEFT JOIN with IS NULL well, 
    # but we can fetch clean documents, then fetch existing embeddings, and filter.
    # Alternatively, for MVP, we just fetch a bunch, and insert with ON CONFLICT DO NOTHING.
    
    # 1. Fetch clean documents
    # Using a simple query: get recently processed docs
    res = client.table("clean_documents").select("id, clean_text").limit(batch_size).order("processed_at", desc=True).execute()
    docs = res.data or []
    
    if not docs:
        logger.info("No clean documents found.")
        return {"processed": 0, "inserted": 0}
        
    # Check which ones already have embeddings
    doc_ids = [d["id"] for d in docs]
    embed_res = client.table("embeddings").select("clean_document_id").in_("clean_document_id", doc_ids).execute()
    existing_ids = {row["clean_document_id"] for row in (embed_res.data or [])}
    
    docs_to_process = [d for d in docs if d["id"] not in existing_ids]
    
    if not docs_to_process:
        logger.info("All fetched documents already have embeddings.")
        return {"processed": len(docs), "inserted": 0}
        
    logger.info(f"Computing embeddings for {len(docs_to_process)} documents...")
    transformer = get_model()
    
    texts = [d["clean_text"] for d in docs_to_process]
    # Compute embeddings
    embeddings = transformer.encode(texts)
    
    inserts = []
    for i, doc in enumerate(docs_to_process):
        inserts.append({
            "clean_document_id": doc["id"],
            "embedding": embeddings[i].tolist(),
            "embedding_model": MODEL_NAME
        })
        
    # Insert
    if inserts:
        client.table("embeddings").insert(inserts).execute()
        logger.info(f"Inserted {len(inserts)} embeddings.")
        
    return {"processed": len(docs_to_process), "inserted": len(inserts)}

def semantic_search(query: str, limit: int = 5, threshold: float = 0.5):
    """
    Embeds the user query and calls the hybrid_search RPC in Supabase.
    This combines vector similarity with exact keyword matches.
    (Note: threshold is currently ignored by the new hybrid SQL, but kept in signature for compatibility)
    """
    transformer = get_model()
    query_vector = transformer.encode(query).tolist()
    
    client = get_client()
    res = client.rpc(
        "hybrid_search",
        {
            "query_text": query,
            "query_embedding": query_vector,
            "match_count": limit
        }
    ).execute()
    
    return res.data or []

if __name__ == "__main__":
    res = generate_embeddings(batch_size=50)
    print("Result:", res)
