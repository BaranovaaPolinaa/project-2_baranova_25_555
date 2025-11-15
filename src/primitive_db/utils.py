import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_metadata(filepath):
    """
    Загружает метаданные из JSON-файла.
    Если файл не найден, возвращает пустой словарь.
    """
    path = Path(filepath)
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка: файл {filepath} поврежден или не является корректным JSON.")
        return {}

def save_metadata(filepath, data):
    """
    Сохраняет метаданные в JSON-файл.
    """
    path = Path(filepath)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def load_table_data(table_name):
    """
    Загружает данные таблицы из JSON-файла.
    Если файла нет, возвращает пустой список.
    """
    path = DATA_DIR / f"{table_name}.json"
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Ошибка: файл данных таблицы {table_name} поврежден.")
        return []

def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в JSON-файл.
    """
    path = DATA_DIR / f"{table_name}.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
