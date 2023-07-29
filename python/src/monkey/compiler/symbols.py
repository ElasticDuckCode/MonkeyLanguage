from dataclasses import dataclass
from typing import NewType, Optional

Scope = NewType("Scope", str)
GLOBAL_SCOPE = Scope("GLOBAL")
LOCAL_SCOPE = Scope("LOCAL")
BUILTIN_SCOPE = Scope("BUILTIN")
FREE_SCOPE = Scope("FREE")


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
        self.free_sym: list[Symbol] = list()

    def resolve(self, name: str) -> Symbol | None:
        if name not in self.store.keys():
            if self.outer:
                sym = self.outer.resolve(name)
                if sym is None:
                    return None
                if sym.scope not in [GLOBAL_SCOPE, BUILTIN_SCOPE]:
                    sym = self.define_free(sym)
                return sym
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

    def define_builtin(self, i: int, name: str) -> Symbol:
        sym = Symbol(name, BUILTIN_SCOPE, i)
        self.store[name] = sym
        return sym

    def define_free(self, og: Symbol) -> Symbol:
        sym = Symbol(og.name, FREE_SCOPE, len(self.free_sym))
        self.free_sym.append(og)
        self.store[og.name] = sym
        return sym
