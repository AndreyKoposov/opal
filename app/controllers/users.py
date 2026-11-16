from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserController:
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> User | None:
        result = await db.execute(select(User).where(User.name == name))
        return result.scalar_one_or_none()

    @classmethod
    async def get_or_create(cls, db: AsyncSession, name: str) -> User:
        """Возвращает существующего пользователя или создаёт нового."""
        user = await cls.get_by_name(db, name)
        if user is not None:
            return user

        user = User(name=name)
        db.add(user)
        try:
            await db.commit()
        except IntegrityError:
            # гонка: параллельный запрос успел вставить того же пользователя
            await db.rollback()
            user = await cls.get_by_name(db, name)
            if user is None:
                raise
            return user

        await db.refresh(user)
        return user
