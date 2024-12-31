import unittest
import os
from unittest.mock import patch
from package.commands.commands import StateCommands, CommandError

class TestStateCommands(unittest.TestCase):
    def setUp(self):
        self.commands = StateCommands()

    def test_echo(self):
        args = ["Hello", "World!"]
        expected_output = "Hello World!"
        result = self.commands.echo(args)
        self.assertEqual(result, expected_output)
        self.assertEqual(self.commands.prev_command_output, expected_output)

    def test_pwd_no_args(self):
        with patch('os.getcwd', return_value='/home/user'):
            result = self.commands.pwd([])
            self.assertEqual(result, '/home/user')
            self.assertEqual(self.commands.prev_command_output, '/home/user')

    def test_pwd_with_args(self):
        with self.assertRaises(CommandError) as context:
            self.commands.pwd(['extra_arg'])
        self.assertEqual(str(context.exception), "pwd: too many arguments")

    def test_cat_no_args_with_prev_output(self):
        self.commands.prev_command_output = "Previous content"
        result = self.commands.cat([])
        self.assertEqual(result, "Previous content")
        self.assertEqual(self.commands.prev_command_output, "")

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_cat_file_not_found(self, mock_file):
        filenames = ['nonexistent.txt']
        with self.assertRaises(CommandError) as context:
            self.commands.cat(filenames)
        self.assertEqual(str(context.exception), "File not found: nonexistent.txt")
        mock_file.assert_called_with('nonexistent.txt', 'r', encoding='utf-8')

    def test_wc_no_args_no_prev_output(self):
        self.commands.prev_command_output = None
        with self.assertRaises(CommandError) as context:
            self.commands.wc([])
        self.assertEqual(str(context.exception), "Usage: wc [FILE]")

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_wc_file_not_found(self, mock_file):
        filenames = ['nonexistent.txt']
        with self.assertRaises(CommandError) as context:
            self.commands.wc(filenames)
        self.assertEqual(str(context.exception), "File not found: nonexistent.txt")
        mock_file.assert_called_with('nonexistent.txt', 'r', encoding='utf-8')

    def test_exit_command_with_args(self):
        with self.assertRaises(CommandError) as context:
            self.commands.exit_command(['now'])
        self.assertEqual(str(context.exception), "exit: слишком много аргументов")

    @patch('os._exit')
    def test_exit_command_no_args(self, mock_exit):
        self.commands.prev_return_code = 0
        self.commands.exit_command([])
        mock_exit.assert_called_with(0)


if __name__ == '__main__':
    unittest.main()
