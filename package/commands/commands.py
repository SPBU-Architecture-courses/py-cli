import os
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Command:
    command: str
    arguments: List[str]


class CommandError(Exception):
    """Кастомное исключение для ошибок выполнения команд."""
    pass


class StateCommands:
    def __init__(self):
        self.prev_command_output: Optional[str] = None
        self.prev_return_code: int = 0
        self.command_content: str = ""
        self.available_commands = {
            "cat": self.cat,
            "echo": self.echo,
            "wc": self.wc,
            "pwd": self.pwd,
            "exit": self.exit_command
        }

    def cat(self, filenames: List[str]) -> str:
        """
        Объединяет содержимое указанных файлов и возвращает результат в виде строки.
        Если файлы не указаны, возвращает содержимое предыдущего вывода команды.

        Параметры:
            filenames (List[str]): Список имен файлов для объединения их содержимого.

        Возвращает:
            str: Содержимое объединённых файлов или предыдущий вывод команды.

        Исключения:
            CommandError: Если не указаны файлы и нет предыдущего вывода,
                         или если возникла ошибка при чтении файлов.
        """
        if not filenames:
            if not self.prev_command_output:
                raise CommandError("Usage: cat [FILE]")
            content = self.prev_command_output
            self.prev_command_output = ""
            return content

        content = ""
        for filename in filenames:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    content += file_content
            except FileNotFoundError:
                raise CommandError(f"File not found: {filename}")
            except Exception as e:
                raise CommandError(f"Error reading file {filename}: {e}")

        self.prev_command_output = content
        return content

    def wc(self, filenames: List[str]) -> str:
        """
        Подсчитывает количество строк, слов и байт в указанном файле или в предыдущем выводе команды.

        Параметры:
            filenames (List[str]): Список имен файлов для анализа. Используется только первый файл.
                                   Если список пуст, используется предыдущий вывод команды.

        Возвращает:
            str: Строка с подсчитанными значениями строк, слов и байт в формате:
                 "Lines: X, Words: Y, Bytes: Z"

        Исключения:
            CommandError: Если не указаны файлы и нет предыдущего вывода,
                         или если возникла ошибка при чтении файла.
        """
        if not filenames:
            if not self.prev_command_output:
                raise CommandError("Usage: wc [FILE]")
            input_stream = self.prev_command_output.splitlines(True)
        else:
            try:
                with open(filenames[0], 'r', encoding='utf-8') as f:
                    input_stream = f
            except FileNotFoundError:
                raise CommandError(f"File not found: {filenames[0]}")
            except Exception as e:
                raise CommandError(f"Error reading file {filenames[0]}: {e}")

        line_count, word_count, byte_count = 0, 0, 0

        if isinstance(input_stream, list):
            # prev_command_output case
            for line in input_stream:
                line_count += 1
                word_count += len(line.split())
                byte_count += len(line.encode('utf-8'))
        else:
            # File object
            for line in input_stream:
                line_count += 1
                word_count += len(line.split())
                byte_count += len(line.encode('utf-8'))

        result = f"Lines: {line_count}, Words: {word_count}, Bytes: {byte_count}"
        self.prev_command_output = result
        return result

    def pwd(self, args: List[str]) -> str:
        """
        Возвращает текущую рабочую директорию.

        Параметры:
            args (List[str]): Список аргументов команды. Должен быть пустым.

        Возвращает:
            str: Абсолютный путь текущей рабочей директории.

        Исключения:
            CommandError: Если передано несколько аргументов,
                         или если возникает ошибка при получении директории.
        """
        if len(args) != 0:
            raise CommandError("pwd: too many arguments")
        try:
            directory = os.getcwd()
            self.prev_command_output = directory
            return directory
        except Exception as e:
            raise CommandError(f"Error getting current directory: {e}")

    def echo(self, args: List[str]) -> str:
        """
        Выводит переданные аргументы в стандартный вывод и сохраняет их как предыдущий вывод команды.

        Параметры:
            args (List[str]): Список аргументов для вывода.

        Возвращает:
            str: Строка, составленная из переданных аргументов, разделённых пробелами.
        """
        output = ' '.join(args)
        self.prev_command_output = output
        return output
    
    def exit_command(self, args: List[str]) -> str:
        """
        Завершает выполнение программы с заданным кодом выхода.

        Параметры:
            args (List[str]): Список аргументов команды. Должен быть пустым.

        Возвращает:
            str: Пустая строка (фактически эта строка никогда не будет возвращена).

        Исключения:
            CommandError: Если передано несколько аргументов.
        """
        if args:
            raise CommandError("exit: слишком много аргументов")
        exit_code = self.prev_return_code
        print(f"Выход с кодом {exit_code}")
        os._exit(exit_code)
        return ""

    def reset(self):
        self.prev_command_output = ""
        self.command_content = ""
