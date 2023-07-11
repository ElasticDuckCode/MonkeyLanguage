from collections import defaultdict
from typing import Dict, Tuple

from ..obj import obj


def _monkey_builtin_len(*args: Tuple[obj.Object]) -> obj.Object:
    from .eval import new_error
    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    if type(args[0]) == obj.String:
        return obj.Integer(len(args[0].value))
    if type(args[0]) == obj.Array:
        return obj.Integer(len(args[0].elements))
    return new_error(f"arguement to `len` not supported. got {args[0].otype}")


def _monkey_builtin_first(*args: Tuple[obj.Object]) -> obj.Object:
    from .eval import new_error
    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    if type(args[0]) == obj.Array:
        if len(args[0].elements) > 0:
            return args[0].elements[0]
        else:
            return obj.NULL
    return new_error(f"arguement to `first` not supported. got {args[0].otype}")


def _monkey_builtin_last(*args: Tuple[obj.Object]) -> obj.Object:
    from .eval import new_error
    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    if type(args[0]) == obj.Array:
        if len(args[0].elements) > 0:
            return args[0].elements[-1]
        else:
            return obj.NULL
    return new_error(f"arguement to `last` not supported. got {args[0].otype}")


def _monkey_builtin_rest(*args: Tuple[obj.Object]) -> obj.Object:
    from .eval import new_error
    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    if type(args[0]) == obj.Array:
        if len(args[0].elements) > 0:
            array = args[0].elements[1:]
            return obj.Array(array.copy())
        else:
            return obj.NULL
    return new_error(f"arguement to `rest` not supported. got {args[0].otype}")


def _monkey_builtin_push(*args: Tuple[obj.Object]) -> obj.Object:
    from .eval import new_error
    if len(args) != 2:
        return new_error(f"wrong number of arguements. got={len(args)}, want=2")
    if type(args[0]) != obj.Array:
        return new_error(f"arguement to `push` not supported. got {args[0].otype}")
    array = args[0].elements.copy()
    array.append(args[1])
    return obj.Array(array)


def _monkey_builtin_puts(*args: Tuple[obj.Object]) -> obj.Object:
    print(*[a.inspect for a in args])
    return obj.NULL


BuiltIn: Dict[str, obj.BuiltIn] = defaultdict(lambda: None)
BuiltIn["len"] = obj.BuiltIn(fn=_monkey_builtin_len)
BuiltIn["first"] = obj.BuiltIn(fn=_monkey_builtin_first)
BuiltIn["last"] = obj.BuiltIn(fn=_monkey_builtin_last)
BuiltIn["rest"] = obj.BuiltIn(fn=_monkey_builtin_rest)
BuiltIn["push"] = obj.BuiltIn(fn=_monkey_builtin_push)
BuiltIn["puts"] = obj.BuiltIn(fn=_monkey_builtin_puts)
