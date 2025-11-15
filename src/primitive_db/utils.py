import json
from pathlib import Path
 

def load_metadata(filepath):
    """
    Загружает данные из JSON-файла.
    Если файл не найден, возвращает пустой словарь {}.
    """
    path = Path(filepath)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка: файл {filepath} поврежден или не является корректным JSON.")
        return {}

def save_metadata(filepath, data):
    """
    Сохраняет данные в JSON-файл.
    """
    path = Path(filepath)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
