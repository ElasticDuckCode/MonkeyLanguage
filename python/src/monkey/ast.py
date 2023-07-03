from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

import src.monkey.token as token


class Node(ABC):
    @property
    @abstractmethod
    def token_literal() -> str: pass


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
    statements: List[Statement] = None

    @property
    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal
        else:
            return ""


@dataclass
class Identifier(Expression):
    tok: token.Token
    value: str

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal


@dataclass
class LetStatement(Statement):
    tok: token.Token
    name: Identifier
    value: Expression

    def statement_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal
