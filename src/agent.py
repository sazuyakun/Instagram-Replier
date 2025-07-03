from langgraph import StateGraph, START, END
from instagram import InstagramClient
from llm import LLM
from utils.utils import load_processed, save_processed

class Agent:
    """
    Orchestrates fetching, generating and replying.
    """
    def __init__(self):
        self.instagram_client = InstagramClient()
        self.llm = LLM()
        self.processed = load_processed()
