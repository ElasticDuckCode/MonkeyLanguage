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


@dataclass
class IntegerLiteral(Expression):
    tok: token.Token = None
    value: int = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass
class Boolean(Expression):
    tok: token.Token = None
    value: bool = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass
class PrefixExpression(Expression):
    tok: token.Token = None
    operator: str = None
    right: Expression = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "(" + self.operator + self.right.string + ")"


@dataclass
class InfixExpression(Expression):
    tok: token.Token = None
    left: Expression = None
    operator: str = None
    right: Expression = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "(" + self.left.string + " " + self.operator + " " + self.right.string + ")"


@dataclass
class BlockStatement(Statement):
    tok: token.Token = None
    statements: List[Statement] = None

    def statement_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "".join([s.string for s in self.statements])


@dataclass
class IfExpression(Expression):
    tok: token.Token = None
    condition: Expression = None
    consequence: BlockStatement = None
    alternative: BlockStatement = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        string = "if"
        string += self.condition.string + " " + self.Consequence.string
        if self.Alternative is not None:
            string += "else " + self.Alternative.string
        return string


@dataclass
class FunctionLiteral(Expression):
    tok: token.Token = None
    parameters: List[Identifier] = None
    body: BlockStatement = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        string = self.tok.token_literal
        string += "(" + ", ".join([p.string for p in self.parameters]) + ")"
        string += self.body.string
        return string


@dataclass
class CallExpression(Expression):
    tok: token.Token = None
    function: Expression = None
    arguements: List[Expression] = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        string = self.function.string
        string += "(" + ", ".join([a.string for a in self.arguements]) + ")"
        return string
