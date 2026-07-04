from typing import TypedDict , List ,Union
from langgraph.graph import StateGraph , START, END
from langchain_core.messages import HumanMessage,AIMessage
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

# model = chat_models(model="kimi-k2.6:cloud")

class AgentState(TypedDict):
    messages:List[Union[HumanMessage,AIMessage]]


llm = ChatOllama(model='gemma3:4b')


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
    

with open("logging.txt","w") as file :
    file.write("Your Conversation LOG: \n")

    for message in conversation_history:
        if isinstance(message,HumanMessage):
            file.write(f"YOU :{message.content} \n")
        elif isinstance(message,AIMessage):
            file.write(f"AI :{message.content} \n\n")

    file.write("End of Conversation")

print(f"Conversation saved to logging.txt")