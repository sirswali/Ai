import os
import json
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sqlite3

class JiraClient:
    def __init__(self, db_path=None):
        # Load JIRA endpoint schemas
        with open('src/JSON/JIRA/Jira_endpoints', 'r') as f:
            self.endpoints = json.load(f)
            
        self.use_test_db = db_path is not None
        if self.use_test_db:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self._init_test_db()
        else:
            # Use environment variables for JIRA connection
            self.server = os.environ.get("JIRA_SERVER")
            self.auth = (os.environ.get("JIRA_USERNAME"), os.environ.get("JIRA_PASSWORD"))
            self.project_key = os.environ.get("JIRA_PROJECT_KEY")

    def _make_request(self, endpoint_key: str, method: str, **kwargs) -> Dict:
        """Make a request to JIRA API using endpoint schemas"""
        if self.use_test_db:
            # Return mock data based on endpoint schemas
            return self._get_mock_response(endpoint_key)
        else:
            # Make actual API request using endpoint schemas
            endpoint = self.endpoints.get(endpoint_key)
            if not endpoint:
                raise ValueError(f"Unknown endpoint: {endpoint_key}")
                
            url = f"{self.server}{endpoint['path']}"
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                **kwargs
            )
            return response.json()

    def _get_mock_response(self, endpoint_key: str) -> Dict:
        """Get mock response based on endpoint schemas"""
        # Return appropriate mock data structure from endpoints schema
        return self.endpoints.get(endpoint_key, {}).get('example_response', {})

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get issue details using endpoint schema"""
        return self._make_request(
            'issues.get',
            'GET',
            params={'issueKey': issue_key}
        )

    def create_issue(self, summary: str, description: str, assignee: str) -> str:
        """Create issue using endpoint schema"""
        data = {
            'fields': {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': description,
                'assignee': {'name': assignee},
                'issuetype': {'name': 'Story'}
            }
        }
        response = self._make_request(
            'issues.create',
            'POST',
            json=data
        )
        return response.get('key')

    def search_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Search issues using endpoint schema"""
        return self._make_request(
            'issues.search',
            'GET',
            params={'jql': jql}
        )

    def get_project(self) -> Dict[str, Any]:
        """Get project details using endpoint schema"""
        return self._make_request(
            'projects.get',
            'GET',
            params={'projectKey': self.project_key}
        )

    def get_user(self, username: str) -> Dict[str, Any]:
        """Get user details using endpoint schema"""
        return self._make_request(
            'users.get',
            'GET',
            params={'username': username}
        )

    def get_workflow(self) -> Dict[str, Any]:
        """Get workflow details using endpoint schema"""
        return self._make_request(
            'workflow',
            'GET'
        )

    def get_sprint(self, sprint_id: str) -> Dict[str, Any]:
        """Get sprint details using endpoint schema"""
        return self._make_request(
            'sprints',
            'GET',
            params={'sprintId': sprint_id}
        )

    def _init_test_db(self):
        """Initialize test database if needed"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            key TEXT PRIMARY KEY,
            summary TEXT,
            description TEXT,
            status TEXT,
            assignee TEXT
        )
        ''')
        self.conn.commit()

    def __del__(self):
        if self.use_test_db:
            self.conn.close()
