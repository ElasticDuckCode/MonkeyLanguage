from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict

from ..token import token


@dataclass(eq=True, frozen=True)
class Node(ABC):
    @property
    @abstractmethod
    def token_literal(self) -> str: pass
    @property
    @abstractmethod
    def string(self) -> str: pass


@dataclass(eq=True, frozen=True)
class Statement(Node):
    @abstractmethod
    def statement_node(self) -> None: pass


@dataclass(eq=True, frozen=True)
class Expression(Node):
    @abstractmethod
    def expression_node(self) -> None: pass


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
class Identifier(Expression):
    tok: token.Token
    value: str

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.value


@dataclass(eq=True, frozen=True)
class LetStatement(Statement):
    tok: token.Token
    name: Identifier
    value: Expression

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


@dataclass(eq=True, frozen=True)
class ReturnStatement(Statement):
    tok: token.Token
    value: Expression

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


@dataclass(eq=True, frozen=True)
class ExpressionStatement(Statement):
    tok: token.Token
    expression: Expression

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


@dataclass(eq=True, frozen=True)
class IntegerLiteral(Expression):
    tok: token.Token
    value: int

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass(eq=True, frozen=True)
class StringLiteral(Expression):
    tok: token.Token
    value: str

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass(eq=True, frozen=True)
class ArrayLiteral(Expression):
    tok: token.Token
    elements: List[Expression]

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "[" + ", ".join([s.string for s in self.elements]) + "]"


@dataclass(eq=True, frozen=True)
class HashLiteral(Expression):
    tok: token.Token
    pairs: Dict[Expression, Expression]

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        pair_strs = []
        for pair in self.pairs.items():
            pair_strs.append(pair[0].string + ": " + pair[1].string)
        return "{" + ", ".join(pair_strs) + "}"


@dataclass(eq=True, frozen=True)
class Boolean(Expression):
    tok: token.Token
    value: bool

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass(eq=True, frozen=True)
class PrefixExpression(Expression):
    tok: token.Token
    operator: str
    right: Expression

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "(" + self.operator + self.right.string + ")"


@dataclass(eq=True, frozen=True)
class InfixExpression(Expression):
    tok: token.Token
    left: Expression
    operator: str
    right: Expression

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "(" + self.left.string + " " + self.operator + " " + self.right.string + ")"


@dataclass(eq=True, frozen=True)
class BlockStatement(Statement):
    tok: token.Token
    statements: List[Statement]

    def statement_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "".join([s.string for s in self.statements])


@dataclass(eq=True, frozen=True)
class IfExpression(Expression):
    tok: token.Token
    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        string = "if"
        string += self.condition.string + " " + self.consequence.string
        if self.alternative is not None:
            string += "else " + self.alternative.string
        return string


@dataclass(eq=True, frozen=True)
class FunctionLiteral(Expression):
    tok: token.Token
    parameters: List[Identifier]
    body: BlockStatement

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        string = self.tok.literal
        string += "(" + ", ".join([p.string for p in self.parameters]) + ")"
        string += self.body.string
        return string


@dataclass(eq=True, frozen=True)
class CallExpression(Expression):
    tok: token.Token
    function: Expression
    arguements: List[Expression]

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        string = self.function.string
        string += "(" + ", ".join([a.string for a in self.arguements]) + ")"
        return string


@dataclass(eq=True, frozen=True)
class IndexExpression(Expression):
    tok: token.Token
    left: Expression
    index: Expression

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        s = "(" + self.left.string + "[" + self.index.string + "]" + ")"
        return s
