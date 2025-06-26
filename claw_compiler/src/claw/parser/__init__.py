# src/claw/parser/__init__.py
"""
Claw 编译器的解析器（Parser）包。

这个包的核心功能是将源代码的 Token 流转换为抽象语法树（AST）。
它对外暴露核心的 Parser 类，作为与编译器其他部分交互的唯一入口。
"""

# 从 .main 模块导入主 Parser 类，使其成为包级别可访问的属性
from .main import Parser

# (可选，但推荐) 定义 __all__，这会指定当其他模块使用
# from claw.parser import * 时，哪些名称会被导入。
# 这是一种明确包公共 API 的好习惯。
__all__ = ['Parser']