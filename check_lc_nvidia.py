from openai import OpenAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os
load_dotenv()
model="meta/llama-3.1-8b-instruct"
base_url=os.getenv("tool_model_base_url")
api_key=os.getenv("tool_model_api_key")
# llm = ChatOllama(model='gemma3:4b')
print(model)
print(base_url)
# print(api_key)

llm = ChatNVIDIA(
    model="meta/llama-3.1-8b-instruct",
    base_url=base_url,
    api_key=api_key,
).bind_tools

print(llm.invoke("Say hello."))

# response = client.chat.completions.create(
#     model="meta/llama-3.3-70b-instruct",
#     messages=[
#         {"role": "user", "content": "Say hello"}
#     ],
# )




# print(client.choices[0].message.content)