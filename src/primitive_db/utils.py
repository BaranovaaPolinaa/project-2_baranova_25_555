import json
from pathlib import Path
from typing import Any

from src.primitive_db.constants import DATA_DIR, FILE_EXT


def _ensure_path(path: Path) -> Path:
    if path.suffix == "":
        return path.with_suffix(FILE_EXT)
    return path

def load_metadata(filepath: Path | str) -> dict:
    path = Path(filepath)
    path = _ensure_path(path)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Ошибка: файл {path} поврежден или не является корректным JSON.")
        return {}

def save_metadata(filepath: Path | str, data: Any) -> None:
    path = Path(filepath)
    path = _ensure_path(path)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def _table_path(table_name: str) -> Path:
    safe_name = Path(table_name).name
    return (DATA_DIR / safe_name).with_suffix(FILE_EXT)

def load_table_data(table_name: str) -> list:
    path = _table_path(table_name)
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Ошибка: файл данных таблицы {table_name} поврежден.")
        return []

def save_table_data(table_name: str, data: list) -> None:
    path = _table_path(table_name)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
