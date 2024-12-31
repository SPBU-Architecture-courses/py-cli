import os
import subprocess
from typing import Dict, List
from  package.commands.commands import StateCommands, Command, CommandError

class State:
    def __init__(self, state_commands):
        self.state_commands: StateCommands = state_commands

        self.global_variables: Dict[str, str] = {
            "HOME": os.getenv("HOME", ""),
            "USER": os.getenv("USER", ""),
        }
        self.prev_return_code: int = 0

    def _check_command(self, cmd: str) -> bool:
        if cmd == "exit":
            return True
        return cmd in self.state_commands.available_commands


    def evaluate_commands(self, commands: List[Command]) -> None:
        """
        Выполняет список команд.

        Для каждой команды:
            1. Подставляет переменные.
            2. Проверяет и выполняет встроенные команды.
            3. Обрабатывает присваивания переменных.
            4. Выполняет внешние команды через subprocess.

        После выполнения выводится результат последней команды и сбрасывается состояние.

        Параметры:
            commands (List[Command]): Список команд для выполнения.

        Исключения:
            CommandError: При ошибках подстановки, выполнения команд или присваивания.
        """
        for command in commands:
            try:
                substituted_command = self._substitute_variables(command) # подстановка переменных
            except Exception as e:
                raise CommandError(f"Ошибка подстановки переменных: {e}")

            cmd_name : str = substituted_command.command
            args : List[str] = substituted_command.arguments

            if self._check_command(cmd_name):
                try:
                    output = self.state_commands.available_commands[cmd_name](args)
                    self.state_commands.prev_command_output = output
                except CommandError as ce:
                    self._renew_return_code(1)
                    raise CommandError(f"Ошибка выполнения встроенной команды '{cmd_name}': {ce}")
                except Exception as e:
                    self._renew_return_code(1)
                    raise CommandError(f"Непредвиденная ошибка при выполнении команды '{cmd_name}': {e}")
                continue

            # Выполнение внешней команды
            try:
                result = subprocess.run([cmd_name] + args, capture_output=True, text=True, check=True)
                self.state_commands.prev_command_output = result.stdout
                self._renew_return_code(result.returncode)
            except subprocess.CalledProcessError as e:
                self.state_commands.prev_command_output = e.output
                self._renew_return_code(e.returncode)
                raise CommandError(f"Ошибка выполнения внешней команды '{cmd_name}': {e}")
            except FileNotFoundError:
                self._renew_return_code(127)
                raise CommandError(f"Команда не найдена: {cmd_name}")
            except Exception as e:
                self._renew_return_code(1)
                raise CommandError(f"Непредвиденная ошибка при выполнении команды '{cmd_name}': {e}")

        print(self.state_commands.prev_command_output)
        self._reset()


    def _reset(self) -> None:
        self.state_commands.reset()
        return
    
    def _renew_return_code(self, code):
        self.state_commands.prev_return_code = code
        self.prev_return_code = code

    def _substitute_variables(self, command: Command) -> Command:
        new_command = self._substitute_variable(command.command)
        new_arguments = [self._substitute_variable(arg) for arg in command.arguments]
        return Command(command=new_command, arguments=new_arguments)

    def _substitute_variable(self, word: str) -> str:
        result = []
        i = 0
        length = len(word)
        while i < length:
            if word[i] == '$':
                i += 1
                var_name = []
                # Собираем имя переменной (до первого неалфавитного символа)
                while i < length and (word[i].isalnum() or word[i] == '_'):
                    var_name.append(word[i])
                    i += 1
                var_name_str = ''.join(var_name)
                var_value = self.global_variables.get(var_name_str, '')
                result.append(var_value)
            else:
                result.append(word[i])
                i += 1
        return ''.join(result)
