# Claw Compiler  

**The Reference Implementation for the NyanLang Programming Language**

[<-- Back to the NyanLang Ecosystem README](../README.md)

---

This directory contains the source code, tests, and documentation for `claw-compiler`, the official reference implementation for NyanLang. This guide is focused on the development workflow for the compiler itself.

## 🚧 Current Status: v0.0.3

The foundation of the compiler is laid. The current version includes:
* ✅ A complete and robust **Lexer**.
* ✅ **100% unit test coverage** for the Lexer.
* ✅ A scalable, file-based **integration test framework**.

## 🗺️ Roadmap to v0.1.0

My immediate goal is to reach `v0.1.0`, the first **interpretable and runnable** version of NyanLang.

1.  ✅ **v0.0.3: Lexer** (Complete)
2.  ➡️ **In Progress: Parser** - Translating the token stream into an Abstract Syntax Tree (AST).
3.  **Upcoming: Evaluator/Interpreter** - Walking the AST to execute the code.
4.  **Target: v0.1.0** - A functional, usable NyanLang interpreter.

*A high-performance LLVM backend is a long-term goal and will be explored after the interpreter is mature.*

## 🛠️ Development Workflow

Follow these steps to set up a local development environment and contribute to the compiler.

### 1. Initial Setup

First, set up the project on your local machine.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Karesis/NyanLang.git
    cd NyanLang
    ```

2.  **Create and activate a Python virtual environment using uv:**
    *It is highly recommended to work from within the `NyanLang` root directory.*
    ```bash
    # Create a virtual environment named .venv
    uv venv -p pypy@3.11

    # Activate on Windows
    .\.venv\Scripts\activate

    # Activate on macOS/Linux
    # source .venv/bin/activate
    ```

3.  **Install the project in editable mode:**
    *This command installs the `claw-compiler` project and its dependencies using `uv`.*
    ```bash
    uv pip install .[dev]
    uv pip install -e claw-compiler
    ```

### 2. Coding & Quality Checks

After making changes to the code inside `claw-compiler/src`, always run the following quality checks from the `NyanLang/claw-compiler` directory.

```bash
# Navigate to the compiler's directory first
cd claw-compiler
````

1.  **Run Ruff to check for linting errors and format code:**

    ```bash
    uv run ruff check .
    uv run ruff format .
    ```

2.  **Run MyPy for static type analysis:**

    ```bash
    uv run mypy .
    ```

### 3\. Running the Test Suite

The test suite is the primary way to verify functionality. All tests are run using `pytest`.

1.  **Run all tests:**
    *From the `NyanLang/claw-compiler` directory:*

    ```bash
    uv run pytest
    ```

2.  **Check test coverage:**
    *To get a coverage summary in your terminal:*

    ```bash
    uv run pytest --cov=claw --cov-report=term-missing
    ```

    *To generate a beautiful, interactive HTML report:*

    ```bash
    uv run pytest --cov=claw --cov-report=html
    ```

    Then open the `htmlcov/index.html` file in your browser to explore the results.

### 4\. Snapshot Testing Workflow

> **Important:** The integration tests use a "snapshot" pattern. Understanding this two-step process is crucial.

When you add a new `.nyan` file to `examples/source/` or modify an existing one, the testing workflow is as follows:

1.  **First Run (Generate / Update Snapshot):**
    Run `uv run pytest`. The test for your new or modified file will **fail intentionally**. This is expected behavior. The test runner will automatically create or update the corresponding `.tokens` snapshot file in the `examples/expected_token/` directory.

2.  **Second Run (Verify):**
    After the first run, you must **manually review the new/updated snapshot file** to ensure its content is correct. Once you have verified it, run `uv run pytest` again. This time, the test will compare the lexer's output against the now-correct snapshot, and it should pass.

This workflow ensures that any change to the language's output is deliberate and reviewed.

-----

*This document was last updated on July 1, 2025.*

