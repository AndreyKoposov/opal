from typing import cast

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProcessRequest, ProcessResponse, ProcessIDResponse
from app.database.engine import get_db
from app.controllers.processes import ProcessController

router = APIRouter()

@router.get("/list/{user}")
async def get_list(user: int, db: AsyncSession = Depends(get_db)):
    processes = await ProcessController.list(db, user)

    processes_json = []
    for p in processes:
        processes_json.append({"id": p.id, "name": p.name, "user_id": p.user_id})
    return ProcessResponse(
        processes=processes_json
    )

@router.post("/create/")
async def create(request: ProcessRequest, db: AsyncSession = Depends(get_db)):
    process = await ProcessController.create(db, request.name, request.user)
    pid = cast(int, process.id)

    return ProcessIDResponse(
        pid=pid
    )

@router.post("/update/")
async def update(request: ProcessRequest, db: AsyncSession = Depends(get_db)):
    await ProcessController.update(db, request.id, request.name)

@router.post("/delete/")
async def delete(request: ProcessRequest, db: AsyncSession = Depends(get_db)):
    await ProcessController.delete(db, request.id)
