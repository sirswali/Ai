import os
import chromadb
from chromadb.config import Settings
from cryptography.fernet import Fernet
import sqlite3
import json

class KnowledgeBase:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        self.storage_type = "sqlite" if storage_path.endswith('.db') else os.environ.get("KB_STORAGE_TYPE", "local")
        
        if self.storage_type == "local":
            self._init_local_storage()
        elif self.storage_type == "cloud":
            self._init_cloud_storage()
        elif self.storage_type == "sqlite":
            self._init_sqlite_storage()
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
        
        # Set up encryption
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            print(f"Generated new encryption key: {key.decode()}. Please set this as ENCRYPTION_KEY in your environment variables.")
        self.cipher_suite = Fernet(key)

    def _init_local_storage(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.storage_path
        ))
        self.collection = self.client.get_or_create_collection("knowledge_base")

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
            metadata TEXT
        )
        ''')
        self.conn.commit()

    def add_data(self, data, metadata=None, ids=None):
        encrypted_data = [self.cipher_suite.encrypt(item.encode()).decode() for item in data]
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(data))]
        
        if self.storage_type in ["local", "cloud"]:
            self.collection.add(
                documents=encrypted_data,
                metadatas=metadata,
                ids=ids
            )
        elif self.storage_type == "sqlite":
            for i, item in enumerate(encrypted_data):
                self.cursor.execute(
                    "INSERT OR REPLACE INTO knowledge_base (id, content, metadata) VALUES (?, ?, ?)",
                    (ids[i], item, json.dumps(metadata[i] if metadata else {}))
                )
            self.conn.commit()
        
        print(f"Added {len(data)} items to the knowledge base.")

    def search(self, query, n_results=5):
        if self.storage_type in ["local", "cloud"]:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            decrypted_results = [self.cipher_suite.decrypt(item.encode()).decode() for item in results['documents'][0]]
        elif self.storage_type == "sqlite":
            self.cursor.execute("SELECT content FROM knowledge_base WHERE content LIKE ? LIMIT ?", (f"%{query}%", n_results))
            results = self.cursor.fetchall()
            decrypted_results = [self.cipher_suite.decrypt(item[0].encode()).decode() for item in results]
        
        return decrypted_results

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

    def update_data(self, id, new_data, new_metadata=None):
        encrypted_data = self.cipher_suite.encrypt(new_data.encode()).decode()
        if self.storage_type in ["local", "cloud"]:
            self.collection.update(
                ids=[id],
                documents=[encrypted_data],
                metadatas=[new_metadata] if new_metadata else None
            )
        elif self.storage_type == "sqlite":
            self.cursor.execute(
                "UPDATE knowledge_base SET content = ?, metadata = ? WHERE id = ?",
                (encrypted_data, json.dumps(new_metadata) if new_metadata else None, id)
            )
            self.conn.commit()
        print(f"Updated item with id {id} in the knowledge base.")

    def delete_data(self, ids):
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