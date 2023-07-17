from dataclasses import dataclass
from enum import Enum


class OpCode(Enum):
    Constant = b"\x01"


@dataclass
class Definition:
    name: str
    operand_widths: list[int]


OpDefs: dict[OpCode, Definition] = {OpCode.Constant: Definition("Constant", [2])}


def instructions_to_string(insts: bytes) -> str:
    string = ""
    ip = 0
    while ip < len(insts):
        string += f"{ip:04x} "
        d = OpDefs[OpCode(insts[ip].to_bytes(1, "big"))]
        string += f"{d.name} "
        ip += 1

        for i, width in enumerate(d.operand_widths):
            v = int.from_bytes(insts[ip : ip + width], "big")
            string += f"{v}"
            ip += width
            if i < len(d.operand_widths) - 1:
                string += " "
            else:
                string += "\n"

    return string[:-1]


def make(op: OpCode, *operands: int) -> bytes:
    instruction = bytearray(op.value)
    for operand, n_bytes in zip(operands, OpDefs[op].operand_widths):
        instruction += operand.to_bytes(n_bytes, "big")
    return instruction
