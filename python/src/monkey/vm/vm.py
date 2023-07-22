from typing import Final

from ..code import code
from ..compiler import compiler
from ..obj import obj

STACK_SIZE: Final[int] = 2048
GLOBAL_SIZE: Final[int] = 2**16


def build_new_globals() -> list[obj.Object]:
    return [obj.NULL] * GLOBAL_SIZE


def build_new_stack() -> list[obj.Object]:
    return [obj.NULL] * STACK_SIZE


class VirtualMachine:
    def __init__(
        self,
        bytecode: compiler.Bytecode,
        globals: list[obj.Object] = build_new_globals(),
    ) -> None:
        self.sp: int = 0
        self.instructions: bytes = bytecode.instructions
        self.constants: list[obj.Object] = bytecode.constants
        self.globals: list[obj.Object] = globals
        self.stack: list[obj.Object] = build_new_stack()

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

    def pop(self) -> obj.Object:
        if self.sp - 1 < 0:
            return obj.NULL
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
                    right = self.pop()
                    left = self.pop()
                    if hasattr(left, "value") and hasattr(right, "value"):
                        result = left.value + right.value
                    else:
                        result = obj.NULL
                    self.push(obj.Integer(result))
                case code.OpCode.Sub:
                    right = self.pop()
                    left = self.pop()
                    if hasattr(left, "value") and hasattr(right, "value"):
                        result = left.value - right.value
                    else:
                        result = obj.NULL
                    self.push(obj.Integer(result))
                case code.OpCode.Mul:
                    right = self.pop()
                    left = self.pop()
                    if hasattr(left, "value") and hasattr(right, "value"):
                        result = left.value * right.value
                    else:
                        result = obj.NULL
                    self.push(obj.Integer(result))
                case code.OpCode.Div:
                    right = self.pop()
                    left = self.pop()
                    if hasattr(left, "value") and hasattr(right, "value"):
                        result = left.value // right.value
                    else:
                        result = obj.NULL
                    self.push(obj.Integer(result))
                case code.OpCode.PTrue:
                    self.push(obj.TRUE)
                case code.OpCode.PFalse:
                    self.push(obj.FALSE)
                case code.OpCode.Pop:
                    self.pop()
                case code.OpCode.Equal:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Integer) and isinstance(right, obj.Integer):
                        result = obj.TRUE if left.value == right.value else obj.FALSE
                    else:
                        result = obj.TRUE if left == right else obj.FALSE
                    self.push(result)
                case code.OpCode.NotEqual:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Integer) and isinstance(right, obj.Integer):
                        result = obj.TRUE if left.value != right.value else obj.FALSE
                    else:
                        result = obj.TRUE if left != right else obj.FALSE
                    self.push(result)
                case code.OpCode.GreaterThan:
                    right = self.pop()
                    left = self.pop()
                    if hasattr(left, "value") and hasattr(right, "value"):
                        result = obj.TRUE if left.value > right.value else obj.FALSE
                    else:
                        result = obj.NULL
                    self.push(result)
                case code.OpCode.Minus:
                    value = self.pop()
                    if hasattr(value, "value"):
                        result = -value.value
                    else:
                        result = obj.NULL
                    self.push(obj.Integer(result))
                case code.OpCode.Bang:
                    value = self.pop()
                    if hasattr(value, "value"):
                        result = obj.TRUE if not value.value else obj.FALSE
                    elif value is obj.NULL:
                        result = obj.TRUE
                    else:
                        result = obj.NULL
                    self.push(result)
                case code.OpCode.Jump:
                    const_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip = const_idx
                case code.OpCode.JumpNT:
                    const_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip += 2
                    condition = self.pop()
                    if condition in [obj.FALSE, obj.NULL]:
                        ip = const_idx
                case code.OpCode.PNull:
                    self.push(obj.NULL)
                case code.OpCode.SetGlobal:
                    global_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip += 2
                    value = self.pop()
                    self.globals[global_idx] = value
                case code.OpCode.GetGlobal:
                    global_idx = int.from_bytes(self.instructions[ip : ip + 2], "big")
                    ip += 2
                    self.push(self.globals[global_idx])
                case _:
                    raise NotImplementedError("OpCode not yet supported")
