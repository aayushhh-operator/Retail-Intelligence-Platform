"""LLM Integration using Groq."""
from groq import Groq
from ai.config import GROQ_API_KEY, MODEL_NAME

def get_groq_client():
    return Groq(api_key=GROQ_API_KEY)

def generate_completion(messages: list, stream: bool = False):
    client = get_groq_client()
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.1,
        max_completion_tokens=1024,
        top_p=1,
        stream=stream,
        stop=None
    )
    if stream:
        return completion
    return completion.choices[0].message.content
