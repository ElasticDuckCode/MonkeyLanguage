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
    tok: token.Token = None
    value: str = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.value


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
class StringLiteral(Expression):
    tok: token.Token = None
    value: str = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass(eq=True, frozen=True)
class ArrayLiteral(Expression):
    tok: token.Token = None
    elements: List[Expression] = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return "[" + ", ".join([s.string for s in self.elements]) + "]"


@dataclass(eq=True, frozen=True)
class HashLiteral(Expression):
    tok: token.Token = None
    pairs: Dict[Expression, Expression] = None

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
    tok: token.Token = None
    value: bool = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        return self.tok.literal


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
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


@dataclass(eq=True, frozen=True)
class IndexExpression(Expression):
    tok: token.Token = None
    left: Expression = None
    index: Expression = None

    def expression_node(self) -> None: return

    @property
    def token_literal(self) -> str:
        return self.tok.literal

    @property
    def string(self) -> str:
        s = "(" + self.left.string + "[" + self.index.string + "]" + ")"
        return s
