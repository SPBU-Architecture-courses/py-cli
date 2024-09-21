# PyCLI Project

**PyCLI** is a command-line interpreter written in Python.

## Overview

The PyCLI interpreter is similar to Bash, supporting most essential CLI functionality, including:

- **Environment management**: creation of new variables (commands like `name=value`, `$` operator)
- **Single and double quotes**: full and weak quoting
- **Pipelines**: connecting commands via pipes (`|`)
- **External program execution**
- **Input/output redirection**

Additionally, the interpreter supports command history, suggestions, and autocomplete during input.

Built-in commands include `cat`, `echo`, `wc`, `pwd`, `exit`, and `grep`. All other commands are executed by searching directories listed in the `PATH` environment variable.

## Installation
TODO

## Development Team

This project is developed as part of the "Architecture and Design of Information Systems" course by students of the Faculty of Mathematics and Computer Science at Saint Petersburg State University:
- [Nikita Fomin](https://github.com/heartmarshall)
- [Mark Bezmaslov](https://github.com/mark47B)
- [Viktor Zakharov](https://github.com/vatican1)

## Additional Resources
Below are the resources used during the development process, including helpful articles, books, and example projects:
The Architecture of Open Source Applications (Volume 1), The Bourne-Again Shell: [article about bash architecture](https://aosabook.org/en/v1/bash.html)

