import unittest
from unittest.mock import MagicMock, patch
from Ai.src.knowledge_base.kb import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        self.mock_storage = MagicMock()
        self.kb = KnowledgeBase(self.mock_storage)

    def test_add_entry(self):
        entry = {"id": "KB-1", "title": "Test Entry", "content": "This is a test entry"}
        self.kb.add_entry(entry)
        self.mock_storage.add.assert_called_once_with(entry)

    def test_get_entry(self):
        mock_entry = {"id": "KB-1", "title": "Test Entry", "content": "This is a test entry"}
        self.mock_storage.get.return_value = mock_entry
        result = self.kb.get_entry("KB-1")
        self.assertEqual(result, mock_entry)
        self.mock_storage.get.assert_called_once_with("KB-1")

    def test_update_entry(self):
        entry = {"id": "KB-1", "title": "Updated Entry", "content": "This is an updated test entry"}
        self.kb.update_entry("KB-1", entry)
        self.mock_storage.update.assert_called_once_with("KB-1", entry)

    def test_delete_entry(self):
        self.kb.delete_entry("KB-1")
        self.mock_storage.delete.assert_called_once_with("KB-1")

    def test_search(self):
        mock_results = [
            {"id": "KB-1", "title": "Test Entry 1", "content": "This is test entry 1"},
            {"id": "KB-2", "title": "Test Entry 2", "content": "This is test entry 2"}
        ]
        self.mock_storage.search.return_value = mock_results
        results = self.kb.search("test")
        self.assertEqual(results, mock_results)
        self.mock_storage.search.assert_called_once_with("test")

    def test_get_storage_info(self):
        mock_info = {"type": "vector", "size": 100}
        self.mock_storage.get_info.return_value = mock_info
        info = self.kb.get_storage_info()
        self.assertEqual(info, mock_info)
        self.mock_storage.get_info.assert_called_once()

    def test_persist(self):
        self.kb.persist()
        self.mock_storage.persist.assert_called_once()

    @patch('Ai.src.knowledge_base.kb.ChromaDB')
    def test_initialize_vector_store(self, mock_chroma_db):
        mock_chroma_instance = MagicMock()
        mock_chroma_db.return_value = mock_chroma_instance
        
        kb = KnowledgeBase("vector")
        
        mock_chroma_db.assert_called_once()
        self.assertIsInstance(kb._storage, MagicMock)

    @patch('Ai.src.knowledge_base.kb.SQLiteStorage')
    def test_initialize_sqlite_store(self, mock_sqlite_storage):
        mock_sqlite_instance = MagicMock()
        mock_sqlite_storage.return_value = mock_sqlite_instance
        
        kb = KnowledgeBase("sqlite")
        
        mock_sqlite_storage.assert_called_once()
        self.assertIsInstance(kb._storage, MagicMock)

if __name__ == '__main__':
    unittest.main()