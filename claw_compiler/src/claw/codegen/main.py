# src/claw/codegen/main.py

"""
Copyright [2025] [杨亦锋]

Licensed under the Apache License, Version 2.0 (the "License");
... (保留您的许可证头部)

此文件定义了 CodeGen 的主类和核心协调逻辑。
它负责初始化 LLVM、管理全局状态，并将具体的代码生成任务分派给子生成器。
"""
from llvmlite import ir, binding
from .. import ast

# 从即将创建的子生成器模块中导入类
from .type import TypeManager
from .statement import StatementGenerator
from .expression import ExpressionGenerator

class CodeGen:
    """
    主代码生成器类，作为协调器。

    它管理着 LLVM 模块、IR 构建器、符号表等全局状态，
    并将对 AST 节点的访问委托给专门的子生成器。
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
        self.module.data_layout = self.target_machine.target_data
        
        self.builder: ir.IRBuilder = None
        self.symtab: dict[str, ir.Value] = {}

        # 3. 组合子生成器
        # 将主 CodeGen 实例 (self) 传递给它们，以共享状态和辅助方法
        self.types = TypeManager(self)
        self.statements = StatementGenerator(self)
        self.expressions = ExpressionGenerator(self)

    def generate(self, node: ast.Node) -> str:
        """生成 LLVM IR 字符串的顶层入口。"""
        self.visit(node)
        return str(self.module)

    def visit(self, node: ast.Node):
        """
        根据节点类型，将访问任务分派给相应的子生成器。
        这是一个通用的分派中心。
        """
        # 优先处理最具体的类型
        if isinstance(node, ast.StructDefinition):
            return self.types.visit_StructDefinition(node)
        elif isinstance(node, ast.Expression):
            return self.expressions.visit(node)
        elif isinstance(node, ast.Statement):
            return self.statements.visit(node)
        elif isinstance(node, ast.Program):
            return self.visit_Program(node)
        else:
            raise NotImplementedError(f'No visit method for {node.__class__.__name__}')

    def visit_Program(self, node: ast.Program):
        """
        程序节点的访问方法。
        定义了代码生成的两个主要阶段：类型定义和函数生成。
        """
        # 第一遍：委托给 TypeManager 处理所有结构体定义
        for stmt in node.statements:
            if isinstance(stmt, ast.StructDefinition):
                self.types.visit_StructDefinition(stmt)
        
        # 第二遍：委托给 StatementGenerator 处理所有函数/流程定义
        for stmt in node.statements:
            if isinstance(stmt, ast.FunctionDeclaration):
                self.statements.visit_FunctionDeclaration(stmt)