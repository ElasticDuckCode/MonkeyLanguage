from unittest import TestCase

from src.monkey import code


class TestOpCode(TestCase):
    def test_code_make(self):
        cases = (
            (
                code.OpCode.PConstant,
                [65534],
                bytes(code.OpCode.PConstant.value)
                + (255).to_bytes(1, "big")
                + (254).to_bytes(1, "big"),
            ),
            (code.OpCode.Add, [], bytes(code.OpCode.Add.value)),
        )
        for opcode, operands, expected in cases:
            instruction = code.make(opcode, *operands)
            self.assertEqual(instruction, expected)

    def test_code_repr(self):
        instructions = (
            code.make(code.OpCode.PConstant, 1)
            + code.make(code.OpCode.PConstant, 2)
            + code.make(code.OpCode.PConstant, 65535)
            + code.make(code.OpCode.Add)
        )
        expected = """0000 PConstant 1
0003 PConstant 2
0006 PConstant 65535
0009 Add"""
        received = code.instructions_to_string(instructions)
        self.assertEqual(received, expected)
