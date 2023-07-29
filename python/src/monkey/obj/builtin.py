from dataclasses import dataclass
from . import obj


def new_error(msg: str) -> obj.Error:
    return obj.Error(msg)


def _monkey_builtin_len(*args: obj.Object) -> obj.Object:
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


@dataclass
class BuiltInStruct:
    name: str
    fn: obj.BuiltIn


BuiltIns: list[BuiltInStruct] = [
    BuiltInStruct("len", obj.BuiltIn(fn=_monkey_builtin_len)),
]


def get_builtin_by_name(name: str) -> obj.BuiltIn | None:
    for b in BuiltIns:
        if b.name == name:
            return b.fn
    return None
