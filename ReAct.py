from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content and tl
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.tools import tool
from langgraph.graph.message import add_messages # is a reducer func allows to append msg to state
from langgraph.graph import StateGraph, END
from langgraph. prebuilt import ToolNode
import os
load_dotenv()


class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage],add_messages] # seq of basemsg is datatype and add_msg is medidator

@tool 
def add(a:int , b:int):
    """
    Add two integers.

    Inputs:
        a: first integer
        b: second integer

    Returns:
        Sum of a and b.
    """
    return a+b

@tool
def subtract(a: int, b: int):
    """
    subtract two integers.

    Inputs:
        a: first integer
        b: second integer

    Returns:
        Subtraction of a and b.
    """
    return a - b

@tool
def multiply(a: int, b: int):
    """
    Multiple two integers.

    Inputs:
        a: first integer
        b: second integer

    Returns:
        Multiple of a and b.
    """
    return a * b

tools = [add,subtract,multiply]


model=os.getenv("tool_model")
base_url=os.getenv("tool_model_base_url")
api_key=os.getenv("tool_model_api_key")
# llm = ChatOllama(model='gemma3:4b')
print(model)
print(base_url)
print(api_key)


llm = ChatNVIDIA(model="meta/llama-3.1-8b-instruct",base_url=base_url,api_key=api_key,timeout=120).bind_tools(tools=tools,tool_choice="auto",parallel_tool_calls=False)

def model_call(state:AgentState):
    system_prompt = SystemMessage(content=
                                  """You are a ReAct agent.
                                  Use at most ONE tool call per assistant message.
                                  After receiving a tool result, decide whether another tool is required.
                                  Do not reference future tool outputs such as "result_of_add". Wait for the actual tool response before making another tool call.
                                  After all required tool calls are complete, provide a final answer to the user.
                                  """
                                  )
    response = llm.invoke([system_prompt]+ state["messages"])
    return {"messages":[response]}

def should_continue(state:AgentState):
    message = state["messages"]
    last_message = message[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)
graph.add_node("our_agent",model_call)

tool_node= ToolNode(tools=tools)
graph.add_node('tools',tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {"end":END,
     "continue":"tools"
    },
)

graph.add_edge("tools","our_agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"] [-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Add 40 + 12 and then multiply the result by 6. Also tell me a joke please")]}
print_stream(app.stream(inputs,stream_mode="values"))
