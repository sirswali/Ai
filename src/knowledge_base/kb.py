import os
from cryptography.fernet import Fernet
import sqlite3
import json
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer

class KnowledgeBase:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.storage_type = "sqlite" if storage_path.endswith('.db') else os.environ.get("KB_STORAGE_TYPE", "local")
        
        # Initialize sentence transformer for text embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        if self.storage_type == "local":
            try:
                import chromadb
                from chromadb.config import Settings
                self._init_local_storage()
            except ImportError:
                print("ChromaDB not installed. Falling back to SQLite storage with basic vector support.")
                self.storage_type = "sqlite"
                self._init_sqlite_storage()
        elif self.storage_type == "cloud":
            try:
                import chromadb
                from chromadb.config import Settings
                self._init_cloud_storage()
            except ImportError:
                print("ChromaDB not installed. Falling back to SQLite storage with basic vector support.")
                self.storage_type = "sqlite"
                self._init_sqlite_storage()
        elif self.storage_type == "sqlite":
            self._init_sqlite_storage()
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
        
        # Set up encryption
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            print(f"Generated new encryption key: {key.decode()}. Please set this as ENCRYPTION_KEY in your environment variables.")
        self.cipher_suite = Fernet(key.encode() if isinstance(key, str) else key)

    def _init_local_storage(self):
        import chromadb
        from chromadb.config import Settings
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.storage_path
        ))
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity for semantic search
        )

    def _init_cloud_storage(self):
        # Placeholder for cloud storage initialization
        print("Cloud storage initialization not yet implemented")

    def _init_sqlite_storage(self):
        self.conn = sqlite3.connect(self.storage_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id TEXT PRIMARY KEY,
            content TEXT,
            metadata TEXT,
            embedding BLOB  -- Store vector embeddings
        )
        ''')
        self.conn.commit()

    def _compute_embedding(self, text: str) -> List[float]:
        """Compute vector embedding for a text using sentence-transformers."""
        return self.encoder.encode(text).tolist()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import numpy as np
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def add_data(self, data: List[str], metadata: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        encrypted_data = [self.cipher_suite.encrypt(item.encode()).decode() for item in data]
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(data))]
            
        if metadata is None:
            metadata = [{}] * len(data)
        
        # Compute embeddings for semantic search
        embeddings = [self._compute_embedding(text) for text in data]
        
        if self.storage_type in ["local", "cloud"]:
            self.collection.add(
                documents=encrypted_data,
                metadatas=metadata,
                ids=ids,
                embeddings=embeddings
            )
        elif self.storage_type == "sqlite":
            for i, item in enumerate(encrypted_data):
                embedding_bytes = json.dumps(embeddings[i]).encode()
                self.cursor.execute(
                    "INSERT OR REPLACE INTO knowledge_base (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
                    (ids[i], item, json.dumps(metadata[i]), embedding_bytes)
                )
            self.conn.commit()
        
        print(f"Added {len(data)} items to the knowledge base.")

    def search(self, query: str, n_results: int = 5) -> List[str]:
        query_embedding = self._compute_embedding(query)
        
        if self.storage_type in ["local", "cloud"]:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            decrypted_results = [self.cipher_suite.decrypt(item.encode()).decode() for item in results['documents'][0]]
        elif self.storage_type == "sqlite":
            # Get all documents and their embeddings
            self.cursor.execute("SELECT content, embedding FROM knowledge_base")
            results = self.cursor.fetchall()
            
            # Compute similarities and sort
            similarities = []
            for content, embedding_bytes in results:
                doc_embedding = json.loads(embedding_bytes.decode())
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((similarity, content))
            
            # Sort by similarity and take top n_results
            similarities.sort(reverse=True)
            top_results = similarities[:n_results]
            
            # Decrypt results
            decrypted_results = [
                self.cipher_suite.decrypt(content.encode()).decode()
                for _, content in top_results
            ]
        
        return decrypted_results

    def semantic_search(self, query: str, n_results: int = 5, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search with optional source filtering (e.g., 'jira', 'slack').
        Returns both documents and their metadata.
        """
        query_embedding = self._compute_embedding(query)
        
        if self.storage_type in ["local", "cloud"]:
            where = {"source": source_filter} if source_filter else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            return [{
                'content': self.cipher_suite.decrypt(doc.encode()).decode(),
                'metadata': meta
            } for doc, meta in zip(results['documents'][0], results['metadatas'][0])]
        else:
            # Get all documents with their embeddings and metadata
            self.cursor.execute("SELECT content, embedding, metadata FROM knowledge_base")
            results = self.cursor.fetchall()
            
            # Compute similarities and filter by source if needed
            similarities = []
            for content, embedding_bytes, metadata_str in results:
                metadata = json.loads(metadata_str)
                if source_filter and metadata.get('source') != source_filter:
                    continue
                    
                doc_embedding = json.loads(embedding_bytes.decode())
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((similarity, content, metadata))
            
            # Sort by similarity and take top n_results
            similarities.sort(reverse=True)
            top_results = similarities[:n_results]
            
            return [{
                'content': self.cipher_suite.decrypt(content.encode()).decode(),
                'metadata': metadata
            } for _, content, metadata in top_results]

    def get_all_data(self):
        if self.storage_type in ["local", "cloud"]:
            all_data = self.collection.get()
            decrypted_docs = [self.cipher_suite.decrypt(item.encode()).decode() for item in all_data['documents']]
            return {
                'documents': decrypted_docs,
                'metadatas': all_data['metadatas'],
                'ids': all_data['ids']
            }
        elif self.storage_type == "sqlite":
            self.cursor.execute("SELECT id, content, metadata FROM knowledge_base")
            results = self.cursor.fetchall()
            return {
                'documents': [self.cipher_suite.decrypt(item[1].encode()).decode() for item in results],
                'metadatas': [json.loads(item[2]) for item in results],
                'ids': [item[0] for item in results]
            }

    def update_data(self, id: str, new_data: str, new_metadata: Optional[Dict[str, Any]] = None):
        encrypted_data = self.cipher_suite.encrypt(new_data.encode()).decode()
        embedding = self._compute_embedding(new_data)
        
        if self.storage_type in ["local", "cloud"]:
            self.collection.update(
                ids=[id],
                documents=[encrypted_data],
                metadatas=[new_metadata] if new_metadata else None,
                embeddings=[embedding]
            )
        elif self.storage_type == "sqlite":
            embedding_bytes = json.dumps(embedding).encode()
            self.cursor.execute(
                "UPDATE knowledge_base SET content = ?, metadata = ?, embedding = ? WHERE id = ?",
                (encrypted_data, json.dumps(new_metadata) if new_metadata else None, embedding_bytes, id)
            )
            self.conn.commit()
        print(f"Updated item with id {id} in the knowledge base.")

    def delete_data(self, ids: List[str]):
        if self.storage_type in ["local", "cloud"]:
            self.collection.delete(ids=ids)
        elif self.storage_type == "sqlite":
            placeholders = ', '.join(['?' for _ in ids])
            self.cursor.execute(f"DELETE FROM knowledge_base WHERE id IN ({placeholders})", ids)
            self.conn.commit()
        print(f"Deleted {len(ids)} items from the knowledge base.")

    def persist(self):
        if self.storage_type == "local":
            self.client.persist()
            print("Knowledge base data persisted to local storage.")
        elif self.storage_type == "cloud":
            print("Data persistence handled automatically in cloud storage.")
        elif self.storage_type == "sqlite":
            self.conn.commit()
            print("Knowledge base data persisted to SQLite database.")

    def get_storage_info(self):
        return f"Knowledge Base is using {self.storage_type} storage at {self.storage_path}."

    def __del__(self):
        if self.storage_type == "sqlite":
            self.conn.close()
