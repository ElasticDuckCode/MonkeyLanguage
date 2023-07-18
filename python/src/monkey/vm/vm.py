from typing import Final, cast

from ..code import code
from ..compiler import compiler
from ..obj import obj

STACK_SIZE: Final[int] = 2048


class VirtualMachine:
    def __init__(self, bytecode: compiler.Bytecode) -> None:
        self.instructions: bytes = bytecode.instructions
        self.constants: list[obj.Object] = bytecode.constants
        self.stack: list[obj.Object | None] = [None] * STACK_SIZE
        self.sp: int = 0

    @property
    def stack_top(self) -> obj.Object | None:
        if self.sp <= 0:
            return None
        else:
            return self.stack[self.sp - 1]

    @property
    def last_popped(self) -> obj.Object | None:
        return self.stack[self.sp]

    def push(self, o: obj.Object) -> None:
        if self.sp > STACK_SIZE:
            raise OverflowError("Stack overflow.")
        self.stack[self.sp] = o
        self.sp += 1

    def pop(self) -> obj.Object | None:
        if self.sp - 1 < 0:
            return None
        o = self.stack[self.sp - 1]
        self.sp -= 1
        return o

    def run(self) -> None:
        ip = 0
        while ip < len(self.instructions):
            op = code.OpCode(self.instructions[ip].to_bytes(1, "big"))
            ip += 1
            match op:
                case code.OpCode.PConstant:
                    const_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip += 2
                    self.push(self.constants[const_idx])
                case code.OpCode.Add:
                    right = cast(obj.Integer, self.pop())
                    left = cast(obj.Integer, self.pop())
                    result = left.value + right.value
                    self.push(obj.Integer(result))
                case code.OpCode.Sub:
                    right = cast(obj.Integer, self.pop())
                    left = cast(obj.Integer, self.pop())
                    result = left.value - right.value
                    self.push(obj.Integer(result))
                case code.OpCode.Mul:
                    right = cast(obj.Integer, self.pop())
                    left = cast(obj.Integer, self.pop())
                    result = left.value * right.value
                    self.push(obj.Integer(result))
                case code.OpCode.Div:
                    right = cast(obj.Integer, self.pop())
                    left = cast(obj.Integer, self.pop())
                    result = left.value // right.value
                    self.push(obj.Integer(result))
                case code.OpCode.PTrue:
                    self.push(obj.TRUE)
                case code.OpCode.PFalse:
                    self.push(obj.FALSE)
                case code.OpCode.Pop:
                    self.pop()
                case _:
                    raise NotImplementedError("OpCode not yet supported")
