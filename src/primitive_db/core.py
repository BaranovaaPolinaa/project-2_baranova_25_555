from prettytable import PrettyTable

from src.primitive_db.constants import VALID_TYPES
from src.primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from src.primitive_db.utils import load_table_data, save_table_data

cacher = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    """
    Создаёт таблицу с заданными столбцами.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    parsed_columns = []

    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        name, type_name = col.split(":", 1)

        if type_name not in VALID_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata

        parsed_columns.append((name, type_name))

    full_columns = [("ID", "int")] + parsed_columns
    metadata[table_name] = full_columns

    cols_str = (
        ", ".join(f"{col_name}:{col_type}" for col_name, col_type in full_columns)
    )
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')

    return metadata


@handle_db_errors
@confirm_action("Удаление таблицы")
def drop_table(metadata, table_name):
    """
    Удаляет таблицу.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def list_tables(metadata):
    """
    Показывает список таблиц.
    """
    if not metadata:
        return

    for name in metadata:
        print(f"- {name}")


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """
    Добавляет запись в таблицу.
    Автоматически генерирует ID. Проверяет соответствие типов данных.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]
    if len(values) != len(columns) - 1:
        print("Ошибка: количество значений не соответствует количеству столбцов.")
        return

    record = {}
    for (col_name, col_type), val in zip(columns[1:], values):
        val = str(val).strip('"').strip("'")
        if col_type == "int":
            try:
                record[col_name] = int(val)
            except ValueError:
                print(f"Ошибка: {col_name} должен быть int.")
                return
        elif col_type == "str":
            record[col_name] = val
        elif col_type == "bool":
            if val.lower() in ("true", "1"):
                record[col_name] = True
            elif val.lower() in ("false", "0"):
                record[col_name] = False
            else:
                print(f"Ошибка: {col_name} должен быть bool.")
                return

    data = load_table_data(table_name)
    new_id = max((r["ID"] for r in data), default=0) + 1
    record["ID"] = new_id
    data.append(record)
    save_table_data(table_name, data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


@handle_db_errors
@log_time
def select(metadata, table_name, where_clause=None):
    """
    Выводит записи таблицы. Фильтрует по условию where_clause, если задано.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    def get_data():
        data = load_table_data(table_name)
        if where_clause:
            column, value = where_clause
            value = str(value).strip('"').strip("'")
            table_data = [row for row in data if str(row.get(column)) == value]
        return table_data

    key = (table_name, str(where_clause))
    data = cacher(key, get_data)

    table = PrettyTable()
    columns = [name for name, _ in metadata[table_name]]
    table.field_names = columns
    for row in data:
        table.add_row([row.get(col) for col in columns])
    print(table)


@handle_db_errors
def update(metadata, table_name, set_clause, where_clause):
    """
    Обновляет записи в таблице по условию.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    data = load_table_data(table_name)
    set_column, set_value = set_clause
    where_column, where_value = where_clause
    where_value = str(where_value).strip('"').strip("'")
    set_value = str(set_value).strip('"').strip("'")

    updated_count = 0
    for row in data:
        if str(row.get(where_column)) == where_value:
            row[set_column] = set_value
            updated_count += 1
            print(
                f'Запись с ID={row["ID"]} в таблице "{table_name}" успешно обновлена.'
            )

    if updated_count == 0:
        print(f'Записей, соответствующих условию, не найдено в таблице "{table_name}".')

    save_table_data(table_name, data)


@handle_db_errors
@confirm_action("Удаление записей")
def delete(metadata, table_name, where_clause):
    """
    Удаляет записи из таблицы по условию.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    data = load_table_data(table_name)
    column, value = where_clause
    value = str(value).strip('"').strip("'")

    to_delete = [row for row in data if str(row.get(column)) == value]

    if not to_delete:
        print(f'Записей, соответствующих условию, не найдено в таблице "{table_name}".')
        return

    for row in to_delete:
        print(f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".')

    data = [row for row in data if str(row.get(column)) != value]
    save_table_data(table_name, data)


@handle_db_errors
def info(metadata, table_name):
    """
    Выводит информацию о таблице: столбцы и количество записей.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    data = load_table_data(table_name)
    columns_str = ", ".join(
    f"{col_name}:{col_type}" for col_name, col_type in metadata[table_name]
    )
    print(
        f"Таблица: {table_name}\n"
        f"Столбцы: {columns_str}\n"
        f"Количество записей: {len(data)}"
    )
