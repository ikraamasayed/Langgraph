# CONTEXT MEMORY AGENT 

from typing import TypedDict , List ,Union
from langgraph.graph import StateGraph , START, END
from langchain_core.messages import HumanMessage,AIMessage
from langchain_ollama import ChatOllama
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os

load_dotenv()

# model = chat_models(model="kimi-k2.6:cloud")

class AgentState(TypedDict):
    messages:List[Union[HumanMessage,AIMessage]]


model=os.getenv("model")
base_url=os.getenv("base_url")
api_key=os.getenv("api_key")
# llm = ChatOllama(model='gemma3:4b')
llm = ChatNVIDIA(model=model,base_url=base_url,api_key=api_key)


def process(state:AgentState)->AgentState:
    response = llm.invoke(state['messages'])
    state["messages"].append(AIMessage(content=response.content))
    print(f"AI : {response.content}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process",END)

agent = graph.compile()


conversation_history =[]

user_input = input(f'Enter: ')
while user_input!= "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages":conversation_history})
    conversation_history = result['messages']
    user_input = input(f'Enter: ')
    

with open("logging.txt","w",encoding="utf-8",errors="ignore") as file :
    file.write("Your Conversation LOG: \n")

    for message in conversation_history:
        if isinstance(message,HumanMessage):
            file.write(f"YOU :{message.content} \n")
        elif isinstance(message,AIMessage):
            file.write(f"AI :{message.content} \n\n")

    file.write("End of Conversation")

print(f"Conversation saved to logging.txt")