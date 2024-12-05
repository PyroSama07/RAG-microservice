from fastapi import FastAPI, File
from contextlib import asynccontextmanager
from qdrant_client import models, AsyncQdrantClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging 
import os
from dotenv import load_dotenv
from .router import ingestion, delete, chat, retrieval
from ollama import AsyncClient

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger()

load_dotenv()
QDRANT_URL = os.getenv('QDRANT_URL')
OLLAMA_URL=os.getenv("OLLAMA_URL")
COLLECTION_NAME=os.getenv('COLLECTION_NAME')
EMBEDDING_SIZE=os.getenv('EMBEDDING_SIZE')

@asynccontextmanager
async def lifespan(app: FastAPI):
    emb_client = AsyncClient(host=OLLAMA_URL,timeout=120)
    logger.debug("Embeddings initialized")
    client = AsyncQdrantClient(QDRANT_URL,timeout=60)
    if not await client.collection_exists(collection_name=COLLECTION_NAME):
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=int(EMBEDDING_SIZE),
                distance=models.Distance.COSINE,
            ),
        )
        logger.debug("Collection Created")
    else:
        logger.debug("Collection Already existed")
    
    await client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="name",
        field_schema=models.PayloadSchemaType.TEXT,
        )
    logger.debug("Index created")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    app.state.client = client
    app.state.text_splitter = text_splitter
    app.state.emb_client = emb_client

    try:
        yield
    finally:
        del app.state.client 
        del app.state.text_splitter
        del app.state.emb_client

app = FastAPI(lifespan=lifespan)
app.include_router(ingestion.router)
app.include_router(delete.router)
app.include_router(chat.router)
app.include_router(retrieval.router)

@app.get("/")
def read_root():
    return {"message": "RAG Application"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", reload=True, host="127.0.0.1", port=5000)
