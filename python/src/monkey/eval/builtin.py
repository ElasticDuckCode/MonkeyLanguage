from collections import defaultdict
from typing import DefaultDict

from ..obj import obj, builtin


BuiltIn: DefaultDict[str, obj.BuiltIn | None] = defaultdict(lambda: None)
BuiltIn["len"] = builtin.get_builtin_by_name("len")
BuiltIn["first"] = builtin.get_builtin_by_name("first")
BuiltIn["last"] = builtin.get_builtin_by_name("last")
BuiltIn["rest"] = builtin.get_builtin_by_name("rest")
BuiltIn["push"] = builtin.get_builtin_by_name("push")
BuiltIn["puts"] = builtin.get_builtin_by_name("puts")
