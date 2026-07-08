# Python execution rules

Do not run Python directly with python, python3, pip, pip3, pytest, mypy, or ruff.

Always use uv for Python-related commands.

UV_SYSTEM_CERTS is already configured globally in Claude Code settings, so do not prefix commands with `export UV_SYSTEM_CERTS=true &&`.

Correct examples:

- `uv run -- python -m pytest`
- `uv run -- python path/to/script.py`
- `uv run -- ruff check .`
- `uv run -- mypy .`

Incorrect examples:

- `python3 script.py`
- `python -m pytest`
- `pip install package`
- `export UV_SYSTEM_CERTS=true && uv run -- python -m pytest`
