import sys
import logging
from package.parser.parser import parse_command_line
from package.state.state import State
from package.commands.commands import StateCommands

def main():
    logging.basicConfig(level=logging.ERROR, format='%(message)s')
    
    state_commands = StateCommands()
    state = State(state_commands)
    
    try:
        while True:
            try:
                command_input = input("> ")
            except EOFError:
                print()
                break

            if not command_input.strip():
                continue

            try:
                commands = parse_command_line(command_input)
                
                if not commands:
                    continue

                state.evaluate_commands(commands)

            except Exception as e:
                logging.error(f"Ошибка: {e}")

    except KeyboardInterrupt:
        print("\nВыход.")
        sys.exit(0)

if __name__ == "__main__":
    main()