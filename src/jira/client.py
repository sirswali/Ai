import os
from jira import JIRA
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sqlite3
import json

class JiraClient:
    def __init__(self, db_path=None):
        self.use_test_db = db_path is not None
        if self.use_test_db:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self._init_test_db()
        else:
            self.jira = JIRA(
                server=os.environ.get("JIRA_SERVER"),
                basic_auth=(os.environ.get("JIRA_USERNAME"), os.environ.get("JIRA_PASSWORD"))
            )
        self.project_key = os.environ.get("JIRA_PROJECT_KEY")

    def _init_test_db(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            key TEXT PRIMARY KEY,
            summary TEXT,
            description TEXT,
            status TEXT,
            assignee TEXT
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            issue_key TEXT,
            author TEXT,
            content TEXT,
            created TEXT,
            FOREIGN KEY (issue_key) REFERENCES issues (key)
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY,
            issue_key TEXT,
            type TEXT,
            author TEXT,
            from_status TEXT,
            to_status TEXT,
            created TEXT,
            FOREIGN KEY (issue_key) REFERENCES issues (key)
        )
        ''')
        self.conn.commit()

    def get_relevant_data(self, query: str) -> List[Dict[str, Any]]:
        if self.use_test_db:
            self.cursor.execute("SELECT * FROM issues WHERE summary LIKE ? OR description LIKE ? LIMIT 5", (f"%{query}%", f"%{query}%"))
            issues = self.cursor.fetchall()
            return [self.get_issue_data(issue[0]) for issue in issues]
        else:
            jql_query = f'project = {self.project_key} AND text ~ "{query}"'
            issues = self.jira.search_issues(jql_query, maxResults=5)
            return [self.get_issue_data(issue) for issue in issues]

    def get_issue_data(self, issue_key) -> Dict[str, Any]:
        if self.use_test_db:
            self.cursor.execute("SELECT * FROM issues WHERE key = ?", (issue_key,))
            issue = self.cursor.fetchone()
            return {
                "key": issue[0],
                "summary": self.anonymize_text(issue[1]),
                "description": self.anonymize_text(issue[2]),
                "status": issue[3],
                "assignee": self.anonymize_text(issue[4]) if issue[4] else "Unassigned",
                "activities": self.get_issue_activities(issue_key)
            }
        else:
            issue = self.jira.issue(issue_key)
            return {
                "key": issue.key,
                "summary": self.anonymize_text(issue.fields.summary),
                "description": self.anonymize_text(issue.fields.description or ""),
                "status": str(issue.fields.status),
                "assignee": self.anonymize_text(str(issue.fields.assignee)) if issue.fields.assignee else "Unassigned",
                "activities": self.get_issue_activities(issue.key)
            }

    def get_issue_activities(self, issue_key: str) -> List[Dict[str, Any]]:
        if self.use_test_db:
            self.cursor.execute("SELECT * FROM comments WHERE issue_key = ?", (issue_key,))
            comments = self.cursor.fetchall()
            self.cursor.execute("SELECT * FROM activities WHERE issue_key = ?", (issue_key,))
            status_changes = self.cursor.fetchall()
            
            activities = []
            for comment in comments:
                activities.append({
                    "type": "comment",
                    "author": self.anonymize_text(comment[2]),
                    "content": self.anonymize_text(comment[3]),
                    "created": comment[4]
                })
            for change in status_changes:
                activities.append({
                    "type": "status_change",
                    "author": self.anonymize_text(change[3]),
                    "from_status": change[4],
                    "to_status": change[5],
                    "created": change[6]
                })
            activities.sort(key=lambda x: x['created'])
            return activities
        else:
            issue = self.jira.issue(issue_key)
            activities = []
            for comment in issue.fields.comment.comments:
                activities.append({
                    "type": "comment",
                    "author": self.anonymize_text(str(comment.author)),
                    "content": self.anonymize_text(comment.body),
                    "created": comment.created
                })
            for history in issue.changelog.histories:
                for item in history.items:
                    if item.field == 'status':
                        activities.append({
                            "type": "status_change",
                            "author": self.anonymize_text(str(history.author)),
                            "from_status": item.fromString,
                            "to_status": item.toString,
                            "created": history.created
                        })
            activities.sort(key=lambda x: x['created'])
            return activities

    def get_team_members(self) -> List[str]:
        return ["Alice", "Bob", "Charlie", "David", "Eve"]

    def get_team_workload(self) -> Dict[str, List[Dict[str, Any]]]:
        team_members = self.get_team_members()
        workload = {}
        
        for member in team_members:
            if self.use_test_db:
                self.cursor.execute("SELECT * FROM issues WHERE assignee = ? AND status != 'Done'", (member,))
                issues = self.cursor.fetchall()
                workload[member] = [self.get_issue_data(issue[0]) for issue in issues]
            else:
                jql_query = f'project = {self.project_key} AND assignee = "{member}" AND status != Done'
                issues = self.jira.search_issues(jql_query)
                workload[member] = [self.get_issue_data(issue.key) for issue in issues]
        
        return workload

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        if self.use_test_db:
            self.cursor.execute("SELECT * FROM issues WHERE status != 'Done'")
            issues = self.cursor.fetchall()
            return [self.get_issue_data(issue[0]) for issue in issues]
        else:
            jql_query = f'project = {self.project_key} AND status != Done'
            issues = self.jira.search_issues(jql_query)
            return [self.get_issue_data(issue.key) for issue in issues]

    def get_team_skills(self) -> Dict[str, Dict[str, str]]:
        return {
            "Alice": {"Python": "Expert", "JavaScript": "Intermediate", "AWS": "Advanced"},
            "Bob": {"Java": "Expert", "Spring": "Advanced", "Docker": "Intermediate"},
            "Charlie": {"Python": "Advanced", "Data Science": "Expert", "Machine Learning": "Advanced"},
            "David": {"JavaScript": "Expert", "React": "Advanced", "Node.js": "Expert"},
            "Eve": {"DevOps": "Expert", "Kubernetes": "Advanced", "AWS": "Expert"}
        }

    def anonymize_text(self, text: str) -> str:
        import re
        return re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', text)

    def create_task(self, summary: str, description: str, assignee: str) -> str:
        if self.use_test_db:
            key = f"TEST-{self._get_next_id()}"
            self.cursor.execute(
                "INSERT INTO issues (key, summary, description, status, assignee) VALUES (?, ?, ?, ?, ?)",
                (key, summary, description, "To Do", assignee)
            )
            self.conn.commit()
            return key
        else:
            issue_dict = {
                'project': self.project_key,
                'summary': summary,
                'description': description,
                'issuetype': {'name': 'Task'},
                'assignee': {'name': assignee}
            }
            new_issue = self.jira.create_issue(fields=issue_dict)
            return new_issue.key

    def update_task(self, issue_key: str, **kwargs) -> None:
        if self.use_test_db:
            set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
            query = f"UPDATE issues SET {set_clause} WHERE key = ?"
            self.cursor.execute(query, list(kwargs.values()) + [issue_key])
            self.conn.commit()
        else:
            issue = self.jira.issue(issue_key)
            issue.update(kwargs)

    def add_task_comment(self, issue_key: str, comment: str) -> None:
        if self.use_test_db:
            self.cursor.execute(
                "INSERT INTO comments (issue_key, author, content, created) VALUES (?, ?, ?, ?)",
                (issue_key, "Test User", comment, datetime.now().isoformat())
            )
            self.conn.commit()
        else:
            self.jira.add_comment(issue_key, comment)

    def get_task_details(self, issue_key: str) -> Dict[str, Any]:
        return self.get_issue_data(issue_key)

    def get_recent_activities(self, days: int = 7) -> List[Dict[str, Any]]:
        since_date = datetime.now() - timedelta(days=days)
        if self.use_test_db:
            self.cursor.execute(
                "SELECT * FROM issues WHERE key IN (SELECT DISTINCT issue_key FROM activities WHERE created >= ?)",
                (since_date.isoformat(),)
            )
            issues = self.cursor.fetchall()
            activities = []
            for issue in issues:
                issue_activities = self.get_issue_activities(issue[0])
                activities.extend([{**activity, "issue_key": issue[0]} for activity in issue_activities])
        else:
            jql_query = f'project = {self.project_key} AND updated >= "{since_date.strftime("%Y-%m-%d")}"'
            issues = self.jira.search_issues(jql_query)
            activities = []
            for issue in issues:
                issue_activities = self.get_issue_activities(issue.key)
                activities.extend([{**activity, "issue_key": issue.key} for activity in issue_activities])
        
        activities.sort(key=lambda x: x['created'], reverse=True)
        return activities

    def _get_next_id(self) -> int:
        self.cursor.execute("SELECT MAX(CAST(SUBSTR(key, 6) AS INTEGER)) FROM issues")
        max_id = self.cursor.fetchone()[0]
        return (max_id or 0) + 1

    def __del__(self):
        if self.use_test_db:
            self.conn.close()

if __name__ == "__main__":
    # Example usage
    jira_client = JiraClient()
    
    print("Team Members:")
    print(jira_client.get_team_members())
    
    print("\nTeam Workload:")
    print(jira_client.get_team_workload())
    
    print("\nAll Tasks:")
    print(jira_client.get_all_tasks())
    
    print("\nTeam Skills:")
    print(jira_client.get_team_skills())
    
    print("\nCreate New Task:")
    new_task_key = jira_client.create_task("Test Task", "This is a test task created by the JiraClient", "Alice")
    print(f"New task created with key: {new_task_key}")
    
    print("\nTask Details:")
    task_details = jira_client.get_task_details(new_task_key)
    print(task_details)
    
    print("\nAdd Comment:")
    jira_client.add_task_comment(new_task_key, "This is a test comment added by the JiraClient")
    
    print("\nUpdated Task Details:")
    updated_task_details = jira_client.get_task_details(new_task_key)
    print(updated_task_details)
    
    print("\nRecent Activities:")
    recent_activities = jira_client.get_recent_activities(days=30)
    print(recent_activities[:5])  # Print first 5 recent activities