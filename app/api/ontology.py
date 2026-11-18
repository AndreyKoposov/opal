from typing import cast

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import YamlRequest, YamlResponse
from app.database.engine import get_db
from app.controllers.ontologies import OntologyController

router = APIRouter()

@router.get("/yaml/{pid}")
async def get(pid: int, db: AsyncSession = Depends(get_db)):
    ont = await OntologyController.get_or_create(db, pid, "")
    if ont:
        return YamlResponse(text=cast(str, ont.content))

@router.post("/yaml/{pid}")
async def send(pid: int, yaml: YamlRequest, db: AsyncSession = Depends(get_db)):
    await OntologyController.update(db, pid, yaml.text)
