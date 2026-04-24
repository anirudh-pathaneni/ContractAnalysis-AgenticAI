import os
import chromadb
from chromadb.config import Settings

class VectorStoreClient:
    def __init__(self, host=None, port=None):
        self.host = host or os.getenv("CHROMA_HOST", "localhost")
        self.port = port or os.getenv("CHROMA_PORT", "8000")
        self._client = None
        self._collection = None

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=self.host, 
                port=self.port, 
                settings=Settings(allow_reset=True)
            )
        return self._client
        
    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="statutory_laws",
                metadata={"hnsw:space": "cosine"} # Default similarity metric
            )
        return self._collection

    def add_documents(self, ids, documents, metadatas=None):
        """Add legal documents into the vector store"""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_law(self, query, n_results=3):
        """Search for relevant statutory provisions given a legal query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def clear(self):
        """Reset the vector store"""
        self.client.reset()

vector_store = VectorStoreClient()
