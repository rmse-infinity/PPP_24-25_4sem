import asyncio
import json

from fastapi import APIRouter
from starlette.websockets import WebSocket

from app.celery.app import rdb

router = APIRouter()


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    pubsub = rdb.pubsub()
    pubsub.subscribe(f"task_updates:{task_id}")

    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = json.loads(message["data"])
                await websocket.send_json(data)
                if data.get("status") == "COMPLETED":
                    break
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        pubsub.unsubscribe(f"task_updates:{task_id}")
        await websocket.close()
