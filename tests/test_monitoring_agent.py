import unittest
from unittest.mock import Mock, patch
import asyncio
from src.utils.monitoring_agent import MonitoringAgent
from src.utils.bias_management import BiasManagementMasterAgent

class TestMonitoringAgent(unittest.TestCase):
    def setUp(self):
        self.bias_management = Mock(spec=BiasManagementMasterAgent)
        self.monitoring_agent = MonitoringAgent(self.bias_management)

    @patch('aiohttp.ClientSession')
    async def test_monitor_slack_activity(self, mock_session):
        mock_response = Mock()
        mock_response.json.return_value = {"last_activity": "2023-05-01T12:00:00Z"}
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

        result = await self.monitoring_agent.monitor_slack_activity("U1234567")
        
        self.assertEqual(result, {"user_id": "U1234567", "last_activity": "2023-05-01T12:00:00Z"})
        mock_session.return_value.__aenter__.return_value.get.assert_called_once_with(
            "https://slack.com/api/users.info?user=U1234567",
            headers={"Authorization": f"Bearer {self.monitoring_agent.slack_token}"}
        )

    @patch('aiohttp.ClientSession')
    async def test_monitor_jira_updates(self, mock_session):
        mock_response = Mock()
        mock_response.json.return_value = {"last_update": "2023-05-01T14:30:00Z"}
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

        result = await self.monitoring_agent.monitor_jira_updates("PROJECT-1")
        
        self.assertEqual(result, {"project_key": "PROJECT-1", "last_update": "2023-05-01T14:30:00Z"})
        mock_session.return_value.__aenter__.return_value.get.assert_called_once_with(
            "https://your-domain.atlassian.net/rest/api/3/project/PROJECT-1",
            headers={"Authorization": f"Basic {self.monitoring_agent.jira_token}"}
        )

    async def test_process_slack_activity(self):
        self.monitoring_agent.monitor_slack_activity = Mock(return_value={"user_id": "U1234567", "last_activity": "2023-05-01T12:00:00Z"})
        result = await self.monitoring_agent.process("slack_activity", "U1234567")
        self.assertEqual(result, {"user_id": "U1234567", "last_activity": "2023-05-01T12:00:00Z"})
        self.monitoring_agent.monitor_slack_activity.assert_called_once_with("U1234567")

    async def test_process_jira_updates(self):
        self.monitoring_agent.monitor_jira_updates = Mock(return_value={"project_key": "PROJECT-1", "last_update": "2023-05-01T14:30:00Z"})
        result = await self.monitoring_agent.process("jira_updates", "PROJECT-1")
        self.assertEqual(result, {"project_key": "PROJECT-1", "last_update": "2023-05-01T14:30:00Z"})
        self.monitoring_agent.monitor_jira_updates.assert_called_once_with("PROJECT-1")

    async def test_process_unknown_task(self):
        with self.assertRaises(ValueError):
            await self.monitoring_agent.process("unknown_task")

if __name__ == '__main__':
    unittest.main()