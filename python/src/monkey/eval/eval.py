from typing import List

from ..ast import ast
from ..obj import obj
from ..obj import env
from .builtin import BuiltIn


def eval(node: ast.Node | None, e: env.Environment) -> obj.Object | None:
    match node:
        case ast.Program():
            return eval_program(node.statements, e)
        case ast.BlockStatement():
            return eval_block_statements(node.statements, e)
        case ast.Identifier():
            return eval_identifier(node, e)
        case ast.IfExpression():
            condition = eval(node.condition, e)
            if is_error(condition):
                return condition
            if is_truthy(condition):
                return eval(node.consequence, e)
            elif node.alternative is not None:
                return eval(node.alternative, e)
            else:
                return obj.NULL
        case ast.LetStatement():
            val = eval(node.value, e)
            if is_error(val):
                return val
            if val:
                e.set(node.name.value, val)
            return None
        case ast.ReturnStatement():
            val = eval(node.value, e)
            if is_error(val):
                return val
            if val:
                return obj.ReturnValue(val)
            return None
        case ast.FunctionLiteral():
            if node.parameters and node.body:
                return obj.Function(node.parameters, node.body, e)
            return None
        case ast.CallExpression():
            function = eval(node.function, e)
            if is_error(function):
                return function
            if node.arguements is None:
                args = eval_expressions([], e)
            else:
                args = eval_expressions(node.arguements, e)
            if len(args) == 1 and is_error(args[0]):
                return args[0]
            if function and args:
                return apply_function(function, args)
            return None
        case ast.ArrayLiteral():
            if node.elements is None:
                elements = eval_expressions([], e)
            else:
                elements = eval_expressions(node.elements, e)
            if len(elements) == 1 and is_error(elements[0]):
                return elements[0]
            return obj.Array(elements)
        case ast.IndexExpression():
            left = eval(node.left, e)
            if is_error(left):
                return left
            index = eval(node.index, e)
            if is_error(index):
                return index
            if left and index:
                return eval_index_expression(left, index)
            return None
        case ast.HashLiteral():
            return eval_hash_literal(node, e)
        case ast.ExpressionStatement():
            return eval(node.expression, e)
        case ast.PrefixExpression():
            right = eval(node.right, e)
            if is_error(right):
                return right
            if right:
                return eval_prefix_expression(node.operator, right, e)
            return None
        case ast.InfixExpression():
            left = eval(node.left, e)
            if is_error(left):
                return left
            right = eval(node.right, e)
            if is_error(right):
                return right
            if left and right:
                return eval_infix_expression(node.operator, left, right, e)
            return None
        case ast.IntegerLiteral():
            return obj.Integer(node.value)
        case ast.StringLiteral():
            return obj.String(node.value)
        case ast.Boolean():
            if node.value:
                return obj.TRUE
            else:
                return obj.FALSE
        case _:
            return None


def eval_program(stmts: List[ast.Statement], e: env.Environment) -> obj.Object | None:
    result = None
    for stmt in stmts:
        result = eval(stmt, e)
        if type(result) == obj.ReturnValue:
            return result.value
        if type(result) == obj.Error:
            return result
    return result


def eval_expressions(
    exps: List[ast.Expression], e: env.Environment
) -> List[obj.Object]:
    result = []
    for exp in exps:
        evaluated = eval(exp, e)
        if evaluated:
            if is_error(evaluated):
                return [evaluated]
            result.append(evaluated)
    return result


def apply_function(fn: obj.Object, args: List[obj.Object]):
    if type(fn) == obj.Function:
        extended_e = extend_function_environment(fn, args)
        evaluated = eval(fn.body, extended_e)
        if evaluated:
            return unwrap_return_value(evaluated)
        return None
    elif type(fn) == obj.BuiltIn:
        return fn.fn(*args)
    return new_error(f"not a function: {fn.otype}")


def extend_function_environment(fn: obj.Function, args: List[obj.Object]):
    e = env.Environment(fn.environment)
    for i, param in enumerate(fn.parameters):
        e.set(param.value, args[i])
    return e


def unwrap_return_value(o: obj.Object):
    if type(o) == obj.ReturnValue:
        return o.value
    else:
        return o


def eval_block_statements(
    stmts: List[ast.Statement], e: env.Environment
) -> obj.Object | None:
    result = None
    for stmt in stmts:
        result = eval(stmt, e)
        if result is not None:
            if type(result) == obj.ReturnValue:
                return result
            if type(result) == obj.Error:
                return result
    return result


def eval_identifier(node: ast.Identifier, e: env.Environment) -> obj.Object:
    if node is not None and node.value == "null":
        return obj.NULL
    val = e.get(node.value)
    if val:
        return val
    blt = BuiltIn[node.value]
    if blt:
        return blt
    return new_error(f"identifier not found: {node.value}")


def eval_prefix_expression(
    op: str, right: obj.Object, e: env.Environment
) -> obj.Object:
    match op:
        case "!":
            return eval_bang_operator(right, e)
        case "-":
            return eval_minus_operator(right, e)
        case _:
            return new_error(f"unknown operator: {op}{right.otype}")


def eval_infix_expression(
    op: str, left: obj.Object, right: obj.Object, e: env.Environment
):
    if (type(left) == obj.Integer) and (type(right) == obj.Integer):
        return eval_integer_infix_expression(op, left, right, e)
    elif (type(left) == obj.Boolean) and (type(right) == obj.Boolean):
        return eval_boolean_infix_expression(op, left, right, e)
    elif (type(left) == obj.String) and (type(right) == obj.String):
        return eval_string_infix_expression(op, left, right, e)
    elif type(left) != type(right):
        return new_error(f"type mismatch: {left.otype} {op} {right.otype}")
    else:
        return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_integer_infix_expression(
    op: str, left: obj.Integer, right: obj.Integer, e: env.Environment
) -> obj.Object:
    match op:
        case "+":
            return obj.Integer(left.value + right.value)
        case "-":
            return obj.Integer(left.value - right.value)
        case "*":
            return obj.Integer(left.value * right.value)
        case "/":
            if right.value != 0:
                return obj.Integer(left.value // right.value)
            else:
                return obj.NULL
        case "<":
            return native_bool_to_obj_bool(left.value < right.value)
        case ">":
            return native_bool_to_obj_bool(left.value > right.value)
        case "==":
            return native_bool_to_obj_bool(left.value == right.value)
        case "!=":
            return native_bool_to_obj_bool(left.value != right.value)
        case _:
            return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_boolean_infix_expression(
    op: str, left: obj.Boolean, right: obj.Boolean, e: env.Environment
) -> obj.Object:
    match op:
        case "==":
            return native_bool_to_obj_bool(left == right)  # directly compare
        case "!=":
            return native_bool_to_obj_bool(left != right)
        case _:
            return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_string_infix_expression(
    op: str, left: obj.String, right: obj.String, e: env.Environment
) -> obj.Object:
    match op:
        case "+":
            return obj.String(left.value + right.value)
        case _:
            return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_index_expression(left: obj.Object, index: obj.Object):
    if (type(left) == obj.Array) and (type(index) == obj.Integer):
        return eval_array_integer_index_expression(left, index)
    if type(left) == obj.Hash:
        if not is_hashable(index):
            return new_error(f"unusable as hash key: {index.otype}")
        return eval_hash_index_expression(left, index)
    return new_error(f"index operator not supported: {left.otype}")


def eval_array_integer_index_expression(left: obj.Array, index: obj.Integer):
    array = left.elements
    idx = index.value
    if (idx < -len(array)) or (idx >= len(array)):
        return obj.NULL
    return array[idx % len(array)]


def eval_hash_index_expression(left: obj.Hash, key: obj.Object):
    if key not in left.pairs.keys():
        return obj.NULL
    return left.pairs[key]


def eval_bang_operator(right: obj.Object, e: env.Environment) -> obj.Object:
    match right:
        case obj.TRUE:
            return obj.FALSE
        case obj.FALSE:
            return obj.TRUE
        case obj.NULL:
            return obj.TRUE  # omega-brain
        case _:
            return obj.FALSE  # galaxy-brain


def native_bool_to_obj_bool(native: bool):
    if native:
        return obj.TRUE
    else:
        return obj.FALSE


def eval_minus_operator(right: obj.Object, e: env.Environment) -> obj.Object:
    if type(right) != obj.Integer:
        return new_error(f"unknown operator: -{right.otype}")
    return obj.Integer(-right.value)


def eval_hash_literal(node: ast.HashLiteral, e: env.Environment) -> obj.Object:
    pairs = {}
    for key_node, val_node in node.pairs.items():
        key = eval(key_node, e)
        if key is None:
            return new_error(f"missing hash key.")
        if is_error(key):
            return key
        if not is_hashable(key):
            return new_error(f"unusable as hash key: {key.otype}")
        value = eval(val_node, e)
        if value is None:
            return new_error(f"missing hash value.")
        if is_error(value):
            return value
        pairs[key] = value
    return obj.Hash(pairs)


def is_hashable(key):
    if type(key) not in [obj.Integer, obj.String, obj.Boolean]:
        return False
    return True


def is_truthy(o: obj.Object | None):
    match o:
        case obj.NULL:
            return False
        case obj.TRUE:
            return True
        case obj.FALSE:
            return False
        case _:
            return True


def new_error(msg: str) -> obj.Error:
    return obj.Error(msg)


def is_error(o: obj.Object | None):
    if o is not None:
        return o.otype == obj.ERROR_OBJ
    else:
        return False
