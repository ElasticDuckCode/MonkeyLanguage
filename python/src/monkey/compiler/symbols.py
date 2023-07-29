from dataclasses import dataclass
from typing import NewType, Optional

Scope = NewType("Scope", str)
GLOBAL_SCOPE = Scope("GLOBAL")
LOCAL_SCOPE = Scope("LOCAL")


@dataclass(eq=True, frozen=True)
class Symbol:
    name: str
    scope: Scope
    index: int


class Table:
    def __init__(
        self,
        outer=None,
        store: Optional[dict[str, Symbol]] = None,
        n_def: int = 0,
    ):
        self.store: dict[str, Symbol] = {}
        self.n_def: int = n_def
        if store:
            store = store
        self.outer: Table | None = outer

    def resolve(self, name: str) -> Symbol | None:
        if self.outer:
            if name not in self.store.keys():
                return self.outer.resolve(name)
        if name not in self.store.keys():
            return None
        return self.store[name]

    def define(self, name: str) -> Symbol:
        scope = GLOBAL_SCOPE
        if self.outer is not None:
            scope = LOCAL_SCOPE
        sym = Symbol(name, scope, self.n_def)
        self.store[name] = sym
        self.n_def += 1
        return sym
