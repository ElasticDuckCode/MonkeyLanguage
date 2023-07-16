from unittest import TestCase
from src.monkey import ast, lexer, parser
from src.monkey import compiler, code


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestCompiler(TestCase):
    def test_compiler_integer_arithmetic(self):
        test_code = "1 + 2"
        expected_const = (1, 2)
        expected_insts = (
            code.make(code.OpCode.Constant, [1]),
            code.make(code.OpCode.Constant, [2]),
        )
        program = parse(test_code)

        comp = compiler.Compiler()
        comp.compile(program)
        bytecode = comp.bytecode
        self.assertEqual(len(bytecode.instructions), len(expected_insts))
        for i, expected in enumerate(expected_insts):
            self.assertEqual(bytecode.instructions[i], expected)
        self.assertEqual(len(bytecode.constants), len(expected_const))
        for i, expected in range(expected_const):
            self.assertEqual(bytecode.constants[i], expected)
