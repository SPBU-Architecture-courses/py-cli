from typing import List
from package.commands.commands import Command

def parse_command_line(s: str) -> List[Command]:
    """
    Разбирает строку командной строки на переменные и команду
    """
    cmd_args = s.strip().split()
    if not cmd_args:
        return []
    return [Command(command=cmd_args[0], arguments=cmd_args[1:])]
