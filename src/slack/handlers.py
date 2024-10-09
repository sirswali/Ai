import json
from datetime import datetime, timedelta

class SlackHandlers:
    def __init__(self, components):
        self.kb = components['kb']
        self.llm = components['llm']
        self.jira = components['jira']
        self.logger = components['logger']
        self.access_control = components['access_control']
        self.chat_memory = components['chat_memory']
        self.data_lineage = components['data_lineage']
        self.bias_management = components['bias_management']
        self.task_allocator = components['task_allocator']

    # ... (previous methods remain unchanged)

    def handle_monitor_slack(self, ack, say, command):
        ack()
        user_id = command['user_id']

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            monitoring_result = self.bias_management.assign_task('monitor_activity', 'slack_activity', user_id)
            say(f"Slack Activity Monitoring Result:\n{monitoring_result}")
        except Exception as e:
            say(f"An error occurred while monitoring Slack activity: {str(e)}")

    def handle_monitor_jira(self, ack, say, command):
        ack()
        user_id = command['user_id']

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            project_key = command['text'].strip()
            if not project_key:
                say("Please provide a JIRA project key. Example: /monitor_jira PROJECT-1")
                return

            monitoring_result = self.bias_management.assign_task('monitor_activity', 'jira_updates', project_key)
            say(f"JIRA Updates Monitoring Result:\n{monitoring_result}")
        except Exception as e:
            say(f"An error occurred while monitoring JIRA updates: {str(e)}")

    def handle_query_knowledge_base(self, ack, say, command):
        ack()
        user_id = command['user_id']
        query = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            result = self.kb.query(query)
            say(f"Knowledge Base Query Result:\n{result}")
        except Exception as e:
            say(f"An error occurred while querying the knowledge base: {str(e)}")

    def handle_create_jira_ticket(self, ack, say, command):
        ack()
        user_id = command['user_id']
        ticket_info = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            ticket = self.jira.create_ticket(ticket_info)
            say(f"JIRA ticket created successfully. Ticket ID: {ticket.id}")
        except Exception as e:
            say(f"An error occurred while creating the JIRA ticket: {str(e)}")

    def handle_summarize_conversation(self, ack, say, command):
        ack()
        user_id = command['user_id']
        conversation_id = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            conversation = self.chat_memory.get_conversation(conversation_id)
            summary = self.llm.summarize(conversation)
            say(f"Conversation Summary:\n{summary}")
        except Exception as e:
            say(f"An error occurred while summarizing the conversation: {str(e)}")

    def handle_task_allocation(self, ack, say, command):
        ack()
        user_id = command['user_id']
        task_info = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            allocation_result = self.task_allocator.allocate_task(task_info)
            say(f"Task Allocation Result:\n{allocation_result}")
        except Exception as e:
            say(f"An error occurred while allocating the task: {str(e)}")

    def handle_data_lineage_request(self, ack, say, command):
        ack()
        user_id = command['user_id']
        data_point = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            lineage_info = self.data_lineage.get_lineage(data_point)
            say(f"Data Lineage Information:\n{lineage_info}")
        except Exception as e:
            say(f"An error occurred while retrieving data lineage: {str(e)}")

    def handle_bias_check(self, ack, say, command):
        ack()
        user_id = command['user_id']
        text = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            bias_result = self.bias_management.check_bias(text)
            say(f"Bias Check Result:\n{bias_result}")
        except Exception as e:
            say(f"An error occurred while performing the bias check: {str(e)}")

    def handle_access_request(self, ack, say, command):
        ack()
        user_id = command['user_id']
        feature = command['text'].strip()

        try:
            request_result = self.access_control.request_access(user_id, feature)
            say(f"Access Request Result:\n{request_result}")
        except Exception as e:
            say(f"An error occurred while processing the access request: {str(e)}")

    def handle_chat_history(self, ack, say, command):
        ack()
        user_id = command['user_id']
        time_range = command['text'].strip()

        if not self.access_control.check_access(user_id):
            say("You don't have permission to use this feature.")
            return

        try:
            history = self.chat_memory.get_user_history(user_id, time_range)
            summary = self.llm.summarize(history)
            say(f"Chat History Summary:\n{summary}")
        except Exception as e:
            say(f"An error occurred while retrieving chat history: {str(e)}")