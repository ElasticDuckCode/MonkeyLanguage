from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import src.monkey.token as token


class Node(ABC):
    @property
    @abstractmethod
    def token_literal(self) -> str: pass
    @property
    @abstractmethod
    def string(self) -> str: pass


@dataclass
class Statement(Node):
    @abstractmethod
    def statement_node(self) -> None: pass


@dataclass
class Expression(Node):
    @abstractmethod
    def expression_node(self) -> None: pass


@dataclass
class Program(Node):
    """Serves as the root node of the AST
    """
    statements: List = field(default_factory=list)

    @property
    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal
        else:
            return ""

    @property
    def string(self) -> str:
        out = ""
        for stmt in self.statements:
            out += stmt.string
        return out


@dataclass
class Identifier(Expression):
    tok: token.Token = None
    value: str = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.value


@dataclass
class LetStatement(Statement):
    tok: token.Token = None
    name: Identifier = None
    value: Expression = None

    def statement_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        out = ""
        out += self.token_literal + " "
        out += self.name.string + " "
        out += "= "
        if self.value is not None:
            out += self.value.string
        out += ";"
        return out


@dataclass
class ReturnStatement(Statement):
    tok: token.Token = None
    value: Expression = None

    def statement_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        out = ""
        out += self.token_literal + " "
        if self.value is not None:
            out += self.value.string
        out += ";"
        return out


@dataclass
class ExpressionStatement(Statement):
    tok: token.Token = None
    expression: Expression = None

    def statement_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        out = ""
        if self.expression is not None:
            out += self.expression.string
        return out
