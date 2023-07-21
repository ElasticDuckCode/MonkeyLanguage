from dataclasses import dataclass, field
from typing import NewType

Scope = NewType("Scope", str)
GLOBAL_SCOPE = Scope("GLOBAL")


@dataclass(eq=True, frozen=True)
class Symbol:
    name: str
    scope: Scope
    index: int


@dataclass
class Table:
    store: dict[str, Symbol] = field(default_factory=dict)
    n_def: int = 0

    def resolve(self, name: str) -> Symbol:
        return self.store[name]

    def define(self, name: str) -> Symbol:
        sym = Symbol(name, GLOBAL_SCOPE, self.n_def)
        self.store[name] = sym
        self.n_def += 1
        return sym
