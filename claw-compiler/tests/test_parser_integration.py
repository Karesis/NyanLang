"""
Snapshot integration tests for the Parser.

This test suite automatically discovers all `.nyan` files in the `examples/source`
directory. For each source file, it performs the following steps:
1.  Parses the source code into an Abstract Syntax Tree (AST).
2.  Checks for any parsing errors. If errors exist, the test fails.
3.  Converts the generated AST into its string representation.
4.  Compares this string output against a "snapshot" file located in the
    `examples/expected_ast` directory (e.g., `happy_path.nyan.ast`).

Snapshot Workflow:
-   If a snapshot file does not exist, the test will fail, but it will
    automatically create the new snapshot file for you.
-   You must then manually review this new snapshot to ensure it is correct.
-   Once verified, run pytest again. The test should now pass.
"""
import pytest
from pathlib import Path

# 从我们的包中导入所需的一切
from claw.lexer import Lexer
from claw.parser import create_parser
from claw.ast import Program

# ===================================================================
# 1. 定义清晰、具体的路径常量
# ===================================================================
# 从当前测试文件出发，定位到项目根目录
ROOT_DIR = Path(__file__).parent.parent
EXAMPLES_DIR = ROOT_DIR / "examples"
SOURCE_DIR = EXAMPLES_DIR / "source"
# 这是我们新的快照目录
EXPECTED_AST_DIR = EXAMPLES_DIR / "expected_ast"

# 确保存放 AST 快照的目录存在
EXPECTED_AST_DIR.mkdir(parents=True, exist_ok=True)


# ===================================================================
# 2. 自动发现所有 .nyan 源文件
# ===================================================================
SOURCE_FILES = list(SOURCE_DIR.glob("**/*.nyan"))
if not SOURCE_FILES:
    print(f"\nWarning: No .nyan files found in {SOURCE_DIR}. Parser integration tests will be skipped.")


# ===================================================================
# 3. 为每个源文件创建一个参数化的快照测试
# ===================================================================
@pytest.mark.parametrize("source_path", SOURCE_FILES)
def test_nyan_file_parsing(source_path: Path):
    """
    Parses a .nyan file and compares its AST string representation
    against a snapshot file.
    """
    print(f"\n--- Testing Parser on: {source_path.relative_to(ROOT_DIR)} ---")

    # --- 步骤 1: 读取源文件并生成实际的 AST 输出 ---
    source_code = source_path.read_text(encoding="utf-8")
    lexer = Lexer(source_code)
    parser = create_parser(lexer)
    program: Program = parser.parse_program()

    # --- 步骤 2: 检查解析错误 ---
    # 在对比快照之前，必须先确保解析过程没有错误。
    if parser.errors:
        messages = "\n".join([str(e) for e in parser.errors])
        pytest.fail(
            f"Parser encountered errors while processing {source_path.name}:\n{messages}"
        )

    # 我们使用 str(program) 来获取 AST 的字符串表示
    actual_output = str(program)

    # --- 步骤 3: 构建期望的快照文件路径 ---
    snapshot_filename = source_path.with_suffix(".nyan.ast").name
    snapshot_path = EXPECTED_AST_DIR / snapshot_filename

    print(f"Expecting snapshot at: {snapshot_path.relative_to(ROOT_DIR)}")

    # --- 步骤 4: 快照对比或创建 ---
    if not snapshot_path.exists():
        snapshot_path.write_text(actual_output, encoding="utf-8")
        pytest.fail(
            f"\nSnapshot file was not found. A new one has been created.\n"
            f"  - Source: {source_path.relative_to(ROOT_DIR)}\n"
            f"  - Snapshot: {snapshot_path.relative_to(ROOT_DIR)}\n"
            f"Please review the new snapshot file and run pytest again."
        )

    expected_output = snapshot_path.read_text(encoding="utf-8").strip()
    
    assert actual_output.strip() == expected_output
