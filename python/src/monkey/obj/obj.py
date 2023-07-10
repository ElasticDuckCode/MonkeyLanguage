from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final, NewType, List, Callable, Tuple

from ..ast import ast


ObjectType = NewType('ObjectType', str)


INTEGER_OBJ:      Final[ObjectType] = ObjectType("INTEGER")
BOOLEAN_OBJ:      Final[ObjectType] = ObjectType("BOOLEAN")
STRING_OBJ:       Final[ObjectType] = ObjectType("STRING")
NULL_OBJ:         Final[ObjectType] = ObjectType("NULL")
RETURN_VALUE_OBJ: Final[ObjectType] = ObjectType("RETURN_VALUE")
ERROR_OBJ:        Final[ObjectType] = ObjectType("ERROR")
FUNCTION_OBJ:     Final[ObjectType] = ObjectType("FUNCTION")
BUILTIN_OBJ:      Final[ObjectType] = ObjectType("BUILTIN")
ARRAY_OBJ:        Final[ObjectType] = ObjectType("ARRAY")


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
class String(Object):
    value: str = None

    @property
    def otype(self) -> ObjectType: return STRING_OBJ

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


@ dataclass
class BuiltIn(Object):

    fn: Callable[[Tuple[Object, ...]], Object] = None

    @ property
    def otype(self) -> ObjectType: return BUILTIN_OBJ

    @ property
    def inspect(self) -> str:
        return "builtin function"


@ dataclass
class Array(Object):
    elements: List[Object] = None

    @ property
    def otype(self) -> ObjectType: return ARRAY_OBJ

    @ property
    def inspect(self) -> str:
        return "[" + ", ".join([e.inspect for e in self.elements]) + "]"
