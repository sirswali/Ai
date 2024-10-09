import unittest
from unittest.mock import MagicMock, patch
from Ai.src.task_management.allocator import TaskAllocator

class TestTaskAllocator(unittest.TestCase):

    def setUp(self):
        self.mock_jira = MagicMock()
        self.mock_llm = MagicMock()
        self.task_allocator = TaskAllocator(self.mock_jira, self.mock_llm)

    def test_allocate_task(self):
        task = {"id": "TASK-1", "summary": "Test task", "description": "This is a test task"}
        team = [{"id": "USER-1", "name": "John Doe", "skills": ["Python", "Java"]}]
        
        self.mock_jira.get_task.return_value = task
        self.mock_jira.get_team.return_value = team
        self.mock_llm.analyze_task.return_value = ["Python"]
        self.mock_llm.match_skills.return_value = "USER-1"

        result = self.task_allocator.allocate_task("TASK-1")

        self.assertEqual(result, "USER-1")
        self.mock_jira.get_task.assert_called_once_with("TASK-1")
        self.mock_jira.get_team.assert_called_once()
        self.mock_llm.analyze_task.assert_called_once_with(task)
        self.mock_llm.match_skills.assert_called_once()

    def test_get_workload_report(self):
        self.mock_jira.get_user_tasks.return_value = [
            {"id": "TASK-1", "summary": "Task 1"},
            {"id": "TASK-2", "summary": "Task 2"}
        ]

        result = self.task_allocator.get_workload_report("USER-1")

        self.assertEqual(len(result), 2)
        self.mock_jira.get_user_tasks.assert_called_once_with("USER-1")

    def test_reallocate_tasks(self):
        tasks = [
            {"id": "TASK-1", "summary": "Task 1", "assignee": "USER-1"},
            {"id": "TASK-2", "summary": "Task 2", "assignee": "USER-2"}
        ]
        team = [
            {"id": "USER-1", "name": "John Doe", "skills": ["Python"]},
            {"id": "USER-2", "name": "Jane Doe", "skills": ["Java"]}
        ]

        self.mock_jira.get_all_tasks.return_value = tasks
        self.mock_jira.get_team.return_value = team
        self.mock_llm.optimize_allocation.return_value = [
            {"id": "TASK-1", "assignee": "USER-2"},
            {"id": "TASK-2", "assignee": "USER-1"}
        ]

        result = self.task_allocator.reallocate_tasks()

        self.assertEqual(len(result), 2)
        self.assertNotEqual(result[0]["assignee"], tasks[0]["assignee"])
        self.assertNotEqual(result[1]["assignee"], tasks[1]["assignee"])
        self.mock_jira.get_all_tasks.assert_called_once()
        self.mock_jira.get_team.assert_called_once()
        self.mock_llm.optimize_allocation.assert_called_once()

if __name__ == '__main__':
    unittest.main()