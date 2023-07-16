from dataclasses import dataclass
from ..ast import ast
from ..obj import obj


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
            case ast.Program:
                print(node.statements)
        return None

    @property
    def bytecode(self) -> Bytecode:
        return Bytecode(self.instructions, self.constants)
