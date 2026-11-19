from typing import cast

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import yaml as Yaml

from app.models import YamlRequest, YamlResponse, GraphResponse
from app.database.engine import get_db
from app.controllers.ontologies import OntologyController
from app.utils.rdf_model import RdfModel
from app.utils.parser import parse_yaml

router = APIRouter()

models: dict[int, RdfModel] = {}

@router.get("/yaml/{pid}")
async def get(pid: int, db: AsyncSession = Depends(get_db)):
    ont = await OntologyController.get_or_create(db, pid, "")
    if ont:
        return YamlResponse(text=cast(str, ont.content))

@router.post("/yaml/{pid}")
async def send(pid: int, yaml: YamlRequest, db: AsyncSession = Depends(get_db)):
    ontology = await OntologyController.update(db, pid, yaml.text)
    if not ontology:
        raise ValueError

    text = cast(str, ontology.content)
    parsed = Yaml.safe_load(text)

    models[pid] = RdfModel(pid)
    model = models[pid]

    entities, stages, resources, transitions, usages, parts = parse_yaml(parsed)

    model.add_entities(entities)
    model.add_stages(stages)
    model.add_resources(resources)
    model.add_transitions(transitions)
    model.add_usages(usages)
    model.add_parts(parts)

@router.get("/graph/{pid}")
async def graph(pid: int):
    if pid < 0:
        return GraphResponse(triplets=[])

    if not models.get(pid, None):
        return GraphResponse(triplets=[])

    triplets = []
    for s, p, o in models[pid].g:
        triplets.append({
            "node1": replace_rdf(str(s), pid),
            "edge": replace_rdf(str(p), pid),
            "node2": replace_rdf(str(o), pid)
        })
    return GraphResponse(triplets=triplets)

def replace_rdf(el: str, pr_id: int) -> str:
    el = el.replace(f"http://{pr_id}/", "")
    el = el.replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "")
    el = el.replace("http://www.w3.org/2001/XMLSchema#", "")
    el = el.replace("http://www.w3.org/2000/01/rdf-schema#", "")
    el = el.replace("http://www.w3.org/2002/07/owl#", "")

    return el
