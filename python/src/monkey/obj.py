from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Final


class ObjectType(str):
    pass


INTEGER_OBJ: Final[ObjectType] = "INTEGER"
BOOLEAN_OBJ: Final[ObjectType] = "BOOLEAN"
NULL_OBJ:    Final[ObjectType] = "NULL"


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
        return str(self.value)


@dataclass
class Null(Object):

    @property
    def otype(self) -> ObjectType: return NULL_OBJ

    @property
    def inspect(self) -> str:
        return "null"
