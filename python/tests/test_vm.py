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
        self.assertIsNotNone(virt.stack_top)
        self.verify_expected_object(expected, virt.stack_top)

    def verify_expected_object(self, expected: Any, actual: obj.Object | None):
        match expected:
            case int():
                self.assertIsInstance(actual, obj.Integer)
                actual = cast(obj.Integer, actual)
                self.assertEqual(expected, actual.value)
            case _:
                self.assertEqual(True, False)

    def test_vm_integer_arithmetic(self):
        # Note: Expected result is no the evaluation of the expression,
        #       but value on top of the vm stack.
        tests = (
            ("1", 1),
            ("2", 2),
            ("245", 245),
            ("1 + 2", 2),  # FIXME
        )
        for src_code, expected in tests:
            self.verify_vm_case(src_code, expected)
