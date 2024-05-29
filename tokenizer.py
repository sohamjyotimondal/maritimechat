import requests
import json
import time
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

class GraphQLClient:

    '''This create a GraphQL client object to send requests to the graphql endpoint.
    
    Class Variables:
    ----------------
        url: str
        The url of the graphql mutation endpoint to get the token

        auth_token: str
        The token to authenticate queries by passing as bearer token in authorization

        last_request_time: float
        The time of the last request made. This is useful to track the time when a new token is needed

        retry: bool
        A flag to check if the the last request failed and needs to be retried

        interval: float
        The interval at which the requests are to be made. If the last request was made before this interval,
        a new token is needed

        variable: dict
        The variable needed in the request payload. It contains the clientID and client_secret

    Methods:
    ----------------
        get_token(makelogs:bool=True)->str:
            This method sends a request to the graphql endpoint to get the token. 

        check_token(makelogs:bool=True):
            This method is a decorator to check if the token is valid before making a request. 
            If the token is not valid, it refreshes the token


        start_timed_requests(makelogs:bool=True):
            This method starts a loop to make requests at regular intervals when a seperate thread can
            be used for renewing the token
        '''
    
    def __init__(self, url:str ,clientID:str , client_secret:str,interval):
   
        self.url = url
        self.auth_token=None
        self.last_request_time = 0
        self.retry=False 
        self.interval=interval

        self.variable={
                "clientId": f"{clientID}",
                "clientSecret": f"{client_secret}"
                }

    def get_token(self,makelogs=True):
        '''async method to get the token from the graphql endpoint. Sets retry flag to True if the request fails.
        
        Args:
        ----------------
            makelogs: bool
            A flag to check if logs are to be made. If True, logs are made in the logs.txt file
            
        Returns:
        ----------------
            str: The token to be used in the authorization header or None if the request fails'''
        payload = {
            "query": """
            mutation PublicAPIToken($clientId: String!, $clientSecret: String!) {
            publicAPIToken(clientId: $clientId, clientSecret: $clientSecret)
            } """,
            "variables": self.variable
            }
        
        headers = { #headers to send with the request
            "Content-Type": "application/json",
            "Authorization": f"Bearer{self.auth_token}"
            }

        # response = await asyncio.to_thread(requests.post, self.url, json=payload, headers=headers)
        response=requests.post(self.url, json=payload, headers=headers)
        self.last_request_time=time.time()

        if response.status_code == 200:
            data = response.json() #get the response in json format 
            self.auth_token=data['data']['publicAPIToken'] #get the token from the response
            if makelogs:
                with open("logs.txt","a") as f:
                    f.write(f"Request made at {time.ctime()} with status code {response.status_code}\n token: {self.auth_token}\n\n")
            self.retry=False
            return self.auth_token
        else:
            if makelogs:
                with open("logs.txt","a") as f:
                    f.write(f"Request made at {time.ctime()} with status code {response.status_code}\n\n error: {response.text}\n\n")
            self.auth_token=None
            self.retry=True
            return False

    def start_timed_requests(self,makelogs=True):
        '''async method for making requests at regular intervals'''
        while True:
            
            if self.auth_token is None or time.time()-self.last_request_time>self.interval:
                self.get_token(makelogs)
            
            if not self.retry:
                # await asyncio.sleep(interval)
                time.sleep(self.interval)
        
    def check_token(self, makelogs=True):
        '''Decorator for renewing token before making a request
        
        Args:
        ----------------
            makelogs: bool
            A flag to check if logs are to be made. If True, logs are made in the logs.txt file
            '''
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.auth_token is None or time.time() - self.last_request_time > float(self.interval):
                    self.get_token(makelogs)    
                return func(*args, **kwargs)
            return wrapper
        return decorator
        
# Example usage
if __name__ == "__main__":
    
    client_secret = os.getenv("CLIENT_SECRET")
    clientID = os.getenv("CLIENT_ID")
    url=os.getenv("URL")
    interval=os.getenv("REQUEST_INTERVAL")
    client = GraphQLClient(url, clientID, client_secret,interval)
    
    # client.start_timed_requests(int(reqtime),makelogs=True)
    
    # asyncio.run(client.start_timed_requests(makelogs=True))