from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import LoginRequest, LoginResponse


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR.parent / "uploads"

MAX_FILE_SIZE = 20 * 1024 * 1024   # 20 МБ
ALLOWED_EXTENSIONS = {".pdf"}

app = FastAPI(title="Ontology Process Analyze Lab")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/lab/")
async def lab():
    return FileResponse(STATIC_DIR / "main.html")

@app.post("/login/")
async def login(user_id: LoginRequest):
    print(f"\nLogin = {user_id.id}")
    return LoginResponse(
        success=True,
        redirect_url="/lab/",
        message="Success"
    )
