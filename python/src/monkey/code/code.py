from dataclasses import dataclass
from enum import Enum


class OpCode(Enum):
    Constant = b"\x01"


@dataclass
class Definition:
    name: str
    operand_widths: list[int]


OpDefs: dict[OpCode, Definition] = {OpCode.Constant: Definition("Constant", [2])}


def instructions_to_string(insts: list[bytes]) -> str:
    string = ""
    offset = 0
    for inst in insts:
        string += f"{offset:04x} "
        d = OpDefs[OpCode(inst[0].to_bytes())]
        string += f"{d.name} "

        remain = inst[1:]
        for width in d.operand_widths:
            v = int.from_bytes(remain[:width])
            string += f"{v}"
            remain = remain[width:]
            if len(remain) > 0:
                string += " "
            else:
                string += "\n"
        offset += len(inst)

    return string[:-1]


def make(op: OpCode, operands: list[int]) -> bytes:
    instruction = bytearray(op.value)
    for operand, n_bytes in zip(operands, OpDefs[op].operand_widths):
        instruction += operand.to_bytes(n_bytes, "big")
    return instruction
