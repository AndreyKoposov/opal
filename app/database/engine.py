from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


from app.config import DB_NAME, DB_PSWRD, DB_USER


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PSWRD}@postgres/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
session_local = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with session_local() as db:
        yield db
