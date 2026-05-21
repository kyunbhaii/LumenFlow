import json
import os
import sys

# Add the backend directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.db import models
from app.db.models.kb_documents import KBDocument
from app.retrieval.retriever import LumenRetriever
from app.core.config import settings
from app.schemas.kb_document import KBDocumentCreate

def run_test():
    # Ensure database extensions and tables exist
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    # 1. Initialize DB Session and Retrieval Service
    db = SessionLocal()
    print("Initializing LumenRetriever...")
    retriever = LumenRetriever(db_url=settings.SQLALCHEMY_DATABASE_URL)

    # 2. Load the synthetic knowledge base
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kb_path = os.path.join(backend_dir, "synthetic_data", "knowledge_base.json")
    with open(kb_path, "r") as f:
        kb_data = json.load(f)

    # 3. Production Ingestion Workflow: ORM -> VectorStore
    print("\nStarting Two-Tier Ingestion (SQL -> PGVector)...")
    docs_for_vector_store = []
    
    for item in kb_data:
        # A. Validate raw data using Pydantic Schema
        validated_doc = KBDocumentCreate(
            source=item["metadata"]["source_id"],
            content=item["content"]
        )

        # B. Save to Relational Database (Source of Truth) using validated data
        kb_doc = KBDocument(
            source=validated_doc.source,
            content=validated_doc.content
        )
        db.add(kb_doc)
        db.commit()
        db.refresh(kb_doc)
        print(f"Saved to SQL: {kb_doc.source} (ID: {kb_doc.id})")
        
        # C. Prepare for Vector Store, tagging it with the SQL ID
        item["metadata"]["sql_id"] = kb_doc.id
        docs_for_vector_store.append(item)

    # C. Sync to LangChain PGVector
    print(f"Syncing {len(docs_for_vector_store)} documents into PGVector embeddings...")
    retriever.insert_documents(docs_for_vector_store)

    # 4. Run a deterministic retrieval test
    test_query = "URGENT: Billed twice for Policy #POL-8829"
    print(f"\nTesting Retrieval with query: '{test_query}'")
    
    results = retriever.retrieve(query=test_query, top_k=2)

    # 5. Output the results
    print("\n--- RETRIEVAL RESULTS ---")
    for i, res in enumerate(results):
        print(f"\nRank {i+1}:")
        print(f"Source ID: {res.source_id}")
        print(f"Similarity Score: {res.similarity_score}")
        print(f"Content: {res.content}")
        
    db.close()

if __name__ == "__main__":
    run_test()