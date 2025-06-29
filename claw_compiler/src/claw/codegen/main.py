# src/claw/codegen/main.py

"""
此文件定义了 CodeGen 的主类和核心协调逻辑。
它负责初始化 LLVM、管理全局状态，并将具体的代码生成任务分派给子生成器。
"""
from llvmlite import ir, binding
from .. import ast

# 从子生成器模块中导入类
from .type import TypeManager
from .statement import StatementGenerator
from .expression import ExpressionGenerator

class CodeGen:
    """
    主代码生成器类，作为协调器。

    它管理着 LLVM 模块、符号表等全局状态，并将对 AST 节点的访问
    委托给专门的、无状态的子生成器。
    """
    def __init__(self):
        # 1. LLVM 和目标机器的初始化
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        self.target_triple = binding.get_default_triple()
        target = binding.Target.from_triple(self.target_triple)
        self.target_machine = target.create_target_machine()

        # 2. 全局状态
        self.module = ir.Module(name="nyan_module")
        self.module.triple = self.target_triple
        self.module.data_layout = str(self.target_machine.target_data)

        # 【已移除】不再需要 builder 作为类的成员。
        # self.builder: Optional[ir.IRBuilder] = None
        
        # 符号表依然是全局的，用于函数间的符号查找（未来可能支持全局变量）
        self.symtab: dict[str, ir.Value] = {}

        # 3. 组合子生成器
        # 将主 CodeGen 实例 (self) 传递给它们，以共享状态和辅助方法
        self.types = TypeManager(self)
        self.statements = StatementGenerator(self)
        self.expressions = ExpressionGenerator(self)

    def generate(self, program_node: ast.Program) -> str:
        """
        【已修改】生成 LLVM IR 字符串的顶层入口。
        它接收一个 Program 节点，并驱动整个编译流程。
        """
        self.visit_Program(program_node)
        return str(self.module)

    # 【已移除】通用的 visit 方法已被移除。
    # 顶层的分派逻辑由 generate 和 visit_Program 精确控制。
    # def visit(self, node: ast.Node): ...

    def visit_Program(self, node: ast.Program):
        """
        【职责明确】程序节点的访问方法，是代码生成的主流程。
        定义了代码生成的两个主要阶段：类型定义和函数生成。
        """
        # 第一遍：委托给 TypeManager 处理所有结构体定义
        # 这确保了在生成函数代码之前，所有自定义类型都已声明。
        for stmt in node.statements:
            if isinstance(stmt, ast.StructDefinition):
                # 假设 TypeManager 中也有类似的顶层 visit 方法
                self.types.visit_StructDefinition(stmt)
        
        # 第二遍：委托给 StatementGenerator 处理所有函数/流程定义
        # 这是我们重构的成果，直接调用顶层专用的 visit 方法。
        for stmt in node.statements:
            if isinstance(stmt, ast.FunctionDeclaration):
                self.statements.visit_FunctionDeclaration(stmt)