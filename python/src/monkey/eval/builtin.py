from collections import defaultdict
from typing import DefaultDict, Callable

from ..obj import obj


def _monkey_builtin_len(*args: obj.Object) -> obj.Object:
    from .eval import new_error

    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    match args[0]:
        case obj.String():
            return obj.Integer(len(args[0].value))
        case obj.Array():
            return obj.Integer(len(args[0].elements))
        case obj.Object():
            return new_error(f"arguement to `len` not supported. got {args[0].otype}")
        case _:
            return new_error(f"arguement to `len` not an obj.Object. got {args[0]}")


def _monkey_builtin_first(*args: obj.Object) -> obj.Object:
    from .eval import new_error

    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    match args[0]:
        case obj.Array():
            if len(args[0].elements) > 0:
                return args[0].elements[0]
            else:
                return obj.NULL
        case obj.Object():
            return new_error(f"arguement to `first` not supported. got {args[0].otype}")
        case _:
            return new_error(f"arguement to `len` not an obj.Object. got {args[0]}")


def _monkey_builtin_last(*args: obj.Object) -> obj.Object:
    from .eval import new_error

    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    match args[0]:
        case obj.Array():
            if len(args[0].elements) > 0:
                return args[0].elements[-1]
            else:
                return obj.NULL
        case obj.Object():
            return new_error(f"arguement to `last` not supported. got {args[0].otype}")
        case _:
            return new_error(f"arguement to `len` not an obj.Object. got {args[0]}")


def _monkey_builtin_rest(*args: obj.Object) -> obj.Object:
    from .eval import new_error

    if len(args) != 1:
        return new_error(f"wrong number of arguements. got={len(args)}, want=1")
    match args[0]:
        case obj.Array():
            if len(args[0].elements) > 0:
                array = args[0].elements[1:]
                return obj.Array(array.copy())
            else:
                return obj.NULL
        case obj.Object():
            return new_error(f"arguement to `rest` not supported. got {args[0].otype}")
        case _:
            return new_error(f"arguement to `len` not an obj.Object. got {args[0]}")


def _monkey_builtin_push(*args: obj.Object) -> obj.Object:
    from .eval import new_error

    if len(args) != 2:
        return new_error(f"wrong number of arguements. got={len(args)}, want=2")
    match args[0]:
        case obj.Array():
            array = args[0].elements.copy()
            array.append(args[1])
            return obj.Array(array)
        case obj.Object():
            return new_error(f"arguement to `push` not supported. got {args[0].otype}")
        case _:
            return new_error(f"arguement to `len` not an obj.Object. got {args[0]}")


def _monkey_builtin_puts(*args: obj.Object) -> obj.Object:
    print(*[a.inspect for a in args])
    return obj.NULL


BuiltIn: DefaultDict[str, obj.BuiltIn | None] = defaultdict(lambda: None)
BuiltIn["len"] = obj.BuiltIn(fn=_monkey_builtin_len)
BuiltIn["first"] = obj.BuiltIn(fn=_monkey_builtin_first)
BuiltIn["last"] = obj.BuiltIn(fn=_monkey_builtin_last)
BuiltIn["rest"] = obj.BuiltIn(fn=_monkey_builtin_rest)
BuiltIn["push"] = obj.BuiltIn(fn=_monkey_builtin_push)
BuiltIn["puts"] = obj.BuiltIn(fn=_monkey_builtin_puts)
