import os
import json
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sqlite3

class JiraClient:
    def __init__(self, db_path=None):
        # Load JIRA endpoint schemas
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'JSON', 'JIRA', 'Jira_endpoints')
        try:
            with open(schema_path, 'r') as f:
                self.endpoints = json.load(f)
        except FileNotFoundError:
            # If schema file not found, use empty dict to allow test mode to work
            self.endpoints = {}
            
        self.use_test_db = db_path is not None
        if self.use_test_db:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self._init_test_db()
        else:
            # Use environment variables for JIRA connection
            self.server = os.getenv("JIRA_SERVER", "http://localhost:8080")
            self.auth = (
                os.getenv("JIRA_USERNAME", "default_user"),
                os.getenv("JIRA_PASSWORD", "default_pass")
            )
            self.project_key = os.getenv("JIRA_PROJECT_KEY", "TEST")

    def _make_request(self, endpoint_key: str, method: str, **kwargs) -> Dict:
        """Make a request to JIRA API using endpoint schemas"""
        if self.use_test_db:
            # Return mock data based on endpoint schemas
            return self._get_mock_response(endpoint_key)
        else:
            # Make actual API request using endpoint schemas
            endpoint = self.endpoints.get(endpoint_key, {})
            if not endpoint:
                return {}  # Return empty dict if endpoint not found
                
            url = f"{self.server}{endpoint.get('path', '')}"
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error making JIRA request: {e}")
                return {}

    def _get_mock_response(self, endpoint_key: str) -> Dict:
        """Get mock response based on endpoint schemas"""
        # Return appropriate mock data structure from endpoints schema
        return self.endpoints.get(endpoint_key, {}).get('example_response', {})

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get issue details using endpoint schema"""
        if self.use_test_db:
            self.cursor.execute("SELECT * FROM issues WHERE key = ?", (issue_key,))
            issue = self.cursor.fetchone()
            if issue:
                return {
                    "key": issue[0],
                    "summary": issue[1],
                    "description": issue[2],
                    "status": issue[3],
                    "assignee": issue[4]
                }
            return {}
        else:
            return self._make_request(
                'issues.get',
                'GET',
                params={'issueKey': issue_key}
            )

    def create_issue(self, summary: str, description: str, assignee: str) -> str:
        """Create issue using endpoint schema"""
        if self.use_test_db:
            key = f"TEST-{self._get_next_id()}"
            self.cursor.execute(
                "INSERT INTO issues (key, summary, description, status, assignee) VALUES (?, ?, ?, ?, ?)",
                (key, summary, description, "To Do", assignee)
            )
            self.conn.commit()
            return key
        else:
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
            return response.get('key', '')

    def search_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Search issues using endpoint schema"""
        if self.use_test_db:
            self.cursor.execute("SELECT * FROM issues")
            issues = self.cursor.fetchall()
            return [{
                "key": issue[0],
                "summary": issue[1],
                "description": issue[2],
                "status": issue[3],
                "assignee": issue[4]
            } for issue in issues]
        else:
            response = self._make_request(
                'issues.search',
                'GET',
                params={'jql': jql}
            )
            return response.get('issues', [])

    def get_team_members(self) -> List[str]:
        """Get list of team members"""
        if self.use_test_db:
            return ["Alice", "Bob", "Charlie", "David", "Eve"]
        else:
            response = self._make_request(
                'users.search',
                'GET',
                params={'groupname': 'jira-software-users'}
            )
            return [user.get('name', '') for user in response.get('users', [])]

    def get_team_workload(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get workload for each team member"""
        team_members = self.get_team_members()
        workload = {}
        
        for member in team_members:
            if self.use_test_db:
                self.cursor.execute("SELECT * FROM issues WHERE assignee = ? AND status != 'Done'", (member,))
                issues = self.cursor.fetchall()
                workload[member] = [{
                    "key": issue[0],
                    "summary": issue[1],
                    "description": issue[2],
                    "status": issue[3]
                } for issue in issues]
            else:
                jql = f'assignee = "{member}" AND status != Done'
                workload[member] = self.search_issues(jql)
        
        return workload

    def _init_test_db(self):
        """Initialize test database tables"""
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

    def _get_next_id(self) -> int:
        """Get next ID for test database"""
        self.cursor.execute("SELECT COUNT(*) FROM issues")
        return self.cursor.fetchone()[0] + 1

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
