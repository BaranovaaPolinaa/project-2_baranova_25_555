from pathlib import Path

PROJECT_ROOT = Path.cwd()
DATA_DIR = PROJECT_ROOT / "data"
META_FILE = DATA_DIR / "db_meta.json"
FILE_EXT = ".json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

ID_FIELD = "ID"
VALID_TYPES = {"int", "str", "bool"}

MSG = {
    "table_exists": 'Ошибка: Таблица "{name}" уже существует.',
    "table_not_exists": 'Ошибка: Таблица "{name}" не существует.',
    "created_table": 'Таблица "{name}" успешно создана со столбцами: {cols}',
    "dropped_table": 'Таблица "{name}" успешно удалена.',
    "record_added": 'Запись с ID={id} успешно добавлена в таблицу "{name}".',
    "no_records_found": 'Записей, соответствующих условию,'
                        'не найдено в таблице "{name}".',
    "record_deleted": 'Запись с ID={id} успешно удалена из таблицы "{name}".',
    "record_updated": 'Запись с ID={id} в таблице "{name}" успешно обновлена.',
    "syntax_error": "Ошибка: некорректный синтаксис.",
    "invalid_json": "Ошибка: файл {path} поврежден или не является корректным JSON.",
    "table_file_invalid": "Ошибка: файл данных таблицы {name} поврежден.",
}

HELP_TEXT = """
***Процесс работы с таблицей***
Функции:
create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу
list_tables - показать список всех таблиц
drop_table <имя_таблицы> - удалить таблицу

***Операции с данными***
insert into <имя_таблицы> values (...)
select from <имя_таблицы> [where ...]
update <имя_таблицы> set ... where ...
delete from <имя_таблицы> where ...
info <имя_таблицы>

Общие команды:
exit - выход из программы
help - справочная информация
"""
