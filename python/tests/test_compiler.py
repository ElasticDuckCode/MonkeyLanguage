from unittest import TestCase

from src.monkey import ast, code, compiler, lexer, obj, parser


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestCompiler(TestCase):
    def test_compiler_integer_arithmetic(self):
        test_code_list = [
            "1 + 2",
            "3 - 4",
            "4 * 5",
            "2 / 1",
        ]
        expected_const_list = [(1, 2), (3, 4), (4, 5), (2, 1)]
        insts_list = [
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Add),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Sub),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Mul),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Div),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            expected_insts = b""
            for inst in insts:
                expected_insts += inst
            program = parse(test_code)
            comp = compiler.Compiler()
            comp.compile(program)
            bytecode = comp.bytecode
            err_msg = (
                f"\nwant:\n{code.instructions_to_string(expected_insts)}"
                f"\ngot:\n{code.instructions_to_string(bytecode.instructions)}"
            )
            self.assertEqual(len(bytecode.instructions), len(expected_insts), err_msg)
            self.assertEqual(bytecode.instructions, expected_insts, err_msg)
            self.assertEqual(len(bytecode.constants), len(expected_const))
            for i, expected in enumerate(expected_const):
                self.assertIsInstance(bytecode.constants[i], obj.Integer)
                self.assertEqual(bytecode.constants[i].value, expected)

    def test_compiler_pop_constant(self):
        test_code = "1; 2;"
        expected_const = (1, 2)
        insts = [
            code.make(code.OpCode.PConstant, 0),
            code.make(code.OpCode.Pop),
            code.make(code.OpCode.PConstant, 1),
            code.make(code.OpCode.Pop),
        ]
        expected_insts = b""
        for inst in insts:
            expected_insts += inst
        program = parse(test_code)
        comp = compiler.Compiler()
        comp.compile(program)
        bytecode = comp.bytecode
        err_msg = (
            f"\nwant:\n{code.instructions_to_string(expected_insts)}"
            f"\ngot:\n{code.instructions_to_string(bytecode.instructions)}"
        )
        self.assertEqual(len(bytecode.instructions), len(expected_insts), err_msg)
        self.assertEqual(bytecode.instructions, expected_insts, err_msg)
        self.assertEqual(len(bytecode.constants), len(expected_const))
        for i, expected in enumerate(expected_const):
            self.assertIsInstance(bytecode.constants[i], obj.Integer)
            self.assertEqual(bytecode.constants[i].value, expected)

    def test_compiler_boolean_expressions(self):
        test_code_list = ["true;", "false;"]
        insts_list = [
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PFalse),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, insts in zip(test_code_list, insts_list):
            expected_insts = b""
            for inst in insts:
                expected_insts += inst
            program = parse(test_code)
            comp = compiler.Compiler()
            comp.compile(program)
            bytecode = comp.bytecode
            err_msg = (
                f"\nwant:\n{code.instructions_to_string(expected_insts)}"
                f"\ngot:\n{code.instructions_to_string(bytecode.instructions)}"
            )
            self.assertEqual(len(bytecode.instructions), len(expected_insts), err_msg)
            self.assertEqual(bytecode.instructions, expected_insts, err_msg)
