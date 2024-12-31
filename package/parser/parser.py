from typing import List
from package.commands.commands import Command

def parse_command_line(s: str) -> List[Command]:
    """
    Разбирает строку командной строки на отдельные команды.

    Строка разделяется по символу '|', затем каждая команда разбивается на имя и аргументы.

    Параметры:
        s (str): Строка командной строки для разбора.

    Возвращает:
        List[Command]: Список объектов Command, представляющих разобранные команды.
    """
    res: List[Command] = []
    chunks = s.split('|')
    for chunk in chunks:
        cmd_args = chunk.strip().split()
        if not cmd_args:
            continue
        res.append(Command(command=cmd_args[0], arguments=cmd_args[1:]))
    return res
