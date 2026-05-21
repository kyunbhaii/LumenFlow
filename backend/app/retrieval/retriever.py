import torch
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document

from app.core.config import settings
from app.schemas.retrieval import RetrievedDocument


class LumenRetriever:
    """
    Dedicated Retrieval Module for LumenFlow.
    Handles embedding generation and pgvector similarity search.
    """
    def __init__(self, db_url: str):
        self.device = self._get_device()
        self.embedding_model = self._load_embedding_model()
        
        self.vector_store = PGVector(
            embeddings=self.embedding_model,
            collection_name="lumenflow_kb",
            connection=db_url,
            use_jsonb=True,
        )

    def _get_device(self) -> str:
        """Automatically select MPS for Mac, CUDA for Nvidia, fallback to CPU."""
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load_embedding_model(self) -> HuggingFaceEmbeddings:
        """Load local embeddings taking inspiration from example_code for max speed."""
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME} on {self.device.upper()}")
        return HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={"device": self.device},
            encode_kwargs={"normalize_embeddings": True}, # Essential for pure Cosine Similarity
        )

    def insert_documents(self, documents: List[dict]):
        """
        Inserts raw dictionaries into pgvector.
        Expected format: [{"content": "...", "metadata": {"source_id": "..."}}]
        """
        lc_docs = []
        for doc in documents:
            lc_docs.append(Document(
                page_content=doc["content"],
                metadata=doc.get("metadata", {})
            ))
        
        self.vector_store.add_documents(lc_docs)
        print(f"Inserted {len(lc_docs)} documents into pgvector.")

    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievedDocument]:
        """
        Deterministic Top-K retrieval mapping perfectly to the Pydantic schema.
        We return similarity scores so the workflow can enforce threshold logic later.
        """
        # similarity_search_with_score returns (Document, score)
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        retrieved = []
        for doc, score in results:
            retrieved.append(RetrievedDocument(
                source_id=doc.metadata.get("source_id", "unknown"),
                content=doc.page_content,
                # In LangChain PGVector, distance is returned. Similarity = 1 - distance.
                similarity_score=round(1.0 - float(score), 4)
            ))
            
        return retrieved
