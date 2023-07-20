from dataclasses import dataclass
from pprint import pformat

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
        self.op_dict: dict[str, code.OpCode] = {
            "+": code.OpCode.Add,
            "-": code.OpCode.Sub,
            "*": code.OpCode.Mul,
            "/": code.OpCode.Div,
            "==": code.OpCode.Equal,
            "!=": code.OpCode.NotEqual,
            ">": code.OpCode.GreaterThan,
            "<": code.OpCode.GreaterThan,
        }

    def compile(self, node: ast.Node) -> None:
        match node:
            case ast.Program():
                for stmt in node.statements:
                    self.compile(stmt)
            case ast.ExpressionStatement():
                self.compile(node.expression)
                self.emit(code.OpCode.Pop)
            case ast.PrefixExpression(operator="-"):
                self.compile(node.right)
                self.emit(code.OpCode.Minus)
            case ast.PrefixExpression(operator="!"):
                self.compile(node.right)
                self.emit(code.OpCode.Bang)
            case ast.InfixExpression(operator=op):
                match op:
                    case "<":
                        self.compile(node.right)
                        self.compile(node.left)
                    case _:
                        self.compile(node.left)
                        self.compile(node.right)
                self.emit(self.op_dict[op])
            case ast.IntegerLiteral():
                integer = obj.Integer(node.value)
                ident = self.add_constant(integer)
                self.emit(code.OpCode.PConstant, ident)
            case ast.Boolean(value=True):
                self.emit(code.OpCode.PTrue)
            case ast.Boolean(value=False):
                self.emit(code.OpCode.PFalse)
            case ast.BlockStatement():
                for s in node.statements:
                    self.compile(s)
            case ast.IfExpression():
                if node.condition and node.consequence:
                    self.compile(node.condition)
                    self.emit(code.OpCode.JumpNT, 9999)
                    self.compile(node.consequence)
                else:
                    raise RuntimeError(
                        f"failed to compile node:\n{pformat(node)}. Conditional missing condition or consequence."
                    )
            case _:
                raise RuntimeError(f"failed to compile node:\n{pformat(node)}")
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
