# src/claw/codegen/type_manager.py

"""
Copyright [2025] [杨亦锋]

Licensed under the Apache License, Version 2.0 (the "License");
... (保留您的许可证头部)

此模块定义了 TypeManager，负责管理和生成所有与类型相关的 LLVM IR。
包括结构体定义和基础类型映射。
"""
from llvmlite import ir
from .. import ast

# 为了类型提示，避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .main import CodeGen


class TypeManager:
    """
    类型管家。

    负责处理所有与类型定义相关的逻辑，将 AST 中的类型信息
    转换为 LLVM IR 中的类型。
    """
    def __init__(self, generator: 'CodeGen'):
        # 持有主 CodeGen 的引用，以便访问全局状态（如 LLVM module）
        self.g = generator
        
        # 将与类型相关的状态从主 CodeGen 类移动到这里
        self.struct_types: dict[str, ir.IdentifiedStructType] = {}
        self.struct_fields: dict[str, dict[str, int]] = {}
        
        # 语言内置的基础类型映射
        self.llvm_type_map = {
            "i32": ir.IntType(32),
            # 未来可以添加更多类型，如 "f64", "bool" 等
        }

    def get_llvm_type(self, type_node: ast.TypeNode) -> ir.Type:
        """
        将 AST 类型节点转换为 LLVM 类型。
        这是一个统一的类型查询接口。
        """
        type_name = type_node.name
        
        # 首先查找内置类型
        if type_name in self.llvm_type_map:
            return self.llvm_type_map[type_name]
            
        # 然后查找用户定义的结构体类型
        if type_name in self.struct_types:
            return self.struct_types[type_name]
            
        raise TypeError(f"Unknown type: {type_name}")

    def visit_StructDefinition(self, node: ast.StructDefinition):
        """
        处理 AST 中的结构体定义节点。

        在 LLVM 模块中创建一个新的、已命名的结构体类型，并定义其成员布局。
        """
        struct_name = node.name.value
        
        # 在 LLVM 上下文中创建一个“已识别的”（identified）结构体类型
        # 这允许我们先创建一个空的壳子，然后再填充它的具体成员（解决循环引用问题）
        struct_type = self.g.module.context.get_identified_type(struct_name)
        
        # 注册这个新类型和它的字段映射表
        self.struct_types[struct_name] = struct_type
        
        field_types = []
        field_map = {}
        for i, (ident, type_node) in enumerate(node.fields):
            # 递归调用 get_llvm_type 来解析字段的类型
            field_types.append(self.get_llvm_type(type_node))
            field_map[ident.value] = i
            
        # 设置结构体的主体（成员类型列表）
        struct_type.set_body(*field_types)
        self.struct_fields[struct_name] = field_map