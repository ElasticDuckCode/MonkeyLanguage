from unittest import TestCase, main
from src.monkey import code


class TestOpCode(TestCase):
    def test_code_make(self):
        cases = (
            (
                code.OpConstant,
                [65534],
                bytes(code.OpConstant) + (255).to_bytes() + (254).to_bytes()
            ),
        )
        for opcode, operands, expected in cases:
            instruction = code.make(opcode, operands)
            self.assertEqual(instruction, expected)


if __name__ == "__main__":
    main()
