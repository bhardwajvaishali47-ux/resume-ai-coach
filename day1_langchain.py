import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

messages = [
    SystemMessage(content="You are an expert AI career coach specialising in tech roles and resume optimisation."),
    HumanMessage(content="I am building an AI resume coach app using LangChain and Claude. In 3 sentences, explain what a context window is and why a larger context window matters for my app.")
]

response = llm.invoke(messages)

print(response.content)