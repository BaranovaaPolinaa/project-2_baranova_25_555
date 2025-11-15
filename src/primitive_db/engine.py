import os
import shlex

from src.primitive_db.core import create_table, drop_table, list_tables
from src.primitive_db.utils import load_metadata, save_metadata

META_FILE = os.path.join(os.path.dirname(__file__), "db_meta.json")


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
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

        command = args[0]

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            list_tables(metadata)

        elif command == "create_table":
            if len(args) < 2:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]
            columns = args[2:]

            before = metadata.copy()
            new_metadata = create_table(metadata, table_name, columns)

            if new_metadata != before:
                save_metadata(META_FILE, new_metadata)

        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]

            before = metadata.copy()
            new_metadata = drop_table(metadata, table_name)

            if new_metadata != before:
                save_metadata(META_FILE, new_metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
