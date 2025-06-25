# NyanLang 🐱

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Welcome to the official repository for the Nyan language compiler! This project is the reference implementation for Nyan, a statically-typed, minimalistic programming language that compiles down to LLVM IR.

This project is currently under active development.

(ps: I have no icons for my language yet. If you have a good idea, pls let me know! I'm taking 🐱 as a temporary marker if my language.)

## ✨ Features

The Nyan language aims to provide modern language features in a simple and understandable package. The current implementation supports:

* **Static Typing**: Strong type checking with type annotations (e.g., `i32`).
* **LLVM Backend**: Compiles directly to high-performance LLVM Intermediate Representation (IR).
* **Structs**: Definition of custom data types.
* **Member Access**: Field access (`var.field`) and assignment (`var.field = ...`).
* **`@main` Flow**: A clear entry point for program execution.
* **Arithmetic Operations**: Standard integer math.
* **WIP**: Function calls, compound returns, and more are under development.

## 🚀 Getting Started

To get the compiler running on your local machine for development or testing, please follow the steps below.

### Prerequisites

You will need the following software installed on your machine:

1.  **Python**: Version 3.13 or higher.
2.  **LLVM**: A **full development version** of LLVM is required.
    * **Windows (Recommended)**: Install via **MSYS2** and `pacman -S mingw-w64-x86_64-llvm`. The official LLVM release for Windows might not include `llvm-config`, which is required by `llvmlite`.
    * **macOS**: Install via Homebrew: `brew install llvm`.
    * **Linux**: Install via your system's package manager (e.g., `sudo apt-get install llvm`).

    After installation, ensure that `llvm-config` is available in your system's `PATH` by running `llvm-config --version` in a **new** terminal.

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Karesis/NyanLang.git
    cd NyanLang/claw_compiler
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    # Create a virtual environment named .venv
    python -m venv .venv

    # Activate it (on Windows)
    .\.venv\Scripts\activate

    # On macOS/Linux, you would use:
    # source .venv/bin/activate
    ```

3.  **Install the project and its dependencies:**
    *The `claw_compiler` project is located in a subdirectory in NyanLang. We install it in "editable" mode (`-e`)*
    ```bash
    pip install -e ./claw_compiler
    ```

4.  **Run the compiler:**
    *The current entry point for testing is `main.py`.*
    ```bash
    python ./claw_compiler/main.py
    ```
    This will generate an `output.ll` file in the `claw_compiler` directory containing the LLVM IR for the sample code in `main.py`.

## 📝 Example

Here is a sample of what Nyan language code looks like:

```nyan
// Define a new struct type named 'Point'
def { x: i32, y: i32 } Point

// The main execution block, which returns an i32
@main -> i32
{
    // Declare and instantiate a variable 'p' of type 'Point'
    p: Point = Point{ x: 10, y: 20 }
    
    // Declare another variable
    z: i32 = 5

    // Access and modify a struct member
    p.y = p.x + z // p.y now becomes 15

    // Return the final value
    ret p.y
}

// Execute the main block
main;
````

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the Apache 2.0 License - see the `LICENSE` file for details.



