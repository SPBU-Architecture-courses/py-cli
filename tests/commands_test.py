import unittest
import os
from unittest.mock import mock_open, patch
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

    @patch('builtins.open', new_callable=mock_open, read_data='Hello World\nHello Python\nGoodbye World\n')
    def test_grep_with_files_matches(self, mock_file):
        args = ['Hello', 'file1.txt', 'file2.txt']
        mock_file.side_effect = [
            mock_open(read_data='Hello World\nHello Python\nGoodbye World\n').return_value,
            mock_open(read_data='Another Hello\nWorld Again\n').return_value
        ]
        expected_output = 'Hello World\nHello Python\nAnother Hello'
        result = self.commands.grep(args)
        self.assertEqual(result, expected_output)
        self.assertEqual(self.commands.prev_command_output, expected_output)
        self.assertEqual(mock_file.call_count, 2)
        mock_file.assert_any_call('file1.txt', 'r', encoding='utf-8')
        mock_file.assert_any_call('file2.txt', 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open, read_data='Hello World\nHello Python\nGoodbye World\n')
    def test_grep_with_files_no_matches(self, mock_file):
        args = ['Ruby', 'file1.txt']
        mock_file.return_value = mock_open(read_data='Hello World\nHello Python\nGoodbye World\n').return_value
        expected_output = ''
        result = self.commands.grep(args)
        self.assertEqual(result, expected_output)
        self.assertEqual(self.commands.prev_command_output, expected_output)
        mock_file.assert_called_once_with('file1.txt', 'r', encoding='utf-8')

    def test_grep_no_files_with_prev_output_matches(self):
        self.commands.prev_command_output = "Hello World\nHello Python\nGoodbye World\n"
        args = ['World']
        expected_output = 'Hello World\nGoodbye World'
        result = self.commands.grep(args)
        self.assertEqual(result, expected_output)
        self.assertEqual(self.commands.prev_command_output, expected_output)

    def test_grep_no_files_with_prev_output_no_matches(self):
        self.commands.prev_command_output = "Hello Python\nGoodbye Python\n"
        args = ['World']
        expected_output = ''
        result = self.commands.grep(args)
        self.assertEqual(result, expected_output)
        self.assertEqual(self.commands.prev_command_output, expected_output)

    def test_grep_no_files_no_prev_output(self):
        self.commands.prev_command_output = None
        args = ['pattern']
        with self.assertRaises(CommandError) as context:
            self.commands.grep(args)
        self.assertEqual(str(context.exception), "No input for grep")

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_grep_file_not_found(self, mock_file):
        args = ['pattern', 'nonexistent.txt']
        with self.assertRaises(CommandError) as context:
            self.commands.grep(args)
        self.assertEqual(str(context.exception), "File not found: nonexistent.txt")
        mock_file.assert_called_with('nonexistent.txt', 'r', encoding='utf-8')

    @patch('builtins.open', side_effect=IOError("Read error"))
    def test_grep_file_read_error(self, mock_file):
        args = ['pattern', 'file.txt']
        with self.assertRaises(CommandError) as context:
            self.commands.grep(args)
        self.assertEqual(str(context.exception), "Error reading file file.txt: Read error")
        mock_file.assert_called_with('file.txt', 'r', encoding='utf-8')

    @patch('builtins.open', new_callable=mock_open, read_data='Привет Мир\nHello World\nПривет Python\n')
    def test_grep_unicode_characters(self, mock_file):
        args = ['Привет', 'file.txt']
        expected_output = 'Привет Мир\nПривет Python'
        result = self.commands.grep(args)
        self.assertEqual(result, expected_output)
        self.assertEqual(self.commands.prev_command_output, expected_output)
        mock_file.assert_called_with('file.txt', 'r', encoding='utf-8')
    
    @patch('os.chdir')
    def test_cd_success(self, mock_chdir):
        args = ['package']
        result = self.commands.cd(args)
        mock_chdir.assert_called_once_with('package')
        self.assertEqual(result, "")

    def test_cd_invalid_number_of_args_multiple(self):
        args = ['dir1', 'dir2']
        with self.assertRaises(RuntimeError) as context:
            self.commands.cd(args)
        self.assertEqual(str(context.exception), "cd: требуется ровно один аргумент")

    @patch('os.chdir', side_effect=FileNotFoundError)
    def test_cd_directory_not_found(self, mock_chdir):
        args = ['non_existent_directory']
        with self.assertRaises(RuntimeError) as context:
            self.commands.cd(args)
        self.assertEqual(str(context.exception), "cd: директория не найдена: non_existent_directory")

    @patch('os.listdir')
    @patch('os.getcwd')
    def test_ls_no_args(self, mock_getcwd, mock_listdir):
        mock_getcwd.return_value = './'
        mock_listdir.return_value = ['file1.txt', 'file2.txt', 'dir1']

        result = self.commands.ls([])

        mock_getcwd.assert_called_once()
        mock_listdir.assert_called_once_with('./')
        expected_output = 'file1.txt\nfile2.txt\ndir1'
        self.assertEqual(result, expected_output)

    @patch('os.listdir')
    def test_ls_with_valid_directory(self, mock_listdir):
        args = ['/valid/directory']
        mock_listdir.return_value = ['fileA.py', 'fileB.py', 'script.sh']

        result = self.commands.ls(args)

        mock_listdir.assert_called_once_with('/valid/directory')
        expected_output = 'fileA.py\nfileB.py\nscript.sh'
        self.assertEqual(result, expected_output)

    @patch('os.listdir', side_effect=FileNotFoundError)
    def test_ls_directory_not_found(self, mock_listdir):
        args = ['/non/existent/directory']

        with self.assertRaises(RuntimeError) as context:
            self.commands.ls(args)

        mock_listdir.assert_called_once_with('/non/existent/directory')
        self.assertEqual(str(context.exception), "ls: директория не найдена: /non/existent/directory")

    @patch('os.listdir', side_effect=PermissionError("Нет доступа"))
    def test_ls_permission_error(self, mock_listdir):
        args = ['/protected/directory']

        with self.assertRaises(RuntimeError) as context:
            self.commands.ls(args)

        mock_listdir.assert_called_once_with('/protected/directory')
        self.assertEqual(str(context.exception), "ls: ошибка: Нет доступа")

    @patch('os.listdir')
    @patch('os.getcwd')
    def test_ls_empty_directory(self, mock_getcwd, mock_listdir):
        mock_getcwd.return_value = '/empty/directory'
        mock_listdir.return_value = []

        result = self.commands.ls([])

        mock_getcwd.assert_called_once()
        mock_listdir.assert_called_once_with('/empty/directory')
        expected_output = ''
        self.assertEqual(result, expected_output)

    @patch('os.listdir')
    def test_ls_with_multiple_arguments(self, mock_listdir):
        # Предположим, что функция должна принимать ровно один аргумент
        args = ['/dir1', '/dir2']
        # В данном случае, функция будет использовать args[0], то есть '/dir1'
        mock_listdir.return_value = ['item1', 'item2']

        result = self.commands.ls(args)

        mock_listdir.assert_called_once_with('/dir1')
        expected_output = 'item1\nitem2'
        self.assertEqual(result, expected_output)
    

if __name__ == '__main__':
    unittest.main()
