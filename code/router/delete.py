from fastapi import APIRouter, Depends, FastAPI
from qdrant_client import AsyncQdrantClient, models
from ..dependency import get_client
import os
from dotenv import load_dotenv

load_dotenv()
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

router = APIRouter(prefix="/data")

@router.delete("/delete/{document_name}")
async def delete_document(
    document_name: str,
    client: AsyncQdrantClient = Depends(get_client),
) -> dict:
    await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="name",
                        match=models.MatchValue(value=document_name),
                    ),
                ],
            )
        ),
    )
    return {"Status": f"{document_name} deleted"}

@router.delete("/delete_all")
async def delete_all_document(
    client: AsyncQdrantClient = Depends(get_client),
) -> dict:
    await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(must=[])
        ),
    )
    return {"Status": f"All Documents deleted"}