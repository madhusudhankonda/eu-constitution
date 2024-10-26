import os
from openai import AzureOpenAI

from client_util import get_azure_openai_client

client = get_azure_openai_client()

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "What is AI?",  # Your question can go here
        },
    ],
)

print(completion.choices[0].message.content)