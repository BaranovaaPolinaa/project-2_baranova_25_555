from typing import List, Tuple

from prettytable import PrettyTable

from src.primitive_db.constants import DATA_DIR, FILE_EXT, ID_FIELD, MSG, VALID_TYPES
from src.primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from src.primitive_db.utils import load_table_data, save_table_data

cache_select, invalidate_cache = create_cacher()

def _convert_value_by_type(value: str, type_name: str):
    """
    Конвертор.
    """
    if type_name == "int":
        return int(value)
    if type_name == "str":
        return value
    if type_name == "bool":
        vl = value.lower()
        if vl in ("true", "1"):
            return True
        if vl in ("false", "0"):
            return False
        raise ValueError(f"значение {value} не является bool")
    raise ValueError(f"неподдерживаемый тип {type_name}")

@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: List[str]) -> dict:
    """
    Создаёт таблицу с заданными столбцами.
    """
    if table_name in metadata:
        print(MSG["table_exists"].format(name=table_name))
        return metadata

    parsed_columns: List[Tuple[str, str]] = []
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}")
            return metadata
        name, type_name = col.split(":", 1)
        type_name = type_name.strip()
        if type_name not in VALID_TYPES:
            print(f"Некорректное значение: {col}")
            return metadata
        parsed_columns.append((name.strip(), type_name))

    full_columns = [(ID_FIELD, "int")] + parsed_columns
    metadata[table_name] = full_columns

    cols_str = ", ".join(f"{c}:{t}" for c, t in full_columns)
    print(MSG["created_table"].format(name=table_name, cols=cols_str))
    return metadata


@handle_db_errors
@confirm_action("Удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """
    Удаляет таблицу.
    """
    if table_name not in metadata:
        print(MSG["table_not_exists"].format(name=table_name))
        return metadata

    del metadata[table_name]
    table_path = (DATA_DIR / table_name).with_suffix(FILE_EXT)
    table_path.unlink(missing_ok=True)
    invalidate_cache(table_name)
    print(MSG["dropped_table"].format(name=table_name))
    return metadata

def list_tables(metadata: dict) -> None:
    """
    Показывает список таблиц.
    """
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: List[str]) -> None:
    """
    Добавляет запись в таблицу.
    Автоматически генерирует ID. Проверяет соответствие типов данных.
    """
    if table_name not in metadata:
        print(MSG["table_not_exists"].format(name=table_name))
        return

    columns = metadata[table_name]
    if len(values) != len(columns) - 1:
        print("Ошибка: количество значений не соответствует количеству столбцов.")
        return

    record = {}
    for (col_name, col_type), val in zip(columns[1:], values):
        val = str(val).strip('"').strip("'").strip()
        try:
            record[col_name] = _convert_value_by_type(val, col_type)
        except ValueError:
            print(f"Ошибка: {col_name} должен быть {col_type}")
            return

    data = load_table_data(table_name)
    new_id = max((r.get(ID_FIELD, 0) for r in data), default=0) + 1
    record[ID_FIELD] = new_id
    data.append(record)
    save_table_data(table_name, data)
    invalidate_cache(table_name)
    print(MSG["record_added"].format(id=new_id, name=table_name))


@handle_db_errors
@log_time
def select(metadata: dict, table_name: str, where_clause=None) -> None:
    """
    Выводит записи таблицы. Фильтрует по условию where_clause, если задано.
    """
    if table_name not in metadata:
        print(MSG["table_not_exists"].format(name=table_name))
        return

    def predicate(row):
        if not where_clause:
            return True
        col, val = where_clause
        val = str(val).strip('"').strip("'")
        return str(row.get(col)) == val

    key = (table_name, str(where_clause))
    def load():
        return [row for row in load_table_data(table_name) if predicate(row)]
    result = cache_select(key, load)

    table = PrettyTable()
    columns = [c for c, _ in metadata[table_name]]
    table.field_names = columns
    for row in result:
        table.add_row([row.get(c) for c in columns])
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
    invalidate_cache(table_name)


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
