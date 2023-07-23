from dataclasses import dataclass

from ..code import code
from ..obj import obj


@dataclass
class Frame:
    fn: obj.CompiledFunction
    ip: int = 0

    @property
    def instructions(self):
        return self.fn.instructions
