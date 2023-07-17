from unittest import TestCase

from src.monkey import ast, code, compiler, lexer, obj, parser


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestCompiler(TestCase):
    def test_compiler_integer_arithmetic(self):
        test_code = "1 + 2"
        expected_const = (1, 2)
        insts = [
            code.make(code.OpCode.Constant, 0),
            code.make(code.OpCode.Constant, 1),
            code.make(code.OpCode.Add),
        ]
        expected_insts = b""
        for inst in insts:
            expected_insts += inst
        program = parse(test_code)
        comp = compiler.Compiler()
        comp.compile(program)
        bytecode = comp.bytecode
        self.assertEqual(len(bytecode.instructions), len(expected_insts))
        self.assertEqual(bytecode.instructions, expected_insts)
        self.assertEqual(len(bytecode.constants), len(expected_const))
        for i, expected in enumerate(expected_const):
            self.assertIsInstance(bytecode.constants[i], obj.Integer)
            self.assertEqual(bytecode.constants[i].value, expected)
