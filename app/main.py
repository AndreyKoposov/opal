from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import STATIC_DIR, UPLOAD_DIR
from app.models import LoginRequest, LoginResponse
from app.database.engine import engine, Base, get_db
from app.controllers.users import UserController
from app.api.processes import router as ProcessRouter
from app.api.chat import router as CharRouter


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print(_app.title)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Ontology Processes Analyze Lab", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(ProcessRouter, prefix="/processes")
app.include_router(CharRouter, prefix="/chat")

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/lab/")
async def lab():
    return FileResponse(STATIC_DIR / "main.html")

@app.post("/login/")
async def login(response: Response, user_id: LoginRequest, db: AsyncSession = Depends(get_db)):
    name = user_id.id.strip()

    user = await UserController.get_or_create(db, name)
    response.set_cookie(key = "user_id", value = str(user.id))

    return LoginResponse(
        success=True,
        redirect_url="/lab/",
        message="Success"
    )
