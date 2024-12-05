from fastapi import APIRouter, Depends
from ..dependency import get_client
from qdrant_client import AsyncQdrantClient, models
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")

router = APIRouter(prefix="/get")

@router.get("/all_points")
async def get_all_points(
    client: AsyncQdrantClient = Depends(get_client)
) -> dict:
    all_points = set()
    scroll_id = None

    while True:
        response = await client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=scroll_id,
            with_payload=["name"],
        )
        all_points = all_points | set([point.payload["name"] for point in response[0]])
        scroll_id = response[1] if len(response) >=1 else None
        if scroll_id is None:
            break
    return {"names":all_points}
    