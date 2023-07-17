from typing import Final

from ..obj import obj
from ..code import code
from ..compiler import compiler


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

    def run(self) -> None:
        ip = 0
        while ip < len(self.instructions):
            op = code.OpCode(self.instructions[ip])
            print(op)
            ip += 1
