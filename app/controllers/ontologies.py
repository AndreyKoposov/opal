from typing import cast

from sqlalchemy import select, Column
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Ontology


class OntologyController:
    # ---------- READ ----------
    @staticmethod
    async def get(db: AsyncSession, process: int) -> Ontology | None:
        result = await db.execute(
            select(Ontology).where(Ontology.pid==process)
        )
        return result.scalar_one_or_none()

    # ---------- Get/Create ----------
    @classmethod
    async def get_or_create(cls, db: AsyncSession, pid: int, text: str) -> Ontology | None:
        yaml = await cls.get(db, pid)
        if yaml is not None:
            return yaml

        yaml = Ontology(pid=pid, content=text)
        db.add(yaml)
        await db.commit()
        yaml = await cls.get(db, pid)

        return yaml

    # ---------- UPDATE ----------
    @classmethod
    async def update(cls, db: AsyncSession, pid: int, text: str) -> Ontology | None:
        text = text.strip()
        if not text:
            raise ValueError("text must not be empty")

        ontology = await cls.get(db, pid)
        if ontology is None:
            return None

        ontology.content = cast(Column[str], text)
        await db.commit()
        await db.refresh(ontology)

        return ontology
