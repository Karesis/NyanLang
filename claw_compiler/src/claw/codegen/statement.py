# src/claw/codegen/statement_generator.py

"""
此模块定义了 StatementGenerator，负责生成所有语句的 LLVM IR。
"""
from llvmlite import ir
from .. import ast

# 为了类型提示，避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main import CodeGen

class StatementGenerator:
    """
    语句生成器。

    负责将所有 ast.Statement 节点转换为相应的 LLVM IR 指令流。
    这个类本身是无状态的，它通过方法参数接收所有必要的上下文（如 IRBuilder）。
    """
    def __init__(self, generator: 'CodeGen'):
        # 持有主 CodeGen 的引用，以便访问其他生成器（如表达式）和全局模块
        self.g = generator

    def visit_statement(self, node: ast.Statement, builder: ir.IRBuilder) -> None:
        """
        【新的分发器】
        在已有上下文（builder）的情况下，分派到具体的语句 visit 方法。
        """
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name)
        # 现在，所有被调用的 visitor 都需要接收 builder
        visitor(node, builder)

    # ================================================================= #
    # VVV        在函数上下文内部（必须有 builder）执行的方法         VVV #
    # ================================================================= #

    def visit_LetStatement(self, node: ast.LetStatement, builder: ir.IRBuilder):
        # 【已移除】不再需要 if builder is None 检查。
        var_name = node.name.value
        var_type = self.g.types.get_llvm_type(node.type)
        
        # 使用传入的 builder，而不是 self.g.builder
        ptr = builder.alloca(var_type, name=var_name)
        
        self.g.symtab[var_name] = ptr
        
        if node.value:
            # 【重要】假定 ExpressionGenerator 也遵循此模式
            value = self.g.expressions.visit(node.value, builder)
            builder.store(value, ptr)

    def visit_ExpressionStatement(self, node: ast.ExpressionStatement, builder: ir.IRBuilder):
        # 【重要】将 builder 传递给表达式生成器
        self.g.expressions.visit(node.expression, builder)

    def visit_BlockStatement(self, node: ast.BlockStatement, builder: ir.IRBuilder):
        # 依次访问块内的每一条语句，并传递上下文
        for stmt in node.statements:
            self.visit_statement(stmt, builder)

    def visit_ReturnStatement(self, node: ast.ReturnStatement, builder: ir.IRBuilder):
        # 【已移除】不再需要 if builder is None 检查。
        if node.return_value:
            # 【重要】将 builder 传递给表达式生成器
            return_val = self.g.expressions.visit(node.return_value, builder)
            builder.ret(return_val)
        else:
            builder.ret_void()

    # ================================================================= #
    # VVV             在顶层（全局作用域）执行的方法                VVV #
    # ================================================================= #

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        """
        处理顶层的函数声明。
        这是创建 IRBuilder 上下文的入口点。
        """
        # --- 函数准备阶段 ---
        # 【设计讨论】清空符号表仍然是一个全局状态操作。
        # 更好的设计是为每个函数创建一个新的符号表作用域。我们稍后可以讨论这个。
        self.g.symtab.clear()

        # TODO: 扩展到支持更多函数
        if not (node.is_flow and node.name.value == "main"):
            return
        
        return_type = self.g.types.get_llvm_type(node.return_type)
        func_type = ir.FunctionType(return_type, [])
        func = ir.Function(self.g.module, func_type, name=node.name.value)
        
        # --- 函数体生成阶段 ---
        # 1. 【创建局部上下文】builder 是一个局部变量，不再是全局状态。
        entry_block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(entry_block)
        
        # 2. 【传递上下文】将新创建的 builder 显式传递给处理函数体的方法。
        self.visit_BlockStatement(node.body, builder)
        
        # --- 函数收尾阶段 ---
        # 3. 【使用局部上下文】使用这个局部的 builder 来完成收尾工作。
        if builder.block and not builder.block.is_terminated:
            if isinstance(return_type, ir.IntType):
                builder.ret(ir.Constant(return_type, 0))
            else:
                builder.ret_void()

        # 4. 【上下文销毁】方法执行完毕后，builder 变量自动销毁，没有副作用。
        #    不再需要 self.g.builder = None 这样的清理代码。