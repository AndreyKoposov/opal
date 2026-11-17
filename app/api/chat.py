from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MessageRequest, MessageResponse
from app.database.engine import get_db
from app.controllers.messages import MessageController

router = APIRouter()

@router.get("/msgs/{pid}")
async def get_list(pid: int, db: AsyncSession = Depends(get_db)):
    messages = await MessageController.list(db, pid)

    msgs_json = []
    for m in messages:
        msgs_json.append({"id": m.id, "content": m.content, "sender": m.sender, "pid": m.pid})
    return MessageResponse(
        msgs=msgs_json
    )

@router.get("/new/{pid}/{after}")
async def get_new(pid: int, after: int, db: AsyncSession = Depends(get_db)):
    messages = await MessageController.new(db, pid, after=after)

    msgs_json = []
    for m in messages:
        msgs_json.append({"id": m.id, "content": m.content, "sender": m.sender, "pid": m.pid})
    return MessageResponse(
        msgs=msgs_json
    )

@router.post("/create/")
async def create(msg: MessageRequest, db: AsyncSession = Depends(get_db)):
    await MessageController.create(db, content=msg.content, sender=msg.sender, process=msg.pid)
