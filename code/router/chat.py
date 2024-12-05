from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from qdrant_client import AsyncQdrantClient
from ollama import AsyncClient
from pydantic import BaseModel
from typing import AsyncGenerator
from ..dependency import get_client, get_emb_client
import os
from dotenv import load_dotenv

import logging
logger = logging.getLogger()

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
EMBEDDING_NAME=os.getenv("EMBEDDING_NAME")

class Question(BaseModel):
    question: str

router = APIRouter(prefix='/chat')

@router.post("/answer/")
async def rag_answer(
    question: Question,
    emb_client: AsyncClient = Depends(get_emb_client),
    client: AsyncQdrantClient = Depends(get_client),
    ) -> StreamingResponse:
    embed = await emb_client.embed(model=EMBEDDING_NAME,input=question.question)
    vector = embed.embeddings[0]
    payload = await client.query_points(
                    collection_name="my_books",
                    query=vector,
                    limit=1,
                ).points
    payload = payload[0].payload
    context = payload["content"]
    filename = payload["name"]
    messages = [
                {"role": "system", 
                        "content": 
                        f'''You are a RAG chatbot. Answer the question based on given context. If incorrect context return "NOT FOUND". 
                        context: {context}
                        file name: {filename}
                        Also give the file name at the last of the reply in a new line in format only if context is correct.
                        Found in File: <file name>'''},
                {"role": "user", 
                        "content": 
                        f'''{question}'''},
                ]
    
    async def generate_response() -> AsyncGenerator[str, None]:
        response=""
        async for part in await emb_client.chat(model=MODEL_NAME, messages=messages, stream=True):
            yield part["message"]["content"]
            # logger.debug(f"Streamed chunk: {part['message']['content']}")
            response = response + part['message']['content']
        logger.info(f'Respose final: {response}')

    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
    )

    # response = await emb_client.chat(model='mistral:7b-instruct', messages=messages)
    # logger.info(response)
    # return {"response":response['message']['content']}