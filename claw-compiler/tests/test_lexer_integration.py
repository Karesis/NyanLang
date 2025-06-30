import pytest
from pathlib import Path

# 你的包名叫 claw，我们从这里导入
from claw.lexer import Lexer
from claw.tokens import TokenType , Token

# ===================================================================
# 1. 定义清晰、具体的路径常量
# ===================================================================
# Path(__file__) 是当前文件 (test_integration.py) 的路径
# .parent 是 tests/ 目录
# .parent.parent 就是项目根目录 (claw-compiler/)
ROOT_DIR = Path(__file__).parent.parent

# 从根目录出发，定义各个子目录
EXAMPLES_DIR = ROOT_DIR / "examples"
SOURCE_DIR = EXAMPLES_DIR / "source"
EXPECTED_TOKEN_DIR = EXAMPLES_DIR / "expected_token"

# 确保存放快照的目录存在，如果不存在就自动创建
EXPECTED_TOKEN_DIR.mkdir(parents=True, exist_ok=True)


# ===================================================================
# 2. 自动发现在 source/ 目录下的所有 .nyan 文件
# ===================================================================
SOURCE_FILES = list(SOURCE_DIR.glob("**/*.nyan"))
if not SOURCE_FILES:
    # 提供一个更明确的警告信息
    print(f"\nWarning: No .nyan files found in the directory: {SOURCE_DIR}")
    print("Integration tests for the lexer will be skipped.")


# ===================================================================
# 3. 为每个发现的源文件创建一个参数化的测试
# ===================================================================
@pytest.mark.parametrize("source_path", SOURCE_FILES)
def test_nyan_file_lexing(source_path: Path):
    """
    对 examples/source/ 下的每个 .nyan 文件进行词法分析，
    并将其结果与 examples/expected_token/ 下的快照进行比对。
    """
    print(f"\n--- Testing: {source_path.relative_to(ROOT_DIR)} ---")

    # --- 步骤 1: 读取源文件并生成实际输出 ---
    source_code = source_path.read_text(encoding="utf-8")
    lexer = Lexer(source_code)

    actual_tokens: list[Token] = []
    while (token := lexer.next_token()).token_type != TokenType.EOF:
        actual_tokens.append(token)
    
    actual_output = "\n".join(repr(t) for t in actual_tokens)

    # --- 步骤 2: 构建期望的快照文件路径 ---
    # 这是本次修正的核心！
    # b. 创建快照文件名，例如 'happy_path.nyan.tokens'
    snapshot_filename: str = source_path.with_suffix(".nyan.tokens").name
    # c. 将快照文件名与期望的目录拼接起来
    snapshot_path: Path = EXPECTED_TOKEN_DIR / snapshot_filename

    print(f"Expecting snapshot at: {snapshot_path.relative_to(ROOT_DIR)}")

    # --- 步骤 3: 快照对比或创建 ---
    if not snapshot_path.exists():
        snapshot_path.write_text(actual_output, encoding="utf-8")
        pytest.fail(
            f"\nSnapshot file was not found. A new one has been created.\n"
            f"  - Source: {source_path.relative_to(ROOT_DIR)}\n"
            f"  - Snapshot: {snapshot_path.relative_to(ROOT_DIR)}\n"
            f"Please review the new snapshot file and run pytest again."
        )

    expected_output = snapshot_path.read_text(encoding="utf-8")
    
    assert actual_output == expected_output