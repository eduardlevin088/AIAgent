from openai import OpenAI
from config import GPT_KEY

client = OpenAI(api_key=GPT_KEY)


def new_conversation():
    conversation = client.conversations.create()
    return conversation.id