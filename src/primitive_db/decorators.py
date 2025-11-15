import time
from functools import wraps


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок в функциях работы с базой данных.
    Перехватывает KeyError, ValueError, FileNotFoundError и выводит сообщение.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            print(f"Ошибка: ключ {exc} не найден.")
        except ValueError as exc:
            print(f"Ошибка: неверное значение. {exc}")
        except FileNotFoundError as exc:
            print(f"Ошибка: файл не найден. {exc}")
        except Exception as exc:
            print(f"Произошла непредвиденная ошибка: {exc}")
    return wrapper


def confirm_action(action_name):
    """
    Фабрика декораторов для подтверждения опасных операций.
    Перед выполнением функции запрашивает у пользователя подтверждение.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if confirmation != "y":
                print(f'Операция "{action_name}" отменена.')
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
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


def create_cacher():
    """
    Возвращает функцию для кэширования результатов.
    Использует замыкание для хранения кэша в словаре.
    """
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result
