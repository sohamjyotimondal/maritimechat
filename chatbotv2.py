from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from tools import alltools
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_structured_chat_agent
from langchain.tools.render import render_text_description
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class chatBot:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", api_key=api_key,temperature=0)
        self.chat_history = [AIMessage(content="Hello! How can I assist you today?")]
        agent = create_structured_chat_agent(self.llm, alltools, prompt=self._makeprompt_(self.chat_history))
        self.chatbot = AgentExecutor(agent=agent,tools=alltools, verbose=True,return_intermediate_steps=True,
                               handle_parsing_errors=True,
                               max_iterations=5)


    def _makeprompt_(self,chat_history):
        '''This method creates a prompt for the chatbot to use
        Parameters:
        ------------
        chat_history: list
            The chat history of the conversation
            
        Returns:
        ------------
        prompt: ChatPromptTemplate
            The prompt to be used by the chatbot to ask the user for input and to answer the question'''
        
        prompt = ChatPromptTemplate.from_messages(
      [
          ("system", """
                        You are an maritime assistant made by the Pythian team and only answer to maritime questions and questions about vessels
                            If you do not have a tool to answer the question break down the questions using decomposer tool to finally reach the answer.
                                    If any information you need to answer the question is missing ask from the user then answer the question 
                            Respond to the human as helpfully and accurately as possible. You have access to the following tools:
                If you need any additional information to answer the question, feel free to answer with a question you want to ask.
                        The final answer can be a paragraph  or even a single sentence but not a markdown. There can also be incomplete responses or invalid responses.
                            in the final answer that isn't a problem.
                {tools}

                Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

                Valid "action" values: "Final Answer" or {tool_names}

                Provide only ONE action per $JSON_BLOB, as shown:

                ```
                {{
                "action": $TOOL_NAME,
                "action_input": $INPUT
                }}
                ```

                Follow this format:

                Question: input question to answer
                Thought: consider previous and subsequent steps
                Action:
                ```
                $JSON_BLOB
                ```
                Observation: action result
                ... (repeat Thought/Action/Observation N times only if you cannot reach the answer.)
                        Make sure that there is nothing inside ``` to  ``` which would create a parsing error, such as text like "json" or "python".
                Thought: I know what to respond
                Action:
                ```
                {{
                "action": "Final Answer",
                "action_input": "Final response to human"
                }}

                """),

          ("human", """{input} 
           
           chat history: 
           {agent_scratchpad} 
           Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate incomplete response or invalid response is also a good response.
            Format is Action:```$JSON_BLOB```then Observation"""),
           ("system", "The input arguments are always json blob but the output is not necessarily json so act accordingly to take the best bath to provide an answer in minimal steps")
          
      ]
  )
        prompt = prompt.partial(
            agent_scratchpad=(chat_history),
            tools=render_text_description(alltools),
            tool_names=", ".join([t.name for t in alltools]),
            )
        return prompt
    
    def _updatechat_history_(self,response):
        self.chat_history.append(HumanMessage(content=response['input']))
        # if 'intermediate_steps' in response:
        #     for step in response['intermediate_steps']:
        #         self.chat_history.append(AIMessage(content=step))
        self.chat_history.append(AIMessage(content=str(response['output'])))
        return self.chat_history
    
    def get_response(self, message):
        response=(self.chatbot.invoke({"input":message,'chat_history':self.chat_history}))
        self._updatechat_history_(response) #update the chat history with current response
        return response['output']
    
if __name__ == "__main__":
    bot = chatBot()
    print(bot.get_response("What is the risk with vessel 9746619"))
    print(bot.chat_history)