import os
from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from app.models import MessageRequest, MessageResponse
from app.database.engine import get_db
from app.controllers.messages import MessageController
from app.ai.engine import engine

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
    if msg.mode == 'normal':
        response = await engine.chat(msg.content)
        await MessageController.create(db, content=response, sender='ai', process=msg.pid)

@router.post("/upload/{pid}")
async def upload_pdf(pid: int, files: list[UploadFile] = File(...),
                     db: AsyncSession = Depends(get_db)):
    original_name = files[0].filename or "file.pdf"
    ext = Path(original_name).suffix.lower()

    # 1) Проверка расширения
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Разрешены только PDF-файлы")

    # 2) Проверка MIME-типа (доп. защита)
    if files[0].content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Неверный тип файла (нужен PDF)")

    # 3) Читаем файл целиком и проверяем размер
    content = files[0].file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой (макс. {MAX_FILE_SIZE // (1024 * 1024)} МБ)",
        )

    # 4) Сохраняем файл
    if not os.path.exists(UPLOAD_DIR / f"{pid}"):
        os.makedirs(UPLOAD_DIR / f"{pid}")
    save_path = UPLOAD_DIR / f"{pid}" / original_name
    save_path.write_bytes(content)

    # 5) Ответ
    await MessageController.create(db, content=f"Файл - <{original_name}>", sender="user", process=pid)
    await MessageController.create(db, content="Файлы успешно загружены", sender='ai', process=pid)
