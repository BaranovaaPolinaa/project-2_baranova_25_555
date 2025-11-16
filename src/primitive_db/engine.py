import shlex

from src.primitive_db.constants import HELP_TEXT, META_FILE
from src.primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from src.primitive_db.parser import parse_set, parse_where
from src.primitive_db.utils import load_metadata, save_metadata


def print_help():
    print(HELP_TEXT)


def _safe_split_values(values_str: str):
    """
    Берёт строку после ключевого слова values и возвращает список значений.
    Учитывает кавычки (простейшая обработка).
    """
    vs = values_str.strip()
    if vs.startswith("(") and vs.endswith(")"):
        inner = vs[1:-1].strip()
    else:
        return None
    parts = [p.strip() for p in inner.split(",")]
    return parts


def run():
    print_help()
    while True:
        metadata = load_metadata(META_FILE)

        user_input = input(">>>Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректное значение. Попробуйте снова.")
            continue

        command = args[0].lower()

        if command == "exit":
            break
        if command == "help":
            print_help()
            continue

        if command == "list_tables":
            list_tables(metadata)
            continue

        if command == "create_table":
            if len(args) < 2:
                print(
                    "Ошибка: нужно указать имя таблицы."
                    "Пример: create_table users name:str age:int"
                )
                continue
            table_name = args[1]
            columns = args[2:]
            new_metadata = create_table(metadata, table_name, columns)
            save_metadata(META_FILE, new_metadata)
            continue

        if command == "drop_table":
            if len(args) != 2:
                print("Ошибка: нужно указать имя таблицы. Пример: drop_table users")
                continue
            table_name = args[1]
            new_metadata = drop_table(metadata, table_name)
            save_metadata(META_FILE, new_metadata)
            continue

        if command == "info":
            if len(args) != 2:
                print("Ошибка: нужно указать имя таблицы. Пример: info users")
                continue
            table_name = args[1]
            info(metadata, table_name)
            continue

        if command == "insert":
            if (
                len(args) < 4 or
                args[1].lower() != "into" or
                args[3].lower() != "values"
            ):
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: insert into users values (\"Sergei\", 28, true)"
                    )
                continue
            table_name = args[2]
            split_point = user_input.lower().find("values")
            values_str = user_input[split_point + len("values") :]
            values = _safe_split_values(values_str)
            if values is None:
                print(
                    "Ошибка: значения должны быть в скобках."
                    "Пример: values (\"Sergei\", 28, true)"
                )
                continue
            insert(metadata, table_name, values)
            continue

        if command == "select":
            if len(args) < 3 or args[1].lower() != "from":
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: select from users [where age = 28]"
                )
                continue
            table_name = args[2]
            if "where" in [a.lower() for a in args]:
                where_index = next(
                    i for i, a in enumerate(args) if a.lower() == "where"
                )
                where_clause_tokens = args[where_index + 1 : where_index + 4]
                if len(where_clause_tokens) != 3:
                    print("Ошибка: некорректное условие where. Пример: where age = 28")
                    continue
                where_clause = parse_where(where_clause_tokens)
            else:
                where_clause = None
            select(metadata, table_name, where_clause)
            continue

        if command == "update":
            if (
                len(args) < 6 or
                args[2].lower() != "set" or
                "where" not in [a.lower() for a in args]
            ):
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: update users set age = 29 where name = \"Sergei\""
                )
                continue
            table_name = args[1]
            where_index = next(i for i, a in enumerate(args) if a.lower() == "where")
            set_tokens = args[3:where_index]
            where_tokens = args[where_index + 1 :]
            if len(set_tokens) != 3 or len(where_tokens) != 3:
                print("Ошибка: некорректное условие set или where")
                continue
            set_clause = parse_set(set_tokens)
            where_clause = parse_where(where_tokens)
            if not set_clause or not where_clause:
                print("Ошибка: некорректное условие set или where")
                continue
            update(metadata, table_name, set_clause, where_clause)
            continue

        if command == "delete":
            if len(args) < 5 or args[1].lower() != "from" or args[3].lower() != "where":
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: delete from users where ID = 1"
                )
                continue
            table_name = args[2]
            where_tokens = args[4:7]
            if len(where_tokens) != 3:
                print("Ошибка: некорректное условие where")
                continue
            where_clause = parse_where(where_tokens)
            if not where_clause:
                print("Ошибка: некорректное условие where")
                continue
            delete(metadata, table_name, where_clause)
            continue

        print(f"Функции {command} нет. Попробуйте снова.")
