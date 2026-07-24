"""
Vector store management using ChromaDB
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

from config.settings import CHROMA_DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS


class VectorStore:
    """Manages ChromaDB vector store for document embeddings"""
    
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Collection name pattern: user_{user_id}
        self.collections = {}
    
    def get_collection(self, user_id: int):
        """Get or create collection for a user"""
        collection_name = f"user_{user_id}"
        
        if collection_name not in self.collections:
            self.collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"user_id": str(user_id)}
            )
        
        return self.collections[collection_name]
    
    def add_documents(self, user_id: int, chunks: List[Dict]) -> int:
        """
        Add document chunks to vector store
        Returns: number of chunks added
        """
        if not chunks:
            return 0
        
        collection = self.get_collection(user_id)
        
        # Prepare data for ChromaDB
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate unique IDs
        ids = [f"{user_id}_{i}_{chunk['metadata'].get('filename', 'doc')}_{chunk['metadata'].get('chunk_id', 0)}" 
               for i, chunk in enumerate(chunks)]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(chunks)
    
    def search(self, user_id: int, query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Search for relevant document chunks
        Returns: list of search results with text, metadata, and distance
        """
        collection = self.get_collection(user_id)
        
        # Check if collection has documents
        if collection.count() == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)[0].tolist()
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
        
        # Format results
        search_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                search_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return search_results
    
    def delete_collection(self, user_id: int):
        """Delete a user's collection"""
        collection_name = f"user_{user_id}"
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def get_document_count(self, user_id: int) -> int:
        """Get number of chunks in user's collection"""
        try:
            collection = self.get_collection(user_id)
            return collection.count()
        except:
            return 0
