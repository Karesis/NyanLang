# main.py (final version)

import sys
from claw.lexer import Lexer
from claw.parser import Parser
from claw.codegen import CodeGen

def main():
    source_code = """
    def { x: i32, y: i32 } Point

    @main -> i32
    {
        p: Point = Point{ x: 10, y: 20 }
        
        z: i32 = 5
        p.y = p.x + z // p.y should become 10 + 5 = 15

        ret p.y
    }
    main;
    """
    # ... (后续的 lexer, parser, codegen 调用和文件写入都不变) ...
    print("--- 1. Lexing ---"); lexer = Lexer(source_code)
    print("--- 2. Parsing ---"); parser = Parser(lexer)
    ast = parser.parse_program()
    if parser.errors:
        print("Parser has errors:"); [print(err) for err in parser.errors]; return
    print("AST generated successfully.")
    print("--- 3. Code Generation ---"); codegen = CodeGen()
    llvm_ir = codegen.generate(ast)
    print("\n--- Generated LLVM IR ---"); print(llvm_ir)
    output_filename = "output.ll"
    with open(output_filename, "w") as f: f.write(llvm_ir)
    print(f"\nLLVM IR successfully saved to {output_filename}")

if __name__ == "__main__":
    main()