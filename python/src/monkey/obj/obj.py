from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Final, List, NewType

from ..ast import ast
from ..code import code

ObjectType = NewType("ObjectType", str)


INTEGER_OBJ: Final[ObjectType] = ObjectType("INTEGER")
BOOLEAN_OBJ: Final[ObjectType] = ObjectType("BOOLEAN")
STRING_OBJ: Final[ObjectType] = ObjectType("STRING")
NULL_OBJ: Final[ObjectType] = ObjectType("NULL")
RETURN_VALUE_OBJ: Final[ObjectType] = ObjectType("RETURN_VALUE")
ERROR_OBJ: Final[ObjectType] = ObjectType("ERROR")
FUNCTION_OBJ: Final[ObjectType] = ObjectType("FUNCTION")
BUILTIN_OBJ: Final[ObjectType] = ObjectType("BUILTIN")
ARRAY_OBJ: Final[ObjectType] = ObjectType("ARRAY")
HASH_OBJ: Final[ObjectType] = ObjectType("HASH")
COMPILED_FUNCTION_OBJ: Final[ObjectType] = ObjectType("COMPILED_FUNCTION")
CLOSURE_OBJ: Final[ObjectType] = ObjectType("CLOSURE")


@dataclass(eq=True, frozen=True)
class Object(ABC):
    @property
    @abstractmethod
    def otype(self) -> ObjectType:
        pass

    @property
    @abstractmethod
    def inspect(self) -> str:
        pass


@dataclass(eq=True, frozen=True)
class Integer(Object):
    value: int

    @property
    def otype(self) -> ObjectType:
        return INTEGER_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value)


@dataclass(eq=True, frozen=True)
class String(Object):
    value: str

    @property
    def otype(self) -> ObjectType:
        return STRING_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value)


@dataclass(eq=True, frozen=True)
class Boolean(Object):
    value: bool

    @property
    def otype(self) -> ObjectType:
        return BOOLEAN_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value).lower()  # True -> true


@dataclass(eq=True, frozen=True)
class Null(Object):
    @property
    def otype(self) -> ObjectType:
        return NULL_OBJ

    @property
    def inspect(self) -> str:
        return "null"


TRUE: Final[Boolean] = Boolean(True)
FALSE: Final[Boolean] = Boolean(False)
NULL: Final[Null] = Null()


@dataclass(eq=True, frozen=True)
class ReturnValue(Object):
    value: Object

    @property
    def otype(self) -> ObjectType:
        return RETURN_VALUE_OBJ

    @property
    def inspect(self) -> str:
        return self.value.inspect


@dataclass(eq=True, frozen=True)
class Error(Object):
    message: str

    @property
    def otype(self) -> ObjectType:
        return ERROR_OBJ

    @property
    def inspect(self) -> str:
        return "ERROR: " + self.message


@dataclass(eq=True, frozen=True)
class Function(Object):
    from . import env

    parameters: List[ast.Identifier]
    body: ast.BlockStatement
    environment: env.Environment

    @property
    def otype(self) -> ObjectType:
        return FUNCTION_OBJ

    @property
    def inspect(self) -> str:
        string = "fn("
        string += ",".join([p.string for p in self.parameters]) + "\n"
        string += self.body.string + "\n"
        return string


@dataclass(eq=True, frozen=True)
class CompiledFunction(Object):
    instructions: bytearray
    n_locals: int
    n_params: int

    @property
    def otype(self) -> ObjectType:
        return COMPILED_FUNCTION_OBJ

    @property
    def inspect(self) -> str:
        str_inst = code.instructions_to_string(self.instructions).replace(
            "\n", "\n    "
        )
        return f"compiled_function[\n    {str_inst}\n]"


@dataclass(eq=True, frozen=True)
class Closure(Object):
    fn: CompiledFunction
    free: list[Object]

    @property
    def otype(self) -> ObjectType:
        return CLOSURE_OBJ

    @property
    def inspect(self) -> str:
        str_inpsect = "Closure["
        str_inpsect += self.fn.inspect
        str_inpsect += ",\nFree[\n"
        for o in self.free:
            str_inpsect += o.inspect
        str_inpsect += "]"
        return str_inpsect


@dataclass(eq=True, frozen=True)
class BuiltIn(Object):
    fn: Callable[..., Object]

    @property
    def otype(self) -> ObjectType:
        return BUILTIN_OBJ

    @property
    def inspect(self) -> str:
        return "builtin function"


@dataclass(eq=True, frozen=True)
class Array(Object):
    elements: List[Object]

    @property
    def otype(self) -> ObjectType:
        return ARRAY_OBJ

    @property
    def inspect(self) -> str:
        return "[" + ", ".join([e.inspect for e in self.elements]) + "]"


@dataclass(eq=True, frozen=True)
class Hash(Object):
    pairs: Dict[Object, Object]

    @property
    def otype(self) -> ObjectType:
        return HASH_OBJ

    @property
    def inspect(self) -> str:
        pair_strs = []
        for pair in self.pairs.items():
            pair_strs.append(pair[0].inspect + ": " + pair[1].inspect)
        return "{" + ", ".join(pair_strs) + "}"
