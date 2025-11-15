VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    """
    Создаёт таблицу.
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
