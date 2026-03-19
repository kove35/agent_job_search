import json
import os
from typing import List
from app.models.application import ApplicationPack

FILE_PATH = "application_packs.json"

def load_application_packs() -> List[ApplicationPack]:
    if not os.path.exists(FILE_PATH):
        return []

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [ApplicationPack(**item) for item in data]

def save_application_packs(packs: List[ApplicationPack]):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump([p.dict() for p in packs], f, ensure_ascii=False, indent=2)
