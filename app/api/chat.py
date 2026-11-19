import os
from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from app.models import MessageRequest, MessageResponse, PDFResponse, PDFDelete
from app.database.engine import get_db
from app.controllers.messages import MessageController
from app.ai.engine import engine
from app.utils.rag import RAGStore

router = APIRouter()

rag_store: dict[int, RAGStore] = {}

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

    if msg.mode == 'document':
        prompt = rag_store[msg.pid].build_prompt(msg.content, top_k=4)
        response = await engine.chat(prompt)
        await MessageController.create(db, content=response, sender='ai', process=msg.pid)

@router.post("/upload/{pid}")
async def upload_pdf(pid: int, files: list[UploadFile] = File(...),
                     db: AsyncSession = Depends(get_db)):
    names = []
    for file in files:
        original_name = file.filename or "file.pdf"
        ext = Path(original_name).suffix.lower()

        # 1) Проверка расширения
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Разрешены только PDF-файлы")

        # 2) Проверка MIME-типа (доп. защита)
        if file.content_type not in ("application/pdf", "application/octet-stream"):
            raise HTTPException(status_code=400, detail="Неверный тип файла (нужен PDF)")

        # 3) Читаем файл целиком и проверяем размер
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Файл слишком большой (макс. {MAX_FILE_SIZE // (1024 * 1024)} МБ)",
            )

        # 4) Сохраняем файл
        names.append(original_name)
        if not os.path.exists(UPLOAD_DIR / f"{pid}"):
            os.makedirs(UPLOAD_DIR / f"{pid}")
        save_path = UPLOAD_DIR / f"{pid}" / original_name
        save_path.write_bytes(content)

    # 5) Пересоздаем базу знаний
    create_rag(pid)

    # 6) Ответ
    content = ""
    for name in names:
        content += f"<{name}>\n"
    await MessageController.create(db, content=f"{content}", sender="user", process=pid)
    await MessageController.create(db, content="Файлы успешно загружены", sender='ai', process=pid)

@router.get("/pdf/{pid}")
async def get_pdf(pid: int):
    p = UPLOAD_DIR / f"{pid}"
    files = []

    if not os.path.exists(p):
        return PDFResponse(files=[])

    for entry in p.iterdir():
        if entry.is_file():
            files.append({"name": entry.name, "size": os.path.getsize(entry)})

    return PDFResponse(files=files)

@router.post("/pdf/{pid}")
async def delete_pdf(pid: int, req: PDFDelete):
    p = UPLOAD_DIR / f"{pid}" / req.name
    p.unlink(missing_ok=True)

    create_rag(pid)

def create_rag(pid: int):
    rag_store[pid] = RAGStore()
    p = UPLOAD_DIR / f"{pid}"

    if not os.path.exists(p):
        return

    for entry in p.iterdir():
        if entry.is_file():
            with open(entry, 'rb') as file:
                content = file.read()
                rag_store[pid].add_pdf(entry.name, content)

    return
