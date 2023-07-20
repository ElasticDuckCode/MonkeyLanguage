from dataclasses import dataclass
from enum import Enum


class OpCode(Enum):
    PConstant = b"\x01"
    PTrue = b"\x02"
    PFalse = b"\x03"
    Pop = b"\x04"
    Add = b"\x05"
    Sub = b"\x06"
    Mul = b"\x07"
    Div = b"\x08"
    Equal = b"\x09"
    NotEqual = b"\x0a"
    GreaterThan = b"\x0b"
    Minus = b"\x0c"
    Bang = b"\x0d"
    Jump = b"\x0e"
    JumpNT = b"\x0f"


@dataclass
class Definition:
    name: str
    operand_widths: list[int]


OpDefs: dict[OpCode, Definition] = {
    OpCode.PConstant: Definition(OpCode.PConstant.name, [2]),
    OpCode.PTrue: Definition(OpCode.PTrue.name, []),
    OpCode.PFalse: Definition(OpCode.PFalse.name, []),
    OpCode.Pop: Definition(OpCode.Pop.name, []),
    OpCode.Add: Definition(OpCode.Add.name, []),
    OpCode.Sub: Definition(OpCode.Sub.name, []),
    OpCode.Mul: Definition(OpCode.Mul.name, []),
    OpCode.Div: Definition(OpCode.Div.name, []),
    OpCode.Equal: Definition(OpCode.Equal.name, []),
    OpCode.NotEqual: Definition(OpCode.NotEqual.name, []),
    OpCode.GreaterThan: Definition(OpCode.GreaterThan.name, []),
    OpCode.Minus: Definition(OpCode.Minus.name, []),
    OpCode.Bang: Definition(OpCode.Bang.name, []),
    OpCode.Jump: Definition(OpCode.Jump.name, [2]),
    OpCode.JumpNT: Definition(OpCode.JumpNT.name, [2]),
}


def instructions_to_string(insts: bytes) -> str:
    string = ""
    ip = 0
    while ip < len(insts):
        string += f"{ip:04x}"
        d = OpDefs[OpCode(insts[ip].to_bytes(1, "big"))]
        string += f" {d.name}"
        ip += 1

        for i, width in enumerate(d.operand_widths):
            v = int.from_bytes(insts[ip : ip + width], "big")
            string += f" {v}"
            ip += width
        string += "\n"

    return string[:-1]


def make(op: OpCode, *operands: int) -> bytes:
    instruction = bytearray(op.value)
    for operand, n_bytes in zip(operands, OpDefs[op].operand_widths):
        instruction += operand.to_bytes(n_bytes, "big")
    return instruction
