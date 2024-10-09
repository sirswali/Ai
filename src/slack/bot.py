from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .handlers import SlackHandlers
import config

class SlackBot:
    def __init__(self, components, bot_token, signing_secret):
        self.app = App(token=bot_token, signing_secret=signing_secret)
        self.handlers = SlackHandlers(components)
        self._register_handlers()

    def _register_handlers(self):
        # Register slash command handlers
        self.app.command("/allocate_task")(self.handlers.handle_task_allocation)
        self.app.command("/workload_report")(self.handlers.handle_workload_report)
        self.app.command("/reallocate_tasks")(self.handlers.handle_task_reallocation)
        self.app.command("/kb_add")(self.handlers.handle_kb_add)
        self.app.command("/kb_search")(self.handlers.handle_kb_search)
        self.app.command("/kb_update")(self.handlers.handle_kb_update)
        self.app.command("/kb_delete")(self.handlers.handle_kb_delete)
        self.app.command("/kb_info")(self.handlers.handle_kb_info)
        self.app.command("/summarize")(self.handlers.handle_summarize)
        self.app.command("/semantic_search")(self.handlers.handle_semantic_search)
        self.app.command("/analyze_task")(self.handlers.handle_task_analysis)
        self.app.command("/match_task")(self.handlers.handle_task_matching)
        self.app.command("/recent_activities")(self.handlers.handle_recent_activities)

        # New monitoring handlers
        self.app.command("/monitor_slack")(self.handlers.handle_monitor_slack)
        self.app.command("/monitor_jira")(self.handlers.handle_monitor_jira)

        # Register app mention handler
        self.app.event("app_mention")(self.handlers.handle_mentions)

        # Register direct message handler
        self.app.event("message")(self.handlers.handle_message)

        # Register interactive component handler (for feedback)
        self.app.action("rate_response")(self.handlers.handle_feedback)

    def start(self):
        handler = SocketModeHandler(self.app, config.SLACK_APP_TOKEN)
        handler.start()

    def send_message(self, channel, text, blocks=None):
        self.app.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )

    def update_message(self, channel, ts, text, blocks=None):
        self.app.client.chat_update(
            channel=channel,
            ts=ts,
            text=text,
            blocks=blocks
        )