from dataclasses import dataclass
from ..ast import ast
from ..obj import obj
from ..code import code


@dataclass
class Bytecode:
    instructions: list[bytes]
    constants: list[obj.Object]


class Compiler:
    def __init__(self) -> None:
        self.instructions: list[bytes] = []
        self.constants: list[obj.Object] = []

    def compile(self, node: ast.Node) -> None:
        match node:
            case ast.Program():
                for stmt in node.statements:
                    self.compile(stmt)
            case ast.ExpressionStatement():
                self.compile(node.expression)
            case ast.InfixExpression():
                self.compile(node.left)
                self.compile(node.right)
            case ast.IntegerLiteral():
                integer = obj.Integer(node.value)
                ident = self.add_constant(integer)
                self.emit(code.OpCode.Constant, ident)
        return None

    def add_constant(self, c: obj.Object) -> int:
        self.constants.append(c)
        return len(self.constants) - 1

    def add_instruction(self, ins: bytes) -> int:
        pos = len(ins)
        self.instructions.append(ins)
        return pos

    def emit(self, op: code.OpCode, *operands: int) -> int:
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)
        return pos

    @property
    def bytecode(self) -> Bytecode:
        return Bytecode(self.instructions, self.constants)
