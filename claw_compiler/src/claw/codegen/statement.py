# src/claw/codegen/statement_generator.py

"""
Copyright [2025] [杨亦锋]

Licensed under the Apache License, Version 2.0 (the "License");
... (保留您的许可证头部)

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
    """
    def __init__(self, generator: 'CodeGen'):
        # 持有主 CodeGen 的引用，以便访问共享状态和辅助方法
        self.g = generator

    def visit(self, node: ast.Statement) -> None:
        """
        根据语句节点的具体类型，分派到相应的 visit 方法。
        """
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name) # 语句必须有专门的 visit 方法
        visitor(node)

    def visit_LetStatement(self, node: ast.LetStatement):
        var_name = node.name.value
        # 通过 TypeManager 获取变量类型
        var_type = self.g.types.get_llvm_type(node.type)
        
        # 在当前函数的入口块中为变量分配栈空间
        ptr = self.g.builder.alloca(var_type, name=var_name)
        
        # 在符号表中注册变量名和其内存地址
        self.g.symtab[var_name] = ptr
        
        # 如果有初始值，则生成其值的 IR，并存入变量地址
        if node.value:
            # 委托 ExpressionGenerator 处理右侧的表达式
            value = self.g.expressions.visit(node.value)
            self.g.builder.store(value, ptr)

    def visit_ExpressionStatement(self, node: ast.ExpressionStatement):
        # 委托 ExpressionGenerator 处理表达式，但忽略其返回值
        self.g.expressions.visit(node.expression)

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        # --- 函数准备阶段 ---
        # 为新函数清空符号表（局部变量）
        self.g.symtab.clear()

        # 当前只实现 main 函数
        if not (node.is_flow and node.name.value == "main"):
            return
        
        # 通过 TypeManager 获取返回类型
        return_type = self.g.types.get_llvm_type(node.return_type)
        
        # 定义函数签名
        func_type = ir.FunctionType(return_type, [])
        func = ir.Function(self.g.module, func_type, name=node.name.value)
        
        # --- 函数体生成阶段 ---
        # 创建函数的入口基本块，并设置 IRBuilder
        entry_block = func.append_basic_block(name="entry")
        self.g.builder = ir.IRBuilder(entry_block)
        
        # 递归访问函数体内的所有语句
        self.visit(node.body)
        
        # --- 函数收尾阶段 ---
        # 如果函数最后一个基本块没有终结指令（如 ret），
        # 则为其添加一个默认的返回指令。
        if self.g.builder.block and not self.g.builder.block.is_terminated:
            if isinstance(return_type, ir.IntType):
                 self.g.builder.ret(ir.Constant(return_type, 0))
            else:
                 # 对于其他返回类型，可能需要不同的默认返回值
                 # 例如，对于指针类型返回 null
                 self.g.builder.ret_void() # 或者其他适当的默认返回

    def visit_BlockStatement(self, node: ast.BlockStatement):
        # 依次访问块内的每一条语句
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ReturnStatement(self, node: ast.ReturnStatement):
        if node.return_value:
            # 委托 ExpressionGenerator 处理返回值表达式
            return_val = self.g.expressions.visit(node.return_value)
            self.g.builder.ret(return_val)
        else:
            self.g.builder.ret_void()