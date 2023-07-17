from dataclasses import dataclass

from ..ast import ast
from ..code import code
from ..obj import obj


@dataclass
class Bytecode:
    instructions: bytearray
    constants: list[obj.Object]


class Compiler:
    def __init__(self) -> None:
        self.instructions: bytearray = bytearray(0)
        self.constants: list[obj.Object] = []

    def compile(self, node: ast.Node) -> None:
        match node:
            case ast.Program():
                for stmt in node.statements:
                    self.compile(stmt)
            case ast.ExpressionStatement():
                self.compile(node.expression)
            case ast.InfixExpression(operator="+"):
                self.compile(node.left)
                self.compile(node.right)
                self.emit(code.OpCode.Add)
            case ast.IntegerLiteral():
                integer = obj.Integer(node.value)
                ident = self.add_constant(integer)
                self.emit(code.OpCode.Constant, ident)
            case _:
                raise RuntimeError(f"failed to compiler node: {node}")
        return None

    def add_constant(self, c: obj.Object) -> int:
        self.constants.append(c)
        return len(self.constants) - 1

    def add_instruction(self, ins: bytes) -> int:
        pos = len(ins)
        self.instructions += ins
        return pos

    def emit(self, op: code.OpCode, *operands: int) -> int:
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)
        return pos

    @property
    def bytecode(self) -> Bytecode:
        return Bytecode(self.instructions, self.constants)
