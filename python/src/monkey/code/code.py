from typing import NewType, Final
from dataclasses import dataclass

Instructions = NewType("Instructions", list[bytes])
OpCode = NewType("Opcode", bytes)


OpConstant: Final[OpCode] = OpCode(b'\x01')


@dataclass
class Definition:
    name: str
    operand_widths: list[int]


OpDefs: dict[OpCode, Definition] = {
    OpConstant: Definition("OpConstant", [2])
}


def make(op: OpCode, operands: list[int]) -> bytes:
    instruction = bytearray(op)
    # The python to_bytes method on `int` objects automatically
    # enforces bytes, and has big-endianess.
    for operand, n_bytes in zip(operands, OpDefs[op].operand_widths):
        instruction += operand.to_bytes(n_bytes, "big")
    return instruction
