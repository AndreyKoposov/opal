from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column

from app.database.models import Process


class ProcessController:
    # ---------- READ (list) ----------
    @staticmethod
    async def list(db: AsyncSession, user: int, offset: int = 0, limit: int = 100) -> list[Process]:
        result = await db.execute(
            select(Process).where(Process.user_id==user).order_by(Process.id)
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    # ---------- READ (one) ----------
    @staticmethod
    async def get(db: AsyncSession, process_id: int) -> Process | None:
        return await db.get(Process, process_id)

    # ---------- CREATE ----------
    @classmethod
    async def create(cls, db: AsyncSession, name: str, user: int) -> Process:
        name = name.strip()
        if not name:
            raise ValueError("name must not be empty")

        process = Process(name=name, user_id=user)
        db.add(process)
        await db.commit()
        # try:
        #     await db.commit()
        # except IntegrityError:
        #     await db.rollback()
        #     raise ValueError(f"process with name={name!r} already exists") from None

        await db.refresh(process)
        return process

    # ---------- UPDATE ----------
    @classmethod
    async def update(cls, db: AsyncSession, process_id: int, name: str) -> Process | None:
        name = name.strip()
        if not name:
            raise ValueError("name must not be empty")

        process = await cls.get(db, process_id)
        if process is None:
            return None

        process.name = cast(Column[str], name)
        await db.commit()
        # try:
        #     await db.commit()
        # except IntegrityError:
        #     await db.rollback()
        #     raise ValueError(f"process with name={name!r} already exists") from None

        await db.refresh(process)
        return process

    # ---------- DELETE ----------
    @staticmethod
    async def delete(db: AsyncSession, process_id: int) -> bool:
        process = await db.get(Process, process_id)
        if process is None:
            return False

        await db.delete(process)
        await db.commit()
        return True
