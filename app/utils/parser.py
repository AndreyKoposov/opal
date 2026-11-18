def parse_yaml(yaml):
    # resources: list[str] = yaml["Ресурсы"]
    entities: list[str] = yaml["Сущности"]
    stages: list[str] = yaml["Этапы"]

    transitions: list[dict[str, str]] = yaml["Переходы"]
    # usages: list[dict[str, str]] = yaml["Использования"]

    trns: list[tuple[str, str]] = []
    for t in transitions:
        trns.append((t["Из"], t["В"]))

    # uses: list[tuple[str, str]] = []
    # for u in usages:
    #     trns.append((u["Этап"], u["Ресурс"]))

    return entities, stages, trns
