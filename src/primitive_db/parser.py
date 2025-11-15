def parse_where(tokens):
    """
    Парсит условие WHERE из SQL команды.
    """
    if len(tokens) != 3 or tokens[1] != "=":
        return None
    col, val = tokens[0], tokens[2]
    val = val.strip('"').strip("'") 
    
    return col, val


def parse_set(tokens):
    """
    Парсит часть команды вида SET <столбец> = <значение>.
    """
    if len(tokens) != 3 or tokens[1] != "=":
        return None
    col, val = tokens[0], tokens[2]
    val = val.strip('"').strip("'")
    
    return col, val
