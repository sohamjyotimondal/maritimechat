from tokenizer import GraphQLClient
from queries import *
from typing import Union
import requests
import os
import json
from datetime import datetime
import asyncio


class Query():
    '''This class contains all the functions to send requests to the graphql endpoint

        Args:
        ----------------
        client: GraphQLClient
            The GraphQl client object to send requests to the graphql endpoint
        
        Methods:
        ----------------
        convert_to_iso_format(year:int, month:int, day:int)->str:
            Converts the date to iso format. Input is of format year-month-day

        check_risk(imo:str)->dict:
            This async function sends a request to the graphql endpoint to check the risk of a vessel
            The function uses a decorator to check if the token is valid and if not, it refreshes the token

        activities():
            This async function sends a request to the graphql endpoint to get the activities of a vessel within a
            given timeframe and a polygon given as coordinates.
            The function uses a decorator to check if the token is valid and if not, it refreshes the token
    '''
    def __init__(self,client:GraphQLClient):
        self.client=client
    
    def convert_to_iso_format(self,year, month, day):
        '''Converts the date to iso format. Input is of format year-month-day
        
        Args:
        ----------------
            year: int ,The year of the date
            month: int ,The month of the date
            day: int ,The day of the date
            
        Returns:
        ----------------
            str: The date in iso format
        '''
        
        dt = datetime(year, month, day)
        iso_date = dt.isoformat()
        return iso_date

        
    def check_risk(self, imo: str):
        '''This async function sends a request to the graphql endpoint to check the risk of a vessel

        Arguments
        ----------------
            imo: str
            The IMO number of the vessel

        Returns
        ----------------
            dict: The response from the graphql endpoint with the risk of the vessel
            '''
        @self.client.check_token(makelogs=True) #This decorator checks if the token is valid and if not, it refreshes the token
        def send_request():
            query_string=risk_assessment_query_string() #get the query string to send
            payload = {
                "query": query_string,
                "variables": {
                    "imo": f"{imo}"
                }
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client.auth_token}" #get auth token from the GraphQl client object
            }

            # response = await asyncio.to_thread(requests.post, self.client.url, json=payload, headers=headers)
            response=requests.post(self.client.url, json=payload, headers=headers)
            return response

        return send_request()
    
    def activities(self,imo:Union[str,int],from_date:str,to_date:str,polygon:list[list],offset=0,limit=100,includePropertyChanges=True):
        """This async function sends a request to the graphql endpoint to get the activities of a vessel within a given timeframe and a polygon
        
        Arguments
        ----------------
        imo: Union[str,int]
            The IMO number of the vessel
        from_date: str
            The start date of the time frame formatted as year-month-day str
        to_date: str
            The end date of time frame formatted as year-month-day str
        polygon: list[list]
            The coordinates for the polygon passed as a list conatining each individual lat and logitude as lists within it
        offset: int
            The offset to start the activities from
        limit: int
            The number of activities to return. The max limit is 500
        includePropertyChanges: bool
            Whether to include the property changes in the activities

        Returns
        ----------------
            dict: The response from the graphql endpoint with the activities of the vessel
        """
        @self.client.check_token(makelogs=True) #This decorator checks if the token is valid and if not, it refreshes the token
        def send_request():
            query_string=activities_query_string() #get the query string to send to the endpoint

            from_datestr=self.convert_to_iso_format(*map(int,from_date.split("-")))#format the dates to iso format
            to_datestr=self.convert_to_iso_format(*map(int,to_date.split("-")))

            variables = activities_input(includePropertyChanges=includePropertyChanges,limit=limit,offset=offset,from_date=from_datestr,to_date=to_datestr,vesselIdOrImo=imo,coordinates=polygon)
            #27/04/2024 properly format the variables to send in the payload

            payload = {
                "query": query_string,
                "variables": variables
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client.auth_token}"
            }

            # response = await asyncio.to_thread(requests.post, self.client.url, json=payload, headers=headers)
            response=requests.post(self.client.url, json=payload, headers=headers)
            return response

        return send_request()

if __name__ == "__main__":
    #get the environment variables
    client_secret = os.getenv("CLIENT_SECRET")
    clientID = os.getenv("CLIENT_ID")
    url=os.getenv("URL")
    interval=os.getenv("REQUEST_INTERVAL")

    query=Query(GraphQLClient(url, clientID, client_secret,interval=interval))#make a Query object with  GraphQl client object
    print(query.check_risk("979").json())
    # response = asyncio.run(query.check_risk("9738909")) #get the risk associated with the vessel with IMO number 9738909 by using the query object
    # activity=asyncio.run(query.activities(imo="9738909",from_date="2021-01-01",to_date="2021-12-31",polygon=[[113.258057,19.823202],[113.258057,23.007113],[120.629883,23.007113],[120.629883,19.823202],[113.258057,19.823202]]))
    
    # with open ("risk.json","w") as f:
    #     json.dump(response.json(),f,indent=4) #save the response of risk in a json file
    # with open ("activities.json","w") as f:
    #     json.dump(activity.json(),f,indent=4) #save the response of activities in a json file
   