from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import List
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from tokenizer import GraphQLClient
from risks import Query

from typing import Optional
from openai import OpenAI
from decomposer import Decomposer

import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd


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


class Endpoint(BaseModel):
    '''This is the individual subquestion that is to be answered'''
    
    query: str = Field(..., description="The subquery")
    endpoint: List[str] = Field(..., description="The graphql endpoint that is required to fetch data from the ai to answer this specific question")
    arguments: List[str] = Field(..., description="The parameters that are required to send in the query request to the endpoint")
    


class Answer(BaseTool):
    name = "Answerafterdecomposition"
    description = "This tool is used to answer the subquestions that are decomposed from the main question. This is used after a question is decomposed. This takes in the plan as a list of dictionaries."
    psubquestion: Optional[Endpoint]=Field(description="A subquestion that is decomposed from the main question which needs to be answered")
    def _run(self, subquery:Endpoint):
        '''the subquestion is a dictionary from the list of dictionaries in plan'''
        print(subquery)
        return "rajmohini1"

class vesselInput(BaseModel):
    imos: List[str] = Field(description="The imo numbers of the vessels to get the details of")

    
class vesselsByImos(BaseTool):
    name="vesselsByImos"
    description="This tool is used to get the risk data about a vessel by its imo number. Use when the imo number is given"
    

    def _run(self, imos: vesselInput):
        if imos.imos is None:
            return "Ask user this question : What is the imo number of the vessel you want to get the details of?"
        else :
            url = os.getenv("URL")
            clientID = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            interval = os.getenv("INTERVAL")
            query=Query(GraphQLClient(url, clientID, client_secret,interval=interval))
            data=[]
            for imo in imos.imos:
                response=query.check_risk(imo)
                response=response.json()
                if response['data']['vesselByIMO'] is None:
                    return {"data":{"response":f"No data found for the given IMO number {imo} as it is wrong ask user to provide a valid imo number"}}
                else:
                    data.append(response['data']['vesselByIMO'])
            return data
            
class areaInput(BaseModel):
    area: str = Field(description="The area to get the polygon ids of")
    areaType: str = Field(description="The type of area is a 'Port' or a 'Country'")

class getAreaPolygonId(BaseTool):
    name="Getareapolygoinid"
    description="This tool is used to get a list of polygon ids of any given area. Use when the name of a place is given"


    def _run(self, area: areaInput):
        if area.area is None:
            return "Ask user this question : What Areas do you want the search to be in?"
        else :
            if area.areaType.lower() == "port":
                return "5358fc78b68ca120a07dbb89"
            elif area.areaType.lower() == "country":
                return "5358fc78b68ca120a07dbb89"

class Decompose(BaseTool):
    name="Decomposequestion"
    description="always Use this tool to first decompose a question when it is regarding maritime insights and vessel risk or location into subquestions that can be answered by the graphql endpoint."
    # question: str = Field(description="The question to decompose")

    def _run(self,question):
        decomposer=Decomposer()
        response = decomposer.decompose_question(question)
        return response.model_dump_json()
    
tools=[getAreaPolygonId(),Decompose(),vesselsByImos()]