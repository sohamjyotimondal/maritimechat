from langchain.tools import BaseTool
from langchain.tools import Field

import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI


class Circumference(BaseTool):
    # a: int = Field(description="The radius of the circle")
    # b: int = Field(description="second number")
    name="Circumference"
    description="useful for when you need to answer questions about the circumference of a circle. The input is int datatype"

    def validate(self, **kwargs):
        if self.a == 0:
            raise ValueError("a cannot be 0")
        return super().validate(**kwargs)
    
    def _run(self,r):
        return 3.14 * 2 * float(r)
    
class Answer(BaseTool):
    name="Answer"
    description="This tool is used to answer questions about any topic"
    question: str = Field(description="The question to answer. Contains all the combined important points gained throughout the conversation")
    def _run(self,question):
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant and will answer this question to the best of your knowledge"},
            {"role": "user", "content": question},
        ]
        )
        return (response.choices[0].message['content'])
    
class Fetchfromapi(BaseTool):
    name="Fetchfromapi"
    description="This tool is used to fetch data from an API"
    url: str = Field(description="The url of the API")
    def _run(self,url):
        import requests
        response = requests.get(url)
        return response.json()