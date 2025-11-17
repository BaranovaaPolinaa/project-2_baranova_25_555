import time
from functools import wraps
from typing import Callable, Tuple


def handle_db_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок в функциях работы с базой данных.
    Перехватывает KeyError, ValueError, FileNotFoundError и выводит сообщение.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if result is None and args:
                return args[0]
            return result
        except Exception as exc:
            print(f"Произошла непредвиденная ошибка: {exc}")
            return args[0] if args else {}
    return wrapper


def confirm_action(action_name: str) -> Callable:
    """
    Фабрика декораторов для подтверждения опасных операций.
    Перед выполнением функции запрашивает у пользователя подтверждение.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if confirmation != "y":
                print(f'Операция "{action_name}" отменена.')
                return args[0] if args else {}
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции.
    Выводит время в консоль.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result
    return wrapper


def create_cacher() -> Tuple[Callable, Callable]:
    """
    Возвращает функцию для кэширования результатов.
    Использует замыкание для хранения кэша в словаре.
    """
    cache = {}
    table_keys = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        table, _ = key
        table_keys.setdefault(table, []).append(key)
        return result

    def invalidate(table):
        if table in table_keys:
            for key in table_keys[table]:
                cache.pop(key, None)
            table_keys[table] = []

    return cache_result, invalidate
