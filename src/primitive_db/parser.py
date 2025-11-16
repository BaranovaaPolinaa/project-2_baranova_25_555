from typing import Optional, Sequence, Tuple


def _parse_binary(tokens: Sequence[str]) -> Optional[Tuple[str, str]]:
    """
    Общий парсер для "<column> = <value>".
    Возвращает (column, value) или None при ошибке.
    """
    if len(tokens) != 3:
        return None
    col, op, val = tokens
    if op != "=":
        return None
    val = val.strip('"').strip("'")
    return col, val


def parse_where(tokens: Sequence[str]) -> Optional[Tuple[str, str]]:
    """Парсер WHERE."""
    return _parse_binary(tokens)


def parse_set(tokens: Sequence[str]) -> Optional[Tuple[str, str]]:
    """Парсер SET."""
    return _parse_binary(tokens)