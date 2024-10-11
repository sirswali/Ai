from jira.client import JiraClient
from llm.wrapper import LLMWrapper
from typing import List, Dict, Any
import json
import os
from datetime import datetime

class TaskAllocator:
    def __init__(self, jira_client: JiraClient, llm: LLMWrapper):
        self.jira_client = jira_client
        self.llm = llm
        self.allocation_history = {}
        self.storage_file = 'task_allocation_history.json'
        self.load_allocation_history()

    def allocate_task(self, task_description: str, task_summary: str) -> str:
        team_members = self.jira_client.get_team_members()
        team_workload = self.get_team_workload()
        team_skills = self.jira_client.get_team_skills()
        
        context = f"Task Summary: {task_summary}\n"
        context += f"Task Description: {task_description}\n"
        context += f"Team Members: {', '.join(team_members)}\n"
        context += f"Current Team Workload:\n"
        for member, workload in team_workload.items():
            context += f"- {member}: {len(workload)} tasks\n"
            for task in workload[:3]:  # Include details of up to 3 tasks
                context += f"  - {task['summary']} (Status: {task['status']})\n"
                context += f"    Recent activity: {self._get_recent_activity(task['activities'])}\n"
        context += f"Team Skills:\n"
        for member, skills in team_skills.items():
            context += f"- {member}: {', '.join([f'{skill} ({level})' for skill, level in skills.items()])}\n"
        
        prompt = f"{context}\nBased on the given information, suggest the best team member to allocate this task to and provide a brief explanation why. Consider their current workload, recent activities, skills, and the requirements of the task."
        
        suggestion = self.llm.generate_response(prompt, context)
        
        # Record the allocation suggestion
        self._record_allocation(task_summary, suggestion)
        
        return suggestion

    def get_team_workload(self) -> dict:
        return self.jira_client.get_team_workload()

    def suggest_task_reallocation(self) -> str:
        current_tasks = self.jira_client.get_all_tasks()
        team_workload = self.get_team_workload()
        team_skills = self.jira_client.get_team_skills()
        
        context = "Current Tasks:\n"
        for task in current_tasks:
            context += f"- {task['key']}: {task['summary']} (Assigned to: {task['assignee']}, Status: {task['status']})\n"
            context += f"  Description: {task['description'][:100]}...\n"
            context += f"  Recent activity: {self._get_recent_activity(task['activities'])}\n"
        
        context += "\nTeam Workload:\n"
        for member, workload in team_workload.items():
            context += f"- {member}: {len(workload)} tasks\n"
            for task in workload[:3]:
                context += f"  - {task['summary']} (Status: {task['status']})\n"
                context += f"    Recent activity: {self._get_recent_activity(task['activities'])}\n"
        
        context += f"\nTeam Skills:\n"
        for member, skills in team_skills.items():
            context += f"- {member}: {', '.join([f'{skill} ({level})' for skill, level in skills.items()])}\n"
        
        prompt = f"{context}\nBased on the current tasks, team workload, recent activities, and team skills, suggest any task reallocations that could optimize team efficiency. Consider team members' skills, current workload, task descriptions, recent activities, and task priorities. Provide brief explanations for your suggestions."
        
        suggestions = self.llm.generate_response(prompt, context)
        
        return suggestions

    def analyze_task_requirements(self, task_description: str, task_summary: str) -> dict:
        prompt = f"Analyze the following task summary and description, and extract key skills or requirements:\n\nSummary: {task_summary}\n\nDescription: {task_description}\n\nList the key skills or requirements in a bullet point format."
        
        analysis = self.llm.generate_response(prompt)
        
        skills_dict = {}
        for line in analysis.split('\n'):
            if line.strip().startswith('- '):
                key, value = line.strip('- ').split(':', 1)
                skills_dict[key.strip()] = value.strip()
        
        return skills_dict

    def match_task_to_team_members(self, task_description: str, task_summary: str) -> List[Dict[str, Any]]:
        task_requirements = self.analyze_task_requirements(task_description, task_summary)
        team_members = self.jira_client.get_team_members()
        team_skills = self.jira_client.get_team_skills()
        team_workload = self.get_team_workload()
        
        matches = []
        for member in team_members:
            match_score = 0
            for skill, level in task_requirements.items():
                if skill in team_skills.get(member, {}):
                    match_score += 1
            
            recent_activity = self._get_recent_activity(team_workload[member][0]['activities']) if team_workload[member] else "No recent activity"
            
            matches.append({
                'member': member,
                'score': match_score,
                'current_tasks': len(team_workload.get(member, [])),
                'recent_activity': recent_activity
            })
        
        matches.sort(key=lambda x: (-x['score'], x['current_tasks']))
        
        return matches

    def _get_recent_activity(self, activities: List[Dict[str, Any]]) -> str:
        if not activities:
            return "No recent activity"
        
        most_recent = max(activities, key=lambda x: x['created'])
        
        if most_recent['type'] == 'comment':
            return f"Comment added by {most_recent['author']} on {most_recent['created']}"
        elif most_recent['type'] == 'status_change':
            return f"Status changed from {most_recent['from_status']} to {most_recent['to_status']} by {most_recent['author']} on {most_recent['created']}"
        else:
            return f"Activity of type {most_recent['type']} on {most_recent['created']}"

    def _record_allocation(self, task_summary: str, suggestion: str):
        self.allocation_history[task_summary] = {
            'suggestion': suggestion,
            'timestamp': datetime.now().isoformat()
        }
        self.save_allocation_history()

    def save_allocation_history(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.allocation_history, f, indent=2)

    def load_allocation_history(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                self.allocation_history = json.load(f)

    def get_allocation_history(self) -> Dict[str, Any]:
        return self.allocation_history

    def generate_allocation_report(self) -> str:
        report = "Task Allocation History Report:\n\n"
        for task, data in self.allocation_history.items():
            report += f"Task: {task}\n"
            report += f"Suggestion: {data['suggestion']}\n"
            report += f"Timestamp: {data['timestamp']}\n\n"
        return report

if __name__ == "__main__":
    jira_client = JiraClient()
    llm = LLMWrapper()
    allocator = TaskAllocator(jira_client, llm)
    
    task_summary = "Implement OAuth2 Authentication"
    task_description = "Implement a new authentication system using OAuth2 and integrate it with our existing Python backend. This task requires expertise in Python, OAuth2 protocols, and API security best practices."
    
    print("Task Allocation Suggestion:")
    print(allocator.allocate_task(task_description, task_summary))
    
    print("\nTask Reallocation Suggestions:")
    print(allocator.suggest_task_reallocation())
    
    print("\nTask Requirements Analysis:")
    print(allocator.analyze_task_requirements(task_description, task_summary))
    
    print("\nTask-Team Member Matching:")
    matches = allocator.match_task_to_team_members(task_description, task_summary)
    for match in matches:
        print(f"{match['member']}: Score {match['score']}, Current Tasks: {match['current_tasks']}, Recent Activity: {match['recent_activity']}")
    
    print("\nAllocation History Report:")
    print(allocator.generate_allocation_report())