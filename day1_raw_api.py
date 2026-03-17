import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "I am building an AI resume coach app using LangChain and Claude. In 3 sentences, explain what a context window is and why a larger context window matters for my app."
        }
    ]
)

print(message.content[0].text)