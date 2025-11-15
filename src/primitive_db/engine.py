import os
import shlex

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
from src.primitive_db.utils import load_metadata, save_metadata

META_FILE = os.path.join(os.getcwd(), "db_meta.json")


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("<command> insert into <имя_аблицы> values (...)")
    print("<command> select from <имя_аблицы> [where ...]")
    print("<command> update <имя_аблицы> set ... where ...")
    print("<command> delete from <имя_аблицы> where ...")
    print("<command> info <имя_аблицы>")
    print("\n:Общие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


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

        elif command == "help":
            print_help()

        elif command == "list_tables":
            list_tables(metadata)

        elif command == "create_table":
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

        elif command == "drop_table":
            if len(args) != 2:
                print("Ошибка: нужно указать имя таблицы. Пример: drop_table users")
                continue
            table_name = args[1]
            new_metadata = drop_table(metadata, table_name)
            save_metadata(META_FILE, new_metadata)

        elif command == "info":
            if len(args) != 2:
                print("Ошибка: нужно указать имя таблицы. Пример: info users")
                continue
            table_name = args[1]
            info(metadata, table_name)

        elif command == "insert":
            if (len(args) < 4 or
                args[1].lower() != "into" or
                args[3].lower() != "values"):
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: insert into users values (\"Sergei\", 28, true)"
                )
                continue
            table_name = args[2]
            values_str = user_input.split("values", 1)[1].strip()
            if values_str.startswith("(") and values_str.endswith(")"):
                values_str = values_str[1:-1]
            else:
                print(
                    "Ошибка: значения должны быть в скобках."
                    "Пример: values (\"Sergei\", 28, true)"
                )
                continue
            values = [v.strip() for v in values_str.split(",")]
            insert(metadata, table_name, values)

        elif command == "select":
            if len(args) < 3 or args[1].lower() != "from":
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: select from users [where age = 28]"
                )
                continue
            table_name = args[2]
            if "where" in args:
                where_index = args.index("where")
                where_clause_tokens = args[where_index + 1 : where_index + 4]
                if len(where_clause_tokens) != 3:
                    print(
                        "Ошибка: некорректное условие where."
                        "Пример: where age = 28"
                    )
                    continue
                from src.primitive_db.parser import parse_where

                where_clause = parse_where(where_clause_tokens)
            else:
                where_clause = None
            select(metadata, table_name, where_clause)

        elif command == "update":
            if len(args) < 6 or args[2].lower() != "set" or "where" not in args:
                print(
                    "Ошибка: некорректный синтаксис."
                    "Пример: update users set age = 29 where name = \"Sergei\""
                )
                continue
            table_name = args[1]
            where_index = args.index("where")
            set_tokens = args[3:where_index]
            where_tokens = args[where_index + 1 :]
            if len(set_tokens) != 3 or len(where_tokens) != 3:
                print("Ошибка: некорректное условие set или where")
                continue
            from src.primitive_db.parser import parse_set, parse_where

            set_clause = parse_set(set_tokens)
            where_clause = parse_where(where_tokens)
            if not set_clause or not where_clause:
                print("Ошибка: некорректное условие set или where")
                continue
            update(metadata, table_name, set_clause, where_clause)

        elif command == "delete":
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
            from src.primitive_db.parser import parse_where

            where_clause = parse_where(where_tokens)
            if not where_clause:
                print("Ошибка: некорректное условие where")
                continue
            delete(metadata, table_name, where_clause)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
