from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final, List

from ..ast import ast


class ObjectType(str):
    pass


INTEGER_OBJ:      Final[ObjectType] = "INTEGER"
BOOLEAN_OBJ:      Final[ObjectType] = "BOOLEAN"
NULL_OBJ:         Final[ObjectType] = "NULL"
RETURN_VALUE_OBJ: Final[ObjectType] = "RETURN_VALUE"
ERROR_OBJ:        Final[ObjectType] = "ERROR"
FUNCTION_OBJ:     Final[ObjectType] = "FUNCTION"


class Object(ABC):

    @property
    @abstractmethod
    def otype(self) -> ObjectType: pass

    @property
    @abstractmethod
    def inspect(self) -> str: pass


@dataclass
class Integer(Object):
    value: int = None

    @property
    def otype(self) -> ObjectType: return INTEGER_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool = None

    @property
    def otype(self) -> ObjectType: return BOOLEAN_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value).lower()  # True -> true


TRUE:  Final[Boolean] = Boolean(True)
FALSE: Final[Boolean] = Boolean(False)


@dataclass
class Null(Object):

    @property
    def otype(self) -> ObjectType: return NULL_OBJ

    @property
    def inspect(self) -> str:
        return "null"


NULL: Final[Null] = Null()


@dataclass
class ReturnValue(Object):
    value: Object = None

    @property
    def otype(self) -> ObjectType: return RETURN_VALUE_OBJ

    @property
    def inspect(self) -> str:
        return self.value.inspect


@dataclass
class Error(Object):
    message: str = None

    @property
    def otype(self) -> ObjectType: return ERROR_OBJ

    @property
    def inspect(self) -> str:
        return "ERROR: " + self.message


@dataclass
class Function(Object):
    from . import env
    parameters: List[ast.Identifier] = None
    body: ast.BlockStatement = None
    environment: env.Environment = None

    @property
    def otype(self) -> ObjectType: return FUNCTION_OBJ

    @property
    def inspect(self) -> str:
        string = "fn("
        string += ",".join([p.string for p in self.parameters]) + "\n"
        string += self.body.string + "\n"
        return self.string
