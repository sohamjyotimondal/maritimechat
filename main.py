from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from tools import *

from langchain.tools.render import render_text_description

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class chatBot:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", api_key=api_key,temperature=0)

    def get_response(self, message):
        response = self.chat.get_response(message)
        return response