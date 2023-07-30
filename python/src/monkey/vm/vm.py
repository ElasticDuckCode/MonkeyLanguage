from typing import Final, cast

from ..code import code
from ..compiler import compiler
from ..obj import obj, builtin
from . import frame

STACK_SIZE: Final[int] = 2048
GLOBAL_SIZE: Final[int] = 2**16
MAX_FRAMES: Final[int] = 2**10


def build_new_globals() -> list[obj.Object]:
    return [obj.NULL] * GLOBAL_SIZE


def build_new_stack() -> list[obj.Object]:
    return [obj.NULL] * STACK_SIZE


def build_new_frames() -> list[frame.Frame]:
    return [
        frame.Frame(obj.Closure(obj.CompiledFunction(bytearray(0), 0, 0), []))
    ] * MAX_FRAMES


def new_error(msg: str) -> obj.Error:
    return obj.Error(msg)


class VirtualMachine:
    def __init__(
        self,
        bytecode: compiler.Bytecode,
        globals: list[obj.Object] = build_new_globals(),
    ) -> None:
        self.stack: list[obj.Object] = build_new_stack()
        self.sp: int = 0

        self.frames: list[frame.Frame] = build_new_frames()
        main_fn = obj.CompiledFunction(bytecode.instructions, 0, 0)
        main_closure = obj.Closure(main_fn, [])
        main_frame = frame.Frame(main_closure)
        self.frames[0] = main_frame
        self.fp: int = 1

        self.constants: list[obj.Object] = bytecode.constants
        self.globals: list[obj.Object] = globals
        self._errors: list[obj.Error] = []

    @property
    def errors(self):
        return self._errors

    @property
    def curr_frame(self) -> frame.Frame:
        return self.frames[self.fp - 1]

    def push_frame(self, f: frame.Frame) -> None:
        if self.fp > MAX_FRAMES:
            raise OverflowError("Frame stack overflow.")
        self.frames[self.fp] = f
        self.fp += 1

    def pop_frame(self) -> frame.Frame:
        f = self.frames[self.fp - 1]
        self.fp -= 1
        return f

    @property
    def instructions(self):
        return self.curr_frame.instructions

    @property
    def ip(self):
        return self.curr_frame.ip

    @ip.setter
    def ip(self, i: int):
        self.frames[self.fp - 1].ip = i

    @property
    def bp(self):
        return self.curr_frame.bp

    @bp.setter
    def bp(self, b: int):
        self.frames[self.fp - 1].bp = b

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

    def push_closure(self, idx: int, n_free: int) -> None:
        constant = self.constants[idx]
        fn = cast(obj.CompiledFunction, constant)
        free: list[obj.Object] = self.stack[self.sp - n_free : self.sp]
        self.sp -= n_free
        cl = obj.Closure(fn, free)
        self.push(cl)

    def pop(self) -> obj.Object:
        if self.sp - 1 < 0:
            return obj.NULL
        o = self.stack[self.sp - 1]
        self.sp -= 1
        return o

    def pop_array(self, n_elems: int) -> list[obj.Object]:
        array = self.stack[self.sp - n_elems : self.sp].copy()
        self.sp -= n_elems
        return array

    def pop_hash(self, n_keyval: int) -> dict[obj.Object, obj.Object]:
        keyvals = self.stack[self.sp - n_keyval : self.sp].copy()
        self.sp -= n_keyval
        hash = dict(map(lambda k, v: (k, v), keyvals[::2], keyvals[1::2]))
        return hash

    def call_closure(self, cl: obj.Closure, n_args: int):
        if n_args != cl.fn.n_params:
            self._errors.append(new_error("incorrect number of args"))
        f = frame.Frame(cl, bp=self.sp - n_args)
        self.push_frame(f)
        self.sp = f.bp + cl.fn.n_locals

    def call_builtin(self, fn: obj.BuiltIn, n_args: int):
        args = self.stack[self.sp - n_args : self.sp]
        result = fn.fn(*args)
        self.sp = self.sp - n_args - 1
        if result is None:
            self.push(obj.NULL)
        else:
            self.push(result)

    def execute_call(self, n_args: int):
        callee = self.stack[self.sp - 1 - n_args]
        match callee:
            case obj.Closure():
                self.call_closure(callee, n_args)
            case obj.BuiltIn():
                self.call_builtin(callee, n_args)

    def run(self) -> None:
        while self.ip < len(self.instructions):
            if len(self._errors) > 0:
                break
            op = code.OpCode(self.instructions[self.ip].to_bytes(1, "big"))
            self.ip += 1
            match op:
                case code.OpCode.PConstant:
                    const_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    self.push(self.constants[const_idx])
                case code.OpCode.Add:
                    right = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Integer) and isinstance(right, obj.Integer):
                        int_result = left.value + right.value
                        self.push(obj.Integer(int_result))
                    elif isinstance(left, obj.String) and isinstance(right, obj.String):
                        str_result: str = left.value + right.value
                        self.push(obj.String(str_result))
                    else:
                        self.push(obj.NULL)
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
                    const_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip = const_idx
                case code.OpCode.JumpNT:
                    const_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    condition = self.pop()
                    if condition in [obj.FALSE, obj.NULL]:
                        self.ip = const_idx
                case code.OpCode.PNull:
                    self.push(obj.NULL)
                case code.OpCode.SetGlobal:
                    global_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    value = self.pop()
                    self.globals[global_idx] = value
                case code.OpCode.GetGlobal:
                    global_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    self.push(self.globals[global_idx])
                case code.OpCode.PArray:
                    n_elems = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    array = self.pop_array(n_elems)
                    self.push(obj.Array(array))
                case code.OpCode.PHash:
                    n_keyval = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    hash = self.pop_hash(n_keyval)
                    self.push(obj.Hash(hash))
                case code.OpCode.Index:
                    index = self.pop()
                    left = self.pop()
                    if isinstance(left, obj.Array) and isinstance(index, obj.Integer):
                        idx = index.value
                        arr = left.elements
                        if (idx < -len(arr)) or (idx >= len(arr)):
                            self.push(obj.NULL)
                        else:
                            self.push(arr[idx % len(arr)])
                    elif isinstance(left, obj.Hash):
                        key = index
                        hash = left.pairs
                        if key not in hash.keys():
                            self.push(obj.NULL)
                        else:
                            self.push(hash[key])
                    else:
                        self.push(obj.NULL)
                case code.OpCode.Call:
                    n_args = int.from_bytes(
                        self.instructions[self.ip : self.ip + 1], "big"
                    )
                    self.ip += 1
                    self.execute_call(n_args)
                case code.OpCode.ReturnValue:
                    value = self.pop()
                    f = self.pop_frame()
                    self.sp = f.bp - 1
                    self.push(value)
                case code.OpCode.Return:
                    f = self.pop_frame()
                    self.sp = f.bp - 1
                    self.push(obj.NULL)
                case code.OpCode.SetLocal:
                    local_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 1], "big"
                    )
                    self.ip += 1
                    value = self.pop()
                    self.stack[self.bp + local_idx] = value
                case code.OpCode.GetLocal:
                    local_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 1], "big"
                    )
                    self.ip += 1
                    value = self.stack[self.bp + local_idx]
                    self.push(value)
                case code.OpCode.GetBuiltIn:
                    builtin_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 1], "big"
                    )
                    self.ip += 1
                    definition = builtin.BuiltIns[builtin_idx]
                    self.push(definition.fn)
                case code.OpCode.Closure:
                    const_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 2], "big"
                    )
                    self.ip += 2
                    n_free = int.from_bytes(
                        self.instructions[self.ip : self.ip + 1], "big"
                    )
                    self.ip += 1
                    self.push_closure(const_idx, n_free)
                case code.OpCode.GetFree:
                    free_idx = int.from_bytes(
                        self.instructions[self.ip : self.ip + 1], "big"
                    )
                    self.ip += 1
                    curr_closure = self.curr_frame.cl
                    self.push(curr_closure.free[free_idx])
                case _:
                    self._errors.append(new_error(f"unknown opcode: {op}"))

    @property
    def error_str(self):
        return "\n".join([e.message for e in self._errors])
