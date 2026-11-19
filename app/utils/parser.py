def parse_yaml(yaml):
    # resources: list[str] = yaml["Ресурсы"]
    entities: list[str] = yaml["Сущности"]
    stages: list[str] = yaml["Этапы"]
    resources: list[str] = yaml["Ресурсы"]

    transitions: list[dict[str, str]] = yaml["Переходы"]
    usages: list[dict[str, str]] = yaml["Использования"]
    parts: list[dict[str, str]] = yaml["Участия"]

    trns: list[tuple[str, str]] = []
    for t in transitions:
        trns.append((t["Из"], t["В"]))

    uses: list[tuple[str, str]] = []
    for u in usages:
        uses.append((u["Этап"], u["Ресурс"]))

    part: list[tuple[str, str]] = []
    for p in parts:
        part.append((p["Сущность"], p["Этап"]))

    return entities, stages, resources, trns, uses, part
