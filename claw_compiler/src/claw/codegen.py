"""
   Copyright [2025] [杨亦锋]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from llvmlite import ir, binding
from . import ast

class CodeGen:
    def __init__(self):
        binding.initialize(); binding.initialize_native_target(); binding.initialize_native_asmprinter()
        self.target_triple = binding.get_default_triple()
        target = binding.Target.from_triple(self.target_triple)
        self.target_machine = target.create_target_machine()
        self.module = ir.Module(name="nyan_module")
        self.module.triple = self.target_triple; self.module.data_layout = self.target_machine.target_data
        self.builder: ir.IRBuilder = None
        self.symtab: dict[str, ir.Value] = {}
        self.struct_types: dict[str, ir.IdentifiedStructType] = {}
        self.struct_fields: dict[str, dict[str, int]] = {}

    def get_llvm_type(self, type_node: ast.TypeNode) -> ir.Type:
        type_name = type_node.name
        if type_name in llvm_type_map: return llvm_type_map[type_name]
        if type_name in self.struct_types: return self.struct_types[type_name]
        raise TypeError(f"Unknown type: {type_name}")

    def generate(self, node: ast.Node) -> str:
        self.visit(node)
        return str(self.module)

    def visit(self, node: ast.Node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node: ast.Node):
        raise NotImplementedError(f'No visit_{node.__class__.__name__} method for {node}')

    def visit_Program(self, node: ast.Program):
        # 第一遍：先访问所有结构体定义，建立类型“户籍库”
        for stmt in node.statements:
            if isinstance(stmt, ast.StructDefinition):
                self.visit(stmt)
        
        # 第二遍：然后访问所有函数/流程定义，生成它们的LLVM IR
        for stmt in node.statements:
            if isinstance(stmt, ast.FunctionDeclaration):
                self.visit(stmt)

    def visit_StructDefinition(self, node: ast.StructDefinition):
        struct_name = node.name.value
        struct_type = self.module.context.get_identified_type(struct_name)
        self.struct_types[struct_name] = struct_type
        field_types, field_map = [], {}
        for i, (ident, type_node) in enumerate(node.fields):
            field_types.append(self.get_llvm_type(type_node))
            field_map[ident.value] = i
        struct_type.set_body(*field_types)
        self.struct_fields[struct_name] = field_map

    def visit_lvalue(self, node: ast.Expression) -> ir.Value:
        if isinstance(node, ast.Identifier):
            return self.symtab[node.value]
        
        if isinstance(node, ast.MemberAccessExpression):
            struct_ptr = self.visit_lvalue(node.object)
            struct_type = struct_ptr.type.pointee
            if not isinstance(struct_type, ir.IdentifiedStructType):
                 raise TypeError("Cannot access member of a non-struct type")
            struct_type_name = struct_type.name
            field_name = node.field.value
            field_index = self.struct_fields[struct_type_name][field_name]
            return self.builder.gep(struct_ptr,
                [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)],
                name=f"{struct_type_name}_{field_name}_addr"
            )
        
        raise TypeError(f"Expression of type {type(node)} cannot be an L-value")

    def visit_AssignmentExpression(self, node: ast.AssignmentExpression) -> ir.Value:
        value_to_store = self.visit(node.value)
        destination_ptr = self.visit_lvalue(node.left)
        self.builder.store(value_to_store, destination_ptr)
        return value_to_store

    def visit_LetStatement(self, node: ast.LetStatement):
        var_name = node.name.value
        var_type = self.get_llvm_type(node.type)
        ptr = self.builder.alloca(var_type, name=var_name)
        self.symtab[var_name] = ptr
        if node.value:
            value = self.visit(node.value)
            self.builder.store(value, ptr)

    def visit_ExpressionStatement(self, node: ast.ExpressionStatement):
        self.visit(node.expression)

    def visit_StructLiteral(self, node: ast.StructLiteral) -> ir.Value:
        struct_name = node.type_name.value
        struct_type = self.struct_types[struct_name]
        temp_ptr = self.builder.alloca(struct_type, name=f"{struct_name}_tmp")
        for ident, expr in node.members:
            field_name = ident.value
            field_index = self.struct_fields[struct_name][field_name]
            value_to_store = self.visit(expr)
            field_ptr = self.builder.gep(temp_ptr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), field_index)])
            self.builder.store(value_to_store, field_ptr)
        return self.builder.load(temp_ptr, name=f"{struct_name}_literal")

    def visit_MemberAccessExpression(self, node: ast.MemberAccessExpression) -> ir.Value:
        ptr_to_field = self.visit_lvalue(node)
        return self.builder.load(ptr_to_field, name=node.field.value)

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        # 清空上一函数的符号表，为新函数做准备
        self.symtab.clear()

        if not (node.is_flow and node.name.value == "main"): return
        return_type = self.get_llvm_type(node.return_type)
        func_type = ir.FunctionType(return_type, [])
        func = ir.Function(self.module, func_type, name=node.name.value)
        entry_block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)
        self.visit(node.body)
        if self.builder.block and not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(return_type, 0))

    def visit_BlockStatement(self, node: ast.BlockStatement):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ReturnStatement(self, node: ast.ReturnStatement):
        self.builder.ret(self.visit(node.return_value))

    def visit_IntegerLiteral(self, node: ast.IntegerLiteral) -> ir.Constant:
        return ir.Constant(ir.IntType(32), node.value)

    def visit_Identifier(self, node: ast.Identifier) -> ir.LoadInstr:
        return self.builder.load(self.symtab[node.value], name=node.value)

    def visit_InfixExpression(self, node: ast.InfixExpression) -> ir.Value:
        left = self.visit(node.left)
        right = self.visit(node.right)
        match node.operator:
            case '+': return self.builder.add(left, right, name="addtmp")
            case '-': return self.builder.sub(left, right, name="subtmp")
            case '*': return self.builder.mul(left, right, name="multmp")
            case '/': return self.builder.sdiv(left, right, name="divtmp")
        raise NotImplementedError(f"Infix operator {node.operator} not implemented")

# 目前支持的类型
llvm_type_map = { "i32": ir.IntType(32) }