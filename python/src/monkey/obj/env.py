from collections import defaultdict
from typing import Mapping
from . import obj


class Environment:

    def __init__(self, outer=None):
        self._outer: Environment = outer
        self._store: Mapping[obj.Object] = defaultdict(lambda: None)

    def get(self, name: str) -> obj.Object:
        val = self._store[name]
        if val is None and self._outer is not None:
            val = self._outer._store[name]
        return val

    def set(self, name: str, o: obj.Object) -> None:
        self._store[name] = o
