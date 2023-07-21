from unittest import TestCase

from src.monkey import ast, code, compiler, lexer, obj, parser


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestCompiler(TestCase):
    def verify_compiler(self, test_code, expected_const, insts):
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
        if len(expected_const):
            self.assertEqual(len(bytecode.constants), len(expected_const))
            for i, expected in enumerate(expected_const):
                match expected:
                    case bool():
                        self.assertIsInstance(bytecode.constants[i], obj.Boolean)
                    case int():
                        self.assertIsInstance(bytecode.constants[i], obj.Integer)
                    case _:
                        self.fail("Unknown object type. Please create new assert...")
                self.assertEqual(bytecode.constants[i].value, expected)

    def test_compiler_integer_arithmetic(self):
        test_code_list = [
            "1 + 2",
            "3 - 4",
            "4 * 5",
            "2 / 1",
            "-1",
        ]
        expected_const_list = [[1, 2], [3, 4], [4, 5], [2, 1], [1]]
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
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Minus),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_pop_constant(self):
        test_code = "1; 2;"
        expected_const = (1, 2)
        insts = [
            code.make(code.OpCode.PConstant, 0),
            code.make(code.OpCode.Pop),
            code.make(code.OpCode.PConstant, 1),
            code.make(code.OpCode.Pop),
        ]
        self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_boolean_expressions(self):
        test_code_list = [
            "true;",
            "false;",
            "1 > 2",
            "1 < 2",
            "1 != 2",
            "1 == 2",
            "true == false",
            "!true",
        ]
        expected_const_list = [(), (), (1, 2), (2, 1), (1, 2), (1, 2), (), ()]
        insts_list = [
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PFalse),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.GreaterThan, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.GreaterThan, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.NotEqual, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Equal, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.PFalse),
                code.make(code.OpCode.Equal, 1),
                code.make(code.OpCode.Pop),
            ),
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.Bang),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)

    def test_compiler_conditionals(self):
        test_code_list = [
            "if (true) { 10 }; 3333;",
            "if (true) { 10 } else { 20 }; 3333;",
        ]
        expected_const_list = [
            [10, 3333],
            [10, 20, 3333],
        ]
        insts_list = [
            (
                code.make(code.OpCode.PTrue),  # 0000
                code.make(code.OpCode.JumpNT, 7),  # 0001
                code.make(code.OpCode.PConstant, 0),  # 0004
                code.make(code.OpCode.Pop),  # 0007
                code.make(code.OpCode.PConstant, 1),  # 0008
                code.make(code.OpCode.Pop),  # 0011
            ),
            (
                code.make(code.OpCode.PTrue),
                code.make(code.OpCode.JumpNT, 10),
                code.make(code.OpCode.PConstant, 0),
                code.make(code.OpCode.Jump, 13),
                code.make(code.OpCode.PConstant, 1),
                code.make(code.OpCode.Pop),
                code.make(code.OpCode.PConstant, 2),
                code.make(code.OpCode.Pop),
            ),
        ]

        for test_code, expected_const, insts in zip(
            test_code_list, expected_const_list, insts_list
        ):
            self.verify_compiler(test_code, expected_const, insts)
