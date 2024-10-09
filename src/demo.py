import os
from dotenv import load_dotenv
from main import initialize_components
from slack.bot import SlackBot
import config

def run_demo():
    load_dotenv()
    components = initialize_components()
    
    print("AI-Powered Task Management and Knowledge Base System Demo")
    print("========================================================")
    
    # Demonstrate task allocation
    task = {"id": "TASK-1", "summary": "Implement login functionality", "description": "Create a secure login system using OAuth2"}
    allocated_user = components['task_allocator'].allocate_task(task['id'])
    print(f"\nTask '{task['summary']}' allocated to user: {allocated_user}")
    
    # Demonstrate knowledge base
    kb_entry = {"id": "KB-1", "title": "OAuth2 Implementation Guide", "content": "Step-by-step guide to implement OAuth2 in Python applications."}
    components['kb'].add_entry(kb_entry)
    print(f"\nAdded knowledge base entry: {kb_entry['title']}")
    
    search_results = components['kb'].search("OAuth2")
    print(f"Search results for 'OAuth2': {search_results}")
    
    # Demonstrate LLM capabilities
    summary = components['llm'].summarize(kb_entry['content'])
    print(f"\nSummary of '{kb_entry['title']}': {summary}")
    
    # Demonstrate Slack integration
    slack_bot = SlackBot(components, config.SLACK_BOT_TOKEN, config.SLACK_SIGNING_SECRET)
    print("\nSlack bot initialized. You can now interact with the bot using the following commands:")
    print("- /allocate_task")
    print("- /workload_report")
    print("- /kb_search")
    print("- /summarize")
    print("(Note: Actual Slack integration requires running the bot in a Slack workspace)")

if __name__ == "__main__":
    run_demo()