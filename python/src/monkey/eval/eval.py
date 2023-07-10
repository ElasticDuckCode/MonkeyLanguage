from typing import List

from ..ast import ast
from ..obj import obj
from ..obj import env
from .builtin import BuiltIn


def eval(node: ast.Node, e: env.Environment) -> obj.Object:
    match type(node):
        case ast.Program:
            return eval_program(node.statements, e)
        case ast.BlockStatement:
            return eval_block_statements(node.statements, e)
        case ast.Identifier:
            return eval_identifier(node, e)
        case ast.IfExpression:
            condition = eval(node.condition, e)
            if is_error(condition):
                return condition
            if is_truthy(condition):
                return eval(node.consequence, e)
            elif node.alternative is not None:
                return eval(node.alternative, e)
            else:
                return obj.NULL
        case ast.LetStatement:
            val = eval(node.value, e)
            if is_error(val):
                return val
            e.set(node.name.value, val)
        case ast.ReturnStatement:
            val = eval(node.value, e)
            if is_error(val):
                return val
            return obj.ReturnValue(val)
        case ast.FunctionLiteral:
            return obj.Function(node.parameters, node.body, e)
        case ast.CallExpression:
            function = eval(node.function, e)
            if is_error(function):
                return function
            args = eval_expressions(node.arguements, e)
            if len(args) == 1 and is_error(args[0]):
                return args[0]
            return apply_function(function, args)
        case ast.ArrayLiteral:
            elements = eval_expressions(node.elements, e)
            if len(elements) == 1 and is_error(elements[0]):
                return elements[0]
            return obj.Array(elements)
        case ast.IndexExpression:
            left = eval(node.left, e)
            if is_error(left):
                return left
            index = eval(node.index, e)
            if is_error(index):
                return index
            return eval_index_expression(left, index)
        case ast.ExpressionStatement:
            return eval(node.expression, e)
        case ast.PrefixExpression:
            right = eval(node.right, e)
            if is_error(right):
                return right
            return eval_prefix_expression(node.operator, right, e)
        case ast.InfixExpression:
            left = eval(node.left, e)
            if is_error(left):
                return left
            right = eval(node.right, e)
            if is_error(right):
                return right
            return eval_infix_expression(node.operator, left, right, e)
        case ast.IntegerLiteral:
            return obj.Integer(node.value)
        case ast.StringLiteral:
            return obj.String(node.value)
        case ast.Boolean:
            if node.value:
                return obj.TRUE
            else:
                return obj.FALSE
        case _:
            return None


def eval_program(stmts: List[ast.Statement], e: env.Environment) -> obj.Object:
    result = None
    for stmt in stmts:
        result = eval(stmt, e)
        if type(result) == obj.ReturnValue:
            return result.value
        if type(result) == obj.Error:
            return result
    return result


def eval_expressions(exps: List[ast.Expression], e: env.Environment) -> List[obj.Object]:
    result = []
    for exp in exps:
        evaluated = eval(exp, e)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def apply_function(fn: obj.Object, args: List[ast.Expression]):
    if type(fn) == obj.Function:
        extended_e = extend_function_environment(fn, args)
        evaluated = eval(fn.body, extended_e)
        return unwrap_return_value(evaluated)
    elif type(fn) == obj.BuiltIn:
        return fn.fn(*args)
    return new_error(f"not a function: {fn.otype}")


def extend_function_environment(fn: obj.Function, args: List[ast.Expression]):
    e = env.Environment(fn.environment)
    for i, param in enumerate(fn.parameters):
        e.set(param.value, args[i])
    return e


def unwrap_return_value(o: obj.Object):
    if type(o) == obj.ReturnValue:
        return o.value
    else:
        return o


def eval_block_statements(stmts: List[ast.Statement], e: env.Environment) -> obj.Object:
    result = None
    for stmt in stmts:
        result = eval(stmt, e)
        if result is not None:
            if type(result) == obj.ReturnValue:
                return result
            if type(result) == obj.Error:
                return result
    return result


def eval_identifier(node: ast.Node, e: env.Environment) -> obj.Object:
    if node is not None and node.value == "null":
        return obj.NULL
    val = e.get(node.value)
    if val:
        return val
    blt = BuiltIn[node.value]
    if blt:
        return blt
    return new_error(f"identifier not found: {node.value}")


def eval_prefix_expression(op: str, right: obj.Object, e: env.Environment) -> obj.Object:
    match op:
        case "!":
            return eval_bang_operator(right, e)
        case "-":
            return eval_minus_operator(right, e)
        case _:
            return new_error(f"unknown operator: {op}{right.otype}")


def eval_infix_expression(op: str, left: obj.Object, right: obj.Object, e: env.Environment):
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


def eval_integer_infix_expression(op: str, left: obj.Integer, right: obj.Integer, e: env.Environment) -> obj.Object:
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


def eval_boolean_infix_expression(op: str, left: obj.Boolean, right: obj.Boolean, e: env.Environment) -> obj.Object:
    match op:
        case "==":
            return native_bool_to_obj_bool(left == right)  # directly compare
        case "!=":
            return native_bool_to_obj_bool(left != right)
        case _:
            return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_string_infix_expression(op: str, left: obj.String, right: obj.String, e: env.Environment) -> obj.Object:
    match op:
        case "+":
            return obj.String(left.value + right.value)
        case _:
            return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_index_expression(left: obj.Object, index: obj.Object):
    if (type(left) == obj.Array) and (type(index) == obj.Integer):
        return eval_array_integer_index_expression(left, index)
    return new_error(f"index operator not supported: {left.otype}")


def eval_array_integer_index_expression(left: obj.Array, index: obj.Integer):
    array = left.elements
    idx = index.value
    if (idx < 0) or (idx >= len(array)):
        return obj.NULL
    return array[idx]


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


def is_truthy(o: obj.Object):
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


def is_error(o: obj.Object):
    if o is not None:
        return o.otype == obj.ERROR_OBJ
    else:
        return False
