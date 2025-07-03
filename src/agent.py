from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict, Any
from src.instagram import InstagramClient
from src.llm import llm
from utils.utils import load_processed, save_processed

class AgentState(TypedDict):
    """State for the LangGraph agent"""
    messages: List[Dict[str, Any]]
    current_message: Dict[str, Any]
    is_birthday_message: bool
    reply_text: str
    processed_count: int

class Agent:
    """
    Orchestrates fetching, generating and replying.
    """
    def __init__(self):
        self.instagram_client = InstagramClient()
        self.llm = llm
        self.processed = load_processed()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph = StateGraph(AgentState)

        graph.add_node("fetch_messages", self.fetch_messages)
        graph.add_node("check_birthday", self.check_birthday_message)
        graph.add_node("generate_reply", self.generate_birthday_reply)
        graph.add_node("send_reply", self.send_reply)
        graph.add_node("skip_message", self.skip_message)

        graph.add_edge(START, "fetch_messages")
        graph.add_conditional_edges(
            "fetch_messages",
            self.has_messages_to_process,
            {
                "process": "check_birthday",
                "end": END
            }
        )
        graph.add_conditional_edges(
            "check_birthday",
            self.is_birthday_condition,
            {
                "birthday": "generate_reply",
                "not_birthday": "skip_message"  # Route to skip_message instead
            }
        )
        graph.add_edge("generate_reply", "send_reply")
        graph.add_edge("send_reply", "fetch_messages")
        graph.add_edge("skip_message", "fetch_messages")

        return graph.compile()

    def skip_message(self, state: AgentState) -> AgentState:
        """Skip the current message and move to the next one"""
        user_id = state["current_message"]["user_id"]
        print(f"⏭️ Skipping non-birthday message from user {user_id}")

        self.processed.add(user_id)
        save_processed(self.processed)

        state["processed_count"] += 1
        return state

    def fetch_messages(self, state: AgentState) -> AgentState:
        """Fetch unread messages from Instagram"""
        if not state.get("messages"):
            # First time fetching messages
            try:
                # messages = self.instagram_client.fetch_unread_msgs()
                messages = MESSAGES_

                unprocessed_messages = [
                    msg for msg in messages
                    if msg["user_id"] not in self.processed and msg.get("text") is not None and msg.get("text").strip() != ""
                ]
                state["messages"] = unprocessed_messages
                state["processed_count"] = 0
            except Exception as e:
                print(f"Error fetching messages: {e}")
                state["messages"] = []
                state["processed_count"] = 0

        if state["processed_count"] < len(state["messages"]):
            state["current_message"] = state["messages"][state["processed_count"]]
        else:
            state["current_message"] = None

        return state

    def has_messages_to_process(self, state: AgentState) -> str:
        """Check if there are more messages to process"""
        if (state.get("current_message") and
            state["processed_count"] < len(state.get("messages", []))):
            return "process"
        return "end"

    def check_birthday_message(self, state: AgentState) -> AgentState:
        """Check if the current message is a birthday message"""
        message_text = state["current_message"]["text"]

        birthday_keywords = ["birthday", "happy birthday", "bday", "celebrate", "wishes", "many more"]

        is_birthday = any(keyword.lower() in message_text.lower() for keyword in birthday_keywords)

        prompt = f"Is this message a birthday wish or birthday-related? Respond with only 'yes' or 'no': '{message_text}'"
        llm_response = self.llm.invoke(prompt)
        is_birthday = llm_response.content.lower().strip() == "yes"

        state["is_birthday_message"] = is_birthday
        return state

    def is_birthday_condition(self, state: AgentState) -> str:
        """Conditional edge for birthday messages"""
        return "birthday" if state["is_birthday_message"] else "not_birthday"

    def generate_birthday_reply(self, state: AgentState) -> AgentState:
        """Generate a suitable birthday reply using LLM"""
        original_message = state["current_message"]["text"]

        prompt = f"""
        Generate a warm and personalized birthday reply to this message: "{original_message}"

        Guidelines:
        - Keep it friendly and genuine
        - Make it feel personal, not automated
        - Keep it concise (1-2 sentences)
        - Match the tone of the original message

        Reply:
        """

        reply = self.llm.invoke(prompt)
        state["reply_text"] = reply.content.strip()
        return state

    def send_reply(self, state: AgentState) -> AgentState:
        """Send the generated reply via Instagram DM"""
        user_id = state["current_message"]["user_id"]
        reply_text = state["reply_text"]

        try:
            self.instagram_client.reply_to_dm(user_id, reply_text)
            print(f"Sending reply to user {user_id}: {reply_text}")

            self.processed.add(user_id)
            save_processed(self.processed)

            print(f"✅ Sent birthday reply to user {user_id}: {reply_text}")

        except Exception as e:
            print(f"❌ Failed to send reply to user {user_id}: {str(e)}")

        state["processed_count"] += 1
        return state

    def run(self):
        """Run the agent workflow"""
        initial_state = {
            "messages": [],
            "current_message": None,
            "is_birthday_message": False,
            "reply_text": "",
            "processed_count": 0
        }

        print("🚀 Starting Instagram Birthday Reply Agent...")
        result = self.graph.invoke(initial_state)
        print("✅ Agent workflow completed!")
        return result

# if __name__ == "__main__":
#     agent = Agent()
#     agent.run()
