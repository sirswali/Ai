from knowledge_base.kb import KnowledgeBase
import os

def test_knowledge_base():
    # Create a test database file
    db_path = "test_knowledge.db"
    
    # Initialize KnowledgeBase with SQLite storage
    kb = KnowledgeBase(db_path)
    
    # Test adding data
    test_data = [
        "This is a test document about AI and machine learning.",
        "Another document about software development and best practices.",
        "A third document discussing vector databases and embeddings."
    ]
    
    test_metadata = [
        {"type": "AI", "source": "test"},
        {"type": "Development", "source": "test"},
        {"type": "Database", "source": "test"}
    ]
    
    kb.add_data(test_data, metadata=test_metadata)
    
    # Test searching
    search_results = kb.search("AI machine learning")
    print("\nSearch results for 'AI machine learning':")
    for result in search_results:
        print(f"- {result}")
    
    # Test getting all data
    all_data = kb.get_all_data()
    print("\nAll data in knowledge base:")
    for doc, meta in zip(all_data['documents'], all_data['metadatas']):
        print(f"- Document: {doc}")
        print(f"  Metadata: {meta}\n")
    
    # Close the database connection
    if hasattr(kb, 'conn'):
        kb.conn.close()
    
    # Clean up
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"\nCleaned up test database: {db_path}")
        except PermissionError:
            print(f"\nNote: Could not remove {db_path} - it may be in use")

if __name__ == "__main__":
    test_knowledge_base()
