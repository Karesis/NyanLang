1. Use 
```
uv pip install -e claw-compiler
```
in the NyanLang root to install the project Claw for dev.

2. Then cd to claw-compiler, and use 
```
uv run ruff check
uv run mypy .
```
everytime you edit something.