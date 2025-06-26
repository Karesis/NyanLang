# src/claw/codegen/expression_generator.py

"""
Copyright [2025] [杨亦锋]

Licensed under the Apache License, Version 2.0 (the "License");
... (保留您的许可证头部)

此模块定义了 ExpressionGenerator，负责生成所有表达式的 LLVM IR。
"""
from llvmlite import ir
from .. import ast

# 为了类型提示，避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main import CodeGen

class ExpressionGenerator:
    """
    表达式生成器。

    负责将所有 ast.Expression 节点转换为相应的 LLVM IR 值。
    """
    def __init__(self, generator: 'CodeGen'):
        # 持有主 CodeGen 的引用，以便访问共享状态和辅助方法
        self.g = generator

    def visit(self, node: ast.Expression) -> ir.Value:
        """
        根据表达式节点的具体类型，分派到相应的 visit 方法。
        """
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name) # 表达式必须有专门的 visit 方法
        return visitor(node)

    def visit_lvalue(self, node: ast.Expression) -> ir.Value:
        """
        处理可作为左值的表达式，返回其内存地址（指针）。
        左值是指可以出现在赋值符号左边的表达式，例如变量名或结构体成员。
        """
        if isinstance(node, ast.Identifier):
            return self.g.symtab[node.value]
        
        if isinstance(node, ast.MemberAccessExpression):
            # 递归调用 visit_lvalue 来获取结构体本身的地址
            struct_ptr = self.visit_lvalue(node.object)
            struct_type = struct_ptr.type.pointee
            
            if not isinstance(struct_type, ir.IdentifiedStructType):
                 raise TypeError("Cannot access member of a non-struct type")
                 
            # 通过 TypeManager 查询字段信息
            struct_type_name = struct_type.name
            field_name = node.field.value
            field_index = self.g.types.struct_fields[struct_type_name][field_name]
            
            # 使用 gep (getelementptr) 指令计算成员的地址
            return self.g.builder.gep(
                struct_ptr,
                [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)],
                name=f"{struct_type_name}_{field_name}_addr"
            )
        
        raise TypeError(f"Expression of type {type(node)} cannot be an L-value")

    def visit_AssignmentExpression(self, node: ast.AssignmentExpression) -> ir.Value:
        # 右侧的值，需要递归访问
        value_to_store = self.visit(node.value)
        # 左侧的地址
        destination_ptr = self.visit_lvalue(node.left)
        
        self.g.builder.store(value_to_store, destination_ptr)
        return value_to_store

    def visit_StructLiteral(self, node: ast.StructLiteral) -> ir.Value:
        # 通过 TypeManager 获取结构体类型
        struct_name = node.type_name.value
        struct_type = self.g.types.struct_types[struct_name]
        
        # 在栈上为结构体分配临时空间
        temp_ptr = self.g.builder.alloca(struct_type, name=f"{struct_name}_tmp")
        
        for ident, expr in node.members:
            field_name = ident.value
            field_index = self.g.types.struct_fields[struct_name][field_name]
            
            # 递归访问成员的值
            value_to_store = self.visit(expr)
            
            # 计算成员地址并存储值
            field_ptr = self.g.builder.gep(temp_ptr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)])
            self.g.builder.store(value_to_store, field_ptr)
            
        # 从栈上加载整个结构体的值并返回
        return self.g.builder.load(temp_ptr, name=f"{struct_name}_literal")

    def visit_MemberAccessExpression(self, node: ast.MemberAccessExpression) -> ir.Value:
        # 当成员访问作为右值使用时，我们先获取其地址，然后加载其值
        ptr_to_field = self.visit_lvalue(node)
        return self.g.builder.load(ptr_to_field, name=node.field.value)

    def visit_IntegerLiteral(self, node: ast.IntegerLiteral) -> ir.Constant:
        return ir.Constant(ir.IntType(32), node.value)

    def visit_Identifier(self, node: ast.Identifier) -> ir.LoadInstr:
        # 当标识符作为右值使用时，从符号表中找到其地址，然后加载其值
        return self.g.builder.load(self.g.symtab[node.value], name=node.value)

    def visit_InfixExpression(self, node: ast.InfixExpression) -> ir.Value:
        # 递归访问左右子表达式
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        match node.operator:
            case '+': return self.g.builder.add(left, right, name="addtmp")
            case '-': return self.g.builder.sub(left, right, name="subtmp")
            case '*': return self.g.builder.mul(left, right, name="multmp")
            case '/': return self.g.builder.sdiv(left, right, name="divtmp")
            
        raise NotImplementedError(f"Infix operator {node.operator} not implemented")