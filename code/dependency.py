from fastapi import Request, Depends
from qdrant_client import AsyncQdrantClient, models
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ollama import AsyncClient
import os
from dotenv import load_dotenv

load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

def get_client(request: Request) -> AsyncQdrantClient:    
    return request.app.state.client

def get_text_splitter(request: Request) -> RecursiveCharacterTextSplitter:
    return request.app.state.text_splitter

def get_emb_client(request: Request) -> AsyncClient:
    return request.app.state.emb_client

async def get_name(
    document_name: str,
    client: AsyncQdrantClient = Depends(get_client)
) -> str:
    value = document_name
    count = 1
    while True:
        response = await client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key="name", match=models.MatchValue(value=value)),
                ]
            ),
            limit=1,
            with_payload=False,
            with_vectors=False,
        )
        if response[0]==list():
            break
            
        temp_list = document_name.split('.')
        temp_list[-1] = f'_{str(count)}.{temp_list[-1]}'
        value = ''.join(temp_list)
        count = count+1

    return value