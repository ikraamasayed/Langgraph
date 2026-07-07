from typing import TypedDict , List
from langgraph.graph import StateGraph , START, END
from langchain_core.messages import HumanMessage,BaseMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os
load_dotenv()

# model = chat_models(model="kimi-k2.6:cloud")
model = os.getenv("model")
api_key= os.getenv("api_key")
base_url = os.getenv("base_url").rstrip('/')

class AgentState(TypedDict):
    messages:List[BaseMessage]


# llm = ChatOllama(model='ornith:9b')
llm = ChatNVIDIA(model=model, api_key=api_key,base_url=base_url,timeout= 120)
# #Does not work's with NIM api 
# llm = ChatOpenAI (model=model , api_key=api_key,base_url=base_url,timeout=120) 


def process(state:AgentState)->AgentState:
    response = llm.invoke(state['messages'])
    print(f"AI : {response.content}")
    state["messages"].append(response)

    return state

graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process",END)

agent = graph.compile()

user_input = input(f'Enter: ')
while user_input!= "exit": 
    agent.invoke({"messages":[HumanMessage(content=user_input)]})
    user_input = input(f'Enter: ')
    

