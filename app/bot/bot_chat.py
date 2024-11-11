import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.models.user_model import User
from app.bot.embedding_service import search_similar, get_embeddings
from dotenv import load_dotenv
from collections import defaultdict
import httpx
from langchain_openai import OpenAIEmbeddings

load_dotenv()

OPEN_API_KEY = os.getenv('OPEN_API_KEY')

router = APIRouter()

embeddings = OpenAIEmbeddings(api_key=OPEN_API_KEY)

async def chat(prompt: str):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPEN_API_KEY}'
        }
        json_data = {
            'model': 'gpt-4-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 1500,
            'temperature': 0.7
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=json_data
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
    except httpx.RequestError as e:
        logging.error(f"OpenAI API request failed: {e}")
        raise HTTPException(status_code=500, detail=f'Unexpected Error: {e}')

class QueryRequest(BaseModel):
    user_id: int
    query: str
    session_id: str

chat_contexts = defaultdict(list)

@router.post("/query-process/")
async def query_process(request: QueryRequest, db: Session = Depends(get_db)):
    query = request.query
    user_id = request.user_id
    session_id = request.session_id


    context = chat_contexts[(user_id, session_id)]
    context.append({"role": "user", "content": query})

    context_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
    
    
    preprocessed_query = await chat(f"Refine the following query by removing unnecessary stop words and making it more concise: {query}")
    processed_query = preprocessed_query.strip()

    query_embedding = get_embeddings(processed_query)
    print(query_embedding)


    if query_embedding is None:
        raise HTTPException(status_code=500, detail="Failed to generate query embeddings")
    

    matched_data = search_similar(query_embedding)

    if not matched_data:
        raise HTTPException(status_code=404, detail="No relevant Data Found against your query..")
    
    combined_context = context_prompt + "\n\n" + "\n".join([item['content']] for item in matched_data)
    prompt = f"""
    Here is the Context:
    {combined_context}

    User Query: {query}
    Please provide the response with clear separations for each item. If the user query contains multiple keywords, please format each response separately with a keyword and response pair, each followed by a line break. For a single query, provide a comprehensive response with appropriate line breaks:
    """
    

    ai_response = await chat(prompt)
    context.append({"role": "bot", "content": ai_response.strip()})
    generated_response = ai_response.strip()

    return JSONResponse(content={"response": generated_response})