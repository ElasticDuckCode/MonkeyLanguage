from typing import Any, cast
from unittest import TestCase

from src.monkey import ast, compiler, lexer, obj, parser, vm


def parse(src_code: str) -> ast.Program:
    lex = lexer.Lexer(src_code)
    par = parser.Parser(lex)
    return par.parse_program()


class TestVirtualMachine(TestCase):
    def verify_vm_case(self, src_code: str, expected: Any):
        program = parse(src_code)
        comp = compiler.Compiler()
        comp.compile(program)
        virt = vm.VirtualMachine(comp.bytecode)
        virt.run()
        self.assertIsNotNone(virt.last_popped)
        self.verify_expected_object(expected, virt.last_popped)

    def verify_expected_object(self, expected: Any, actual: obj.Object | None):
        match expected:
            case bool():
                self.assertIsInstance(actual, obj.Boolean)
                actual = cast(obj.Boolean, actual)
                self.assertEqual(expected, actual.value)
            case int():
                self.assertIsInstance(actual, obj.Integer)
                actual = cast(obj.Integer, actual)
                self.assertEqual(expected, actual.value)
            case _:
                self.assertEqual(True, False)

    def test_vm_integer_arithmetic(self):
        tests = (
            ("1", 1),
            ("2", 2),
            ("245", 245),
            ("1 + 2", 3),
            ("1 - 2", -1),
            ("1 * 2", 2),
            ("4 / 2", 2),
            ("50 / 2 * 2 + 10 - 5", 55),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("5 * (2 + 10)", 60),
            ("-1", -1),
            ("--1", 1),
            ("---1", -1),
            ("50 + -50", 0),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)

    def test_vm_boolean_expressions(self):
        tests = (
            ("true", True),
            ("false", False),
            ("1 < 2", True),
            ("1 > 2", False),
            ("1 < 1", False),
            ("1 > 1", False),
            ("1 == 1", True),
            ("1 != 1", False),
            ("1 == 2", False),
            ("1 != 2", True),
            ("true == true", True),
            ("true != true", False),
            ("true == false", False),
            ("true != false", True),
            ("false == false", True),
            ("(1 < 2) == true", True),
            ("(1 < 2) == false", False),
            ("(1 > 2) == true", False),
            ("(1 > 2) == false", True),
            ("!true", False),
            ("!!true", True),
            ("!false", True),
            ("!1", False),
            ("!(true == true)", False),
            ("!!(true == true)", True),
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)
