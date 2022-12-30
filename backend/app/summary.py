import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize(text):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt= text + '\n\nTl;dr',
    temperature=0.7,
    max_tokens=60,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=1
    )

    text = response['choices'][0]['text'].lstrip(' :\n')
    return text
