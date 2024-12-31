import unittest
from unittest.mock import Mock, patch
import subprocess
import os

from package.state.state import State
from package.commands.commands import StateCommands, Command, CommandError


class TestState(unittest.TestCase):
    def setUp(self):
        self.state_commands = StateCommands()
        self.mock_builtin_command = Mock(return_value="builtin command executed")
        self.state_commands.available_commands = {
            "builtin_cmd": self.mock_builtin_command
        }

        patcher = patch.dict(os.environ, {"HOME": "/home/testuser", "USER": "testuser"})
        self.addCleanup(patcher.stop)
        patcher.start()

        self.state = State(self.state_commands)

    def test_check_existing_builtin_command(self):
        self.assertTrue(self.state._check_command("builtin_cmd"))

    def test_check_exit_command(self):
        self.assertTrue(self.state._check_command("exit"))

    def test_check_nonexistent_command(self):
        self.assertFalse(self.state._check_command("nonexistent_cmd"))

    def test_evaluate_variable_assignment(self):
        commands = [Command(command="MY_VAR=value", arguments=[])]
        self.state.evaluate_commands(commands)
        self.assertIn("MY_VAR", self.state.global_variables)
        self.assertEqual(self.state.global_variables["MY_VAR"], "value")
        self.assertEqual(self.state.prev_return_code, 0)


    def test_evaluate_external_command_failure(self):
        commands = [Command(command="false", arguments=[])]
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="false", output="Error")

            with self.assertRaises(CommandError) as context:
                self.state.evaluate_commands(commands)
            
            mock_run.assert_called_with(["false"], capture_output=True, text=True, check=True)
            self.assertEqual(self.state.prev_return_code, 1)
            self.assertIn("Ошибка выполнения внешней команды 'false'", str(context.exception))

    def test_evaluate_nonexistent_external_command(self):
        commands = [Command(command="nonexistent_cmd", arguments=[])]
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            with self.assertRaises(CommandError) as context:
                self.state.evaluate_commands(commands)
                self.assertEqual(self.state.prev_return_code, 127)
            self.assertIn("Команда не найдена: nonexistent_cmd", str(context.exception))

    def test_substitute_variables_raises_exception(self):
        with patch.object(self.state, '_substitute_variable', side_effect=Exception("Substitution error")):
            commands = [Command(command="echo", arguments=["${VAR}"])]
            with self.assertRaises(CommandError) as context:
                self.state.evaluate_commands(commands)
            
            self.assertIn("Ошибка подстановки переменных: Substitution error", str(context.exception))

    def test_evaluate_builtin_command_raises_command_error(self):
        self.mock_builtin_command.side_effect = CommandError("Builtin failure")
        commands = [Command(command="builtin_cmd", arguments=[])]
        with self.assertRaises(CommandError) as context:
            self.state.evaluate_commands(commands)
        
        self.assertEqual(self.state.prev_return_code, 1)
        self.assertIn("Ошибка выполнения встроенной команды 'builtin_cmd': Builtin failure", str(context.exception))

    def test_evaluate_builtin_command_raises_unexpected_error(self):
        self.mock_builtin_command.side_effect = ValueError("Unexpected error")
        commands = [Command(command="builtin_cmd", arguments=[])]
        with self.assertRaises(CommandError) as context:
            self.state.evaluate_commands(commands)
        
        self.assertEqual(self.state.prev_return_code, 1)
        self.assertIn("Непредвиденная ошибка при выполнении команды 'builtin_cmd': Unexpected error", str(context.exception))

if __name__ == '__main__':
    unittest.main()
