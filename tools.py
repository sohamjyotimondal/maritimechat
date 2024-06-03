from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import List
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from tokenizer import GraphQLClient
from risks import Query
import pandas as pd

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
    '''This tool is used to get the details of a list of vessels by their imo numbers. The input is a list of imo numbers. The output is a list of dictionaries with the details of the vessels.S'''
    name="vesselsByImos"
    description="This tool is used to get the risk data about a vessel by its imo number. Use when the imo number is given"
    

    def _run(self, imos: vesselInput):
        if imos is None:
            return "Ask user this question : What is the imo number of the vessel you want to get the details of?"
        else :
            url = os.getenv("URL")
            clientID = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            interval = os.getenv("INTERVAL")
            query=Query(GraphQLClient(url, clientID, client_secret,interval=interval))
            data=[]
            for imo_ in imos:
                response=query.check_risk(imo_)
                response=response.json()
                if response['data']['vesselByIMO'] is None:
                    return {"data":{"response":f"No data found for the given IMO number {imo_} as it is wrong ask user to provide a valid imo number"}}
                else:
                    data.append(response['data'])
            return {"data":str(data)}
            

class getAreaPolygonId(BaseTool):
    '''Use this to get the polygon id of a given area.
    Mention the areatype as 'Port' or 'Country' and the area as the name of the place
    '''
    name="getAreaPolygonId"
    description="This tool is used to get a list of polygon ids of any given area. Use when the name of a place is given"


    def _run(self, area: str, areaType: str):
        if area is None:
            return "Ask user this question : What Areas do you want the search to be in?"
        else :
            df=pd.read_csv('areaspermitted.csv')
            #select te row where the country areaType column is equal to the area input given
            df=df[df['areaType']=='Port']
            #return id column of the df as a list wherever the country column is equal to the area input given
            if areaType=='country':
                data= df['id'][df['country']==area].tolist() 
                if data==[]:
                    data="No data found for the given area as it is wrong ask user to provide a valid area name"  
                return {"data":{"response":data}}
            elif areaType=='port': #return id column wherever name matches and area type is port
                data=df['id'][df['name']==area].tolist() 
                if data==[]:
                    data="No data found for the given area as it is wrong ask user to provide a valid area name" 
                return {"data":{"response":data}}

class vesselsInPort(BaseTool):
    '''This tool is used to get the vessels in a port within a polygon. The input is the polygon id of the port, the limit of the activities to return which is default to 100, and the offset to start the activities from which is default to 0. The output is the response from the graphql endpoint with the vessels in the port.'''
    name="vesselsInPort"
    description="This tool is used to get the vessels in a port within a given timeframe and a polygon. Use when the polygon id of the port is given"

    def _run(self, polygonID: str, limit: int=100, offset: int=0):
        url = os.getenv("URL")
        clientID = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        interval = os.getenv("INTERVAL")
        query=Query(GraphQLClient(url, clientID, client_secret,interval=interval))
        response=query.vesselsInPort(polygonID,limit,offset)
        response=response.json()
        return str(response)


class Decompose(BaseTool):
    '''always use this tools to decompose a question  into smaller parts that require the other tools
    This helps to solve the question by dealing with the subquestions.'''
    name="Decompose_question"
    description="always Use this tool to first decompose a question when it is regarding maritime insights and vessel risk or location into subquestions that can be answered by the graphql endpoint."
    # question: str = Field(description="The question to decompose")

    def _run(self,question):
        decomposer=Decomposer()
        response = decomposer.decompose_question(question)
        return response.model_dump_json()
    
alltools=[getAreaPolygonId(),vesselsByImos(),vesselsInPort()]
decomposetools=[Decompose()]