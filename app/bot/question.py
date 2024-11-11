from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from app.bot.vector_db import search_similar


load_dotenv()

OPENAI_API_KEY = os.getenv('OPEN_API_KEY')
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

model = ChatOpenAI(model="gpt-4-turbo-preview", api_key=OPENAI_API_KEY) #, streaming=True

chain = prompt | model

async def ask_question(question: str):
    messages = []

    messages.append(
        AIMessage(content=search_similar(question))
    )

    messages.append(
        HumanMessage(content=question)
    )

    response = chain.astream({"messages": messages})

    async for chunk in response:
        content = chunk.content
        yield content