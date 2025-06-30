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

3. when you want to have some tests, straightly run uv run pytest,
then run
```
uv run pytest --cov=claw --cov-report=term-missing
```
for coverage test, and run
```
uv run pytest --cov=claw --cov-report=html
```
for the html report for beautiful report.

4. when you need test, dont forget to run pytest then run again. 
the first time it will generate/update files like .tokens in examples/, and the second time it will tests if they are right.