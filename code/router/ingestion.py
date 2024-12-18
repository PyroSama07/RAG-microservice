from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..dependency import get_client, get_text_splitter, get_emb_client, get_name
import os
from dotenv import load_dotenv
from ollama import AsyncClient
import logging

logger = logging.getLogger()

load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBEDDING_NAME=os.getenv("EMBEDDING_NAME")
FASTAPI_URL = os.getenv("FASTAPI_URL")

class Payload(BaseModel):
    name: str
    content: str

router = APIRouter(prefix="/data")

@router.put("/addDocument")
async def add_documents(
    file: UploadFile = File(...),
    client: AsyncQdrantClient = Depends(get_client),
    text_splitter: RecursiveCharacterTextSplitter = Depends(get_text_splitter),
    emb_client: AsyncClient = Depends(get_emb_client),
) -> dict:
    content = file.file.read().decode("utf-8")
    filename = await get_name(file.filename,client)
    payload = []
    splits = text_splitter.split_text(content)
    vector = await emb_client.embed(model=EMBEDDING_NAME,input=splits)
    for split in splits:
        payload.append(Payload(name=filename,content=split).model_dump())
    client.upload_collection(
        collection_name=COLLECTION_NAME,
        payload=payload,
        vectors=vector.embeddings,
    )
    return {"Status": f"{filename} added"}
