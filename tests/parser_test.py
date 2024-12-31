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

if __name__ == '__main__':
    unittest.main()