from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Message


class MessageController:
    # ---------- READ (list) ----------
    @staticmethod
    async def list(db: AsyncSession, process: int, 
                   offset: int = 0, limit: int = 100) -> list[Message]:
        result = await db.execute(
            select(Message).where(Message.pid==process).order_by(Message.id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    # ---------- READ (new msgs) ----------
    @staticmethod
    async def new(db: AsyncSession, process: int, after: int) -> list[Message]:
        result = await db.execute(
            select(Message).where(Message.pid==process, Message.id > after).order_by(Message.id)
        )
        return list(result.scalars().all())

    # ---------- CREATE ----------
    @classmethod
    async def create(cls, db: AsyncSession, content: str, process: int, sender: str) -> Message:
        content = content.strip()
        if not content:
            raise ValueError("content must not be empty")

        msg = Message(content=content, pid=process, sender=sender)
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg
