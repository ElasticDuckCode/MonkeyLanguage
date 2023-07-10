from collections import defaultdict
from typing import Dict, Tuple

from ..obj import obj


def _monkey_builtin_len(*args: Tuple[obj.Object]) -> obj.Object:
    from .eval import new_error
    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    if type(args[0]) == obj.String:
        return obj.Integer(len(args[0].value))
    return new_error(f"arguement to `len` not supported. got {args[0].otype}")


BuiltIn: Dict[str, obj.BuiltIn] = defaultdict(lambda: None)
BuiltIn["len"] = obj.BuiltIn(fn=_monkey_builtin_len)
