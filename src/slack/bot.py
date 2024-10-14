from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .handlers import SlackHandlers
from utils.logging.logger import CustomLogger
import config
from llm.wrapper import LLMWrapper
from datetime import datetime

class SlackBot:
    def __init__(self, components, bot_token, signing_secret):

        logger = CustomLogger('SlackBot').get_logger()
        logger.info("Initializing Slack bot...")
      
        self.app = App(token=bot_token, signing_secret=signing_secret)
        self.handlers = SlackHandlers(components)
        # self._register_handlers()
        
        # The echo command simply echoes on command
        @self.app.command("/askbot")
        def repeat_text(ack, respond, command):
            # Acknowledge command request
            ack()
            prompt = f"{command['text']}"
            
            # Timestamp
            start = datetime.now()
            # format = '%y/%m/%d %H:%M:%S'
            
            if (prompt.lower() == "what is the answer to the fundamental question about life, the universe and everything else?"):
                respond("The answer to the fundamental question about life, the universe and everything else is 42.")
                # logger.info(f"/askbot triggered:\nPrompt: {prompt}")
            else:
                logger.info(f"/askbot triggered:")
                llm = components["llm"]
                
                # Prompt feedback
                logger.info(f"Prompt: {prompt}")
                respond(f"Prompt: {prompt}")
                
                # Generate answer
                answer = llm.generate_response(prompt)
                
                # Elapsed time
                end = datetime.now()
                timeDiff = end - start
                
                # Provide answer
                respond(f"Answer:{answer}")
                logger.info(f"Answer: [{timeDiff}]\n{answer}")


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