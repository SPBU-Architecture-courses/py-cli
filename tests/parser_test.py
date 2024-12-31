import unittest

from package.state.state import Command
from package.parser.parser import parse_command_line

class TestParseCommandLine(unittest.TestCase):

    def test_empty_string(self):
        input_str = ""
        expected = []
        result = parse_command_line(input_str)
        self.assertEqual(result, expected)

    def test_single_command_no_arguments(self):
        input_str = "ls"
        expected = [Command(command="ls", arguments=[])]
        result = parse_command_line(input_str)
        self.assertEqual(result, expected)

    def test_empty_commands_between_pipes(self):
        input_str = "echo 'Start' || echo 'End'"
        expected = [
            Command(command="echo", arguments=["'Start'"]),
            Command(command="echo", arguments=["'End'"])
        ]
        result = parse_command_line(input_str)
        self.assertEqual(result, expected)

    def test_only_pipes(self):
        input_str = "|||"
        expected = []
        result = parse_command_line(input_str)
        self.assertEqual(result, expected)


    def test_commands_with_special_characters(self):
        input_str = "echo 'Hello, World!' | cat -e"
        expected = [
            Command(command="echo", arguments=["'Hello,", "World!'"]),
            Command(command="cat", arguments=["-e"])
        ]
        result = parse_command_line(input_str)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()