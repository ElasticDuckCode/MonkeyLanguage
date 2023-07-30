from dataclasses import dataclass

from ..obj import obj


@dataclass
class Frame:
    cl: obj.Closure
    ip: int = 0
    bp: int = 0

    @property
    def instructions(self):
        return self.cl.fn.instructions
