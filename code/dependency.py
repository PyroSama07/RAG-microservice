from fastapi import Request
from qdrant_client import QdrantClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ollama import AsyncClient

def get_client(request: Request) -> QdrantClient:    
    return request.app.state.client

def get_text_splitter(request: Request) -> RecursiveCharacterTextSplitter:
    return request.app.state.text_splitter

def get_emb_client(request: Request) -> AsyncClient:
    return request.app.state.emb_client

