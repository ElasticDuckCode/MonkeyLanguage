from collections import defaultdict
from typing import DefaultDict
from . import obj


class Environment:
    def __init__(self, outer=None) -> None:
        self._outer: Environment = outer
        self._store: DefaultDict[str, obj.Object | None] = defaultdict(lambda: None)

    def get(self, name: str) -> obj.Object | None:
        val = self._store[name]
        if val is None and self._outer is not None:
            val = self._outer._store[name]
        return val

    def set(self, name: str, o: obj.Object) -> None:
        if o:
            self._store[name] = o
