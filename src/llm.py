from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

class LLM:
    """
    Handles the LLM operations.
    """
    def __init__(self):
        self.llm = init_chat_model("google_genai:gemini-2.0-flash")

    def generate_response(self, message):
        """
        Generate a response from the LLM based on the provided prompt.
        """
        prompt = f"Write a short friendly reply to the following message: {message}"
        response = self.llm.invoke(prompt)
        return response if response else None
