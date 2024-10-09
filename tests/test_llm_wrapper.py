import unittest
from unittest.mock import MagicMock, patch
from Ai.src.llm.wrapper import LLMWrapper

class TestLLMWrapper(unittest.TestCase):

    def setUp(self):
        self.mock_model = MagicMock()
        self.llm_wrapper = LLMWrapper(self.mock_model)

    def test_analyze_task(self):
        task = {"id": "TASK-1", "summary": "Implement login functionality", "description": "Create a secure login system using OAuth2"}
        expected_skills = ["Python", "OAuth2", "Security"]
        
        self.mock_model.generate.return_value = "Python, OAuth2, Security"
        
        result = self.llm_wrapper.analyze_task(task)
        
        self.assertEqual(result, expected_skills)
        self.mock_model.generate.assert_called_once()

    def test_match_skills(self):
        required_skills = ["Python", "OAuth2", "Security"]
        team = [
            {"id": "USER-1", "name": "John Doe", "skills": ["Python", "Java", "Security"]},
            {"id": "USER-2", "name": "Jane Doe", "skills": ["Python", "OAuth2", "React"]}
        ]
        
        self.mock_model.generate.return_value = "USER-2"
        
        result = self.llm_wrapper.match_skills(required_skills, team)
        
        self.assertEqual(result, "USER-2")
        self.mock_model.generate.assert_called_once()

    def test_optimize_allocation(self):
        tasks = [
            {"id": "TASK-1", "summary": "Implement login", "assignee": "USER-1"},
            {"id": "TASK-2", "summary": "Design database", "assignee": "USER-2"}
        ]
        team = [
            {"id": "USER-1", "name": "John Doe", "skills": ["Python", "Frontend"]},
            {"id": "USER-2", "name": "Jane Doe", "skills": ["Database", "Backend"]}
        ]
        
        expected_allocation = [
            {"id": "TASK-1", "summary": "Implement login", "assignee": "USER-1"},
            {"id": "TASK-2", "summary": "Design database", "assignee": "USER-2"}
        ]
        
        self.mock_model.generate.return_value = str(expected_allocation)
        
        result = self.llm_wrapper.optimize_allocation(tasks, team)
        
        self.assertEqual(result, expected_allocation)
        self.mock_model.generate.assert_called_once()

    def test_summarize(self):
        text = "This is a long text that needs to be summarized. It contains important information about the project."
        expected_summary = "Summary of the project information."
        
        self.mock_model.generate.return_value = expected_summary
        
        result = self.llm_wrapper.summarize(text)
        
        self.assertEqual(result, expected_summary)
        self.mock_model.generate.assert_called_once()

    def test_semantic_search(self):
        query = "How to implement OAuth2?"
        context = ["OAuth2 implementation guide", "Security best practices", "User authentication methods"]
        expected_result = ["OAuth2 implementation guide", "User authentication methods"]
        
        self.mock_model.generate.return_value = str(expected_result)
        
        result = self.llm_wrapper.semantic_search(query, context)
        
        self.assertEqual(result, expected_result)
        self.mock_model.generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()