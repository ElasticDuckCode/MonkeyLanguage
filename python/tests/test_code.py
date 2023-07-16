from unittest import TestCase
from src.monkey import code


class TestOpCode(TestCase):
    def test_code_make(self):
        cases = (
            (
                code.OpCode.Constant,
                [65534],
                bytes(code.OpCode.Constant.value) + (255).to_bytes() + (254).to_bytes(),
            ),
        )
        for opcode, operands, expected in cases:
            instruction = code.make(opcode, *operands)
            self.assertEqual(instruction, expected)

    def test_code_repr(self):
        instructions = (
            code.make(code.OpCode.Constant, 1),
            code.make(code.OpCode.Constant, 2),
            code.make(code.OpCode.Constant, 65535),
        )
        expected = """0000 Constant 1
0003 Constant 2
0006 Constant 65535"""
        received = code.instructions_to_string(instructions)
        self.assertEqual(received, expected)
