import unittest
from unittest.mock import MagicMock, patch
from Ai.src.main import initialize_components, register_slack_handlers, main

class TestMain(unittest.TestCase):

    @patch('Ai.src.main.load_dotenv')
    @patch('Ai.src.main.CustomLogger')
    @patch('Ai.src.main.KnowledgeBase')
    @patch('Ai.src.main.LLMWrapper')
    @patch('Ai.src.main.JiraClient')
    @patch('Ai.src.main.AuditLogger')
    @patch('Ai.src.main.AccessControl')
    @patch('Ai.src.main.ChatMemory')
    @patch('Ai.src.main.DataLineage')
    @patch('Ai.src.main.BiasManagement')
    @patch('Ai.src.main.TaskAllocator')
    def test_initialize_components(self, mock_task_allocator, mock_bias_management, mock_data_lineage, 
                                   mock_chat_memory, mock_access_control, mock_audit_logger, 
                                   mock_jira_client, mock_llm_wrapper, mock_knowledge_base, 
                                   mock_custom_logger, mock_load_dotenv):
        components = initialize_components()
        
        self.assertIsNotNone(components)
        self.assertIn('kb', components)
        self.assertIn('llm', components)
        self.assertIn('jira', components)
        self.assertIn('logger', components)
        self.assertIn('audit_logger', components)
        self.assertIn('access_control', components)
        self.assertIn('chat_memory', components)
        self.assertIn('data_lineage', components)
        self.assertIn('bias_management', components)
        self.assertIn('task_allocator', components)

    @patch('Ai.src.main.SlackBot')
    def test_register_slack_handlers(self, mock_slack_bot):
        mock_app = MagicMock()
        mock_slack_bot.app = mock_app
        mock_slack_bot.handlers = MagicMock()

        register_slack_handlers(mock_slack_bot)

        self.assertEqual(mock_app.command.call_count, 18)  # Number of registered commands

    @patch('Ai.src.main.initialize_components')
    @patch('Ai.src.main.SlackBot')
    def test_main(self, mock_slack_bot, mock_initialize_components):
        mock_components = {
            'kb': MagicMock(),
            'logger': MagicMock()
        }
        mock_initialize_components.return_value = mock_components

        main()

        mock_initialize_components.assert_called_once()
        mock_slack_bot.assert_called_once()
        mock_slack_bot.return_value.start.assert_called_once()
        mock_components['kb'].persist.assert_called_once()

class TestSlackHandlers(unittest.TestCase):

    def setUp(self):
        self.mock_slack_bot = MagicMock()
        self.mock_slack_bot.handlers = MagicMock()

    def test_handle_sprint_planning(self):
        self.mock_slack_bot.handlers.handle_sprint_planning(MagicMock())
        self.mock_slack_bot.handlers.handle_sprint_planning.assert_called_once()

    def test_handle_task_allocation(self):
        self.mock_slack_bot.handlers.handle_task_allocation(MagicMock())
        self.mock_slack_bot.handlers.handle_task_allocation.assert_called_once()

    def test_handle_progress_report(self):
        self.mock_slack_bot.handlers.handle_progress_report(MagicMock())
        self.mock_slack_bot.handlers.handle_progress_report.assert_called_once()

    def test_handle_bug_report(self):
        self.mock_slack_bot.handlers.handle_bug_report(MagicMock())
        self.mock_slack_bot.handlers.handle_bug_report.assert_called_once()

    def test_handle_feature_request(self):
        self.mock_slack_bot.handlers.handle_feature_request(MagicMock())
        self.mock_slack_bot.handlers.handle_feature_request.assert_called_once()

    def test_handle_code_review(self):
        self.mock_slack_bot.handlers.handle_code_review(MagicMock())
        self.mock_slack_bot.handlers.handle_code_review.assert_called_once()

    def test_handle_ci_cd_status(self):
        self.mock_slack_bot.handlers.handle_ci_cd_status(MagicMock())
        self.mock_slack_bot.handlers.handle_ci_cd_status.assert_called_once()

    def test_handle_workload_report(self):
        self.mock_slack_bot.handlers.handle_workload_report(MagicMock())
        self.mock_slack_bot.handlers.handle_workload_report.assert_called_once()

    def test_handle_retrospective(self):
        self.mock_slack_bot.handlers.handle_retrospective(MagicMock())
        self.mock_slack_bot.handlers.handle_retrospective.assert_called_once()

    def test_handle_release_planning(self):
        self.mock_slack_bot.handlers.handle_release_planning(MagicMock())
        self.mock_slack_bot.handlers.handle_release_planning.assert_called_once()

if __name__ == '__main__':
    unittest.main()