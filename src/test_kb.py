from knowledge_base.kb import KnowledgeBase
import os
import traceback

def test_knowledge_base():
    try:
        print("Starting knowledge base test...")
        
        # Create a test database file
        db_path = "test_knowledge.db"
        print(f"Using database path: {db_path}")
        
        # Initialize KnowledgeBase with SQLite storage
        print("Initializing KnowledgeBase...")
        kb = KnowledgeBase(db_path)
        print("KnowledgeBase initialized successfully.")
        
        # Test adding data with different sources
        print("\nPreparing test data...")
        test_data = [
            "JIRA-123: Implement user authentication system with OAuth2 integration.",
            "In yesterday's standup, we discussed the new feature requirements for the dashboard.",
            "JIRA-124: Fix performance bottleneck in database queries.",
            "Team agreed to use ChromaDB for vector storage implementation during architecture review.",
            "JIRA-125: Update API documentation with new endpoints.",
            "The deployment process needs to be automated using Jenkins pipeline."
        ]
        
        test_metadata = [
            {"source": "jira", "type": "task", "priority": "high"},
            {"source": "slack", "type": "meeting", "channel": "team-standup"},
            {"source": "jira", "type": "bug", "priority": "medium"},
            {"source": "slack", "type": "discussion", "channel": "architecture"},
            {"source": "jira", "type": "task", "priority": "low"},
            {"source": "slack", "type": "discussion", "channel": "devops"}
        ]
        
        print("Adding test data to knowledge base...")
        kb.add_data(test_data, metadata=test_metadata)
        
        # Test regular search
        print("\nTesting regular search for 'performance'...")
        results = kb.search("performance")
        print("Regular search results:")
        for result in results:
            print(f"- {result}")
        
        # Test semantic search for development-related queries
        print("\nTesting semantic search for 'authentication security'...")
        results = kb.semantic_search("authentication security")
        print("Semantic search results:")
        for result in results:
            print(f"- Content: {result['content']}")
            print(f"  Metadata: {result['metadata']}\n")
        
        # Test semantic search with source filter (JIRA only)
        print("\nTesting JIRA-only semantic search for 'documentation'...")
        results = kb.semantic_search("documentation", source_filter="jira")
        print("JIRA-filtered search results:")
        for result in results:
            print(f"- Content: {result['content']}")
            print(f"  Metadata: {result['metadata']}\n")
        
        # Test semantic search for similar concepts
        print("\nTesting semantic search for 'CI/CD automation'...")
        results = kb.semantic_search("CI/CD automation")
        print("CI/CD automation search results:")
        for result in results:
            print(f"- Content: {result['content']}")
            print(f"  Metadata: {result['metadata']}\n")
        
        # Test getting all data
        print("\nTesting get_all_data...")
        all_data = kb.get_all_data()
        print("All data in knowledge base:")
        for doc, meta in zip(all_data['documents'], all_data['metadatas']):
            print(f"- Document: {doc}")
            print(f"  Metadata: {meta}\n")
        
        # Close the database connection
        print("\nClosing database connection...")
        if hasattr(kb, 'conn'):
            kb.conn.close()
            print("Database connection closed.")
        
        # Clean up
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Cleaned up test database: {db_path}")
            except PermissionError:
                print(f"Note: Could not remove {db_path} - it may be in use")
                
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError during test execution:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_knowledge_base()
