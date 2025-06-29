# src/claw/codegen/expression_generator.py

"""
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

    def visit(self, node: ast.Expression, builder: ir.IRBuilder) -> ir.Value:
        """
        【已修改】根据表达式节点的具体类型，分派到相应的 visit 方法。
        现在接收并传递 builder 上下文。
        """
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name)
        # 将 builder 传递给具体的 visit 方法
        return visitor(node, builder)

    def visit_lvalue(self, node: ast.Expression, builder: ir.IRBuilder) -> ir.Value:
        """
        【已修改】处理可作为左值的表达式，返回其内存地址（指针）。
        接收 builder 以便用于 GEP 指令。
        """
        if isinstance(node, ast.Identifier):
            return self.g.symtab[node.value]
        
        if isinstance(node, ast.MemberAccessExpression):
            # 递归调用 visit_lvalue，并传递 builder
            struct_ptr = self.visit_lvalue(node.object, builder)
            struct_type = struct_ptr.type.pointee
            
            if not isinstance(struct_type, ir.IdentifiedStructType):
                raise TypeError("Cannot access member of a non-struct type")
                
            struct_type_name = struct_type.name
            field_name = node.field.value
            field_index = self.g.types.struct_fields[struct_type_name][field_name]
            
            # 使用传入的 builder
            return builder.gep(
                struct_ptr,
                [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)],
                name=f"{struct_type_name}_{field_name}_addr"
            )
        
        raise TypeError(f"Expression of type {type(node)} cannot be an L-value")

    def visit_AssignmentExpression(self, node: ast.AssignmentExpression, builder: ir.IRBuilder) -> ir.Value:
        # 递归访问，传递 builder
        value_to_store = self.visit(node.value, builder)
        destination_ptr = self.visit_lvalue(node.left, builder)
        
        # 使用传入的 builder
        builder.store(value_to_store, destination_ptr)
        return value_to_store

    def visit_StructLiteral(self, node: ast.StructLiteral, builder: ir.IRBuilder) -> ir.Value:
        struct_name = node.type_name.value
        struct_type = self.g.types.struct_types[struct_name]
        
        # 使用传入的 builder
        temp_ptr = builder.alloca(struct_type, name=f"{struct_name}_tmp")
        
        for ident, expr in node.members:
            field_name = ident.value
            field_index = self.g.types.struct_fields[struct_name][field_name]
            
            # 递归访问，传递 builder
            value_to_store = self.visit(expr, builder)
            
            # 使用传入的 builder
            field_ptr = builder.gep(temp_ptr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)])
            builder.store(value_to_store, field_ptr)
            
        # 使用传入的 builder
        return builder.load(temp_ptr, name=f"{struct_name}_literal")

    def visit_MemberAccessExpression(self, node: ast.MemberAccessExpression, builder: ir.IRBuilder) -> ir.Value:
        # 传递 builder
        ptr_to_field = self.visit_lvalue(node, builder)
        # 使用传入的 builder
        return builder.load(ptr_to_field, name=node.field.value)

    def visit_IntegerLiteral(self, node: ast.IntegerLiteral, _builder: ir.IRBuilder) -> ir.Constant:
        """
        【注意】这个方法实际上不需要 builder，因为它只创建了一个常量。
        但为了保持所有 visit 方法签名的一致性，我们仍然接收它，并用下划线 `_` 标记为未使用。
        这简化了主 `visit` 分发器的逻辑。
        """
        return ir.Constant(ir.IntType(32), node.value)

    def visit_Identifier(self, node: ast.Identifier, builder: ir.IRBuilder) -> ir.LoadInstr:
        # 使用传入的 builder
        return builder.load(self.g.symtab[node.value], name=node.value)

    def visit_InfixExpression(self, node: ast.InfixExpression, builder: ir.IRBuilder) -> ir.Value:
        # 递归访问，传递 builder
        left = self.visit(node.left, builder)
        right = self.visit(node.right, builder)
        
        # 使用传入的 builder
        match node.operator:
            case '+': return builder.add(left, right, name="addtmp")
            case '-': return builder.sub(left, right, name="subtmp")
            case '*': return builder.mul(left, right, name="multmp")
            case '/': return builder.sdiv(left, right, name="divtmp")
            
            case _:
                raise NotImplementedError(
                    f"Infix operator {node.operator} not implemented"
                )
            