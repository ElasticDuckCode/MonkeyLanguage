from typing import List
from src.monkey import ast, obj


def eval(node: ast.Node) -> obj.Object:
    match type(node):
        case ast.Program:
            return eval_program(node.statements)
        case ast.BlockStatement:
            return eval_block_statements(node.statements)
        case ast.IfExpression:
            condition = eval(node.condition)
            if is_error(condition):
                return condition
            if is_truthy(condition):
                return eval(node.consequence)
            elif node.alternative is not None:
                return eval(node.alternative)
            else:
                return obj.NULL
        case ast.ReturnStatement:
            val = eval(node.value)
            if is_error(val):
                return val
            return obj.ReturnValue(val)
        case ast.ExpressionStatement:
            return eval(node.expression)
        case ast.PrefixExpression:
            right = eval(node.right)
            if is_error(right):
                return right
            return eval_prefix_expression(node.operator, right)
        case ast.InfixExpression:
            left = eval(node.left)
            if is_error(left):
                return left
            right = eval(node.right)
            if is_error(right):
                return right
            return eval_infix_expression(node.operator, left, right)
        case ast.IntegerLiteral:
            return obj.Integer(node.value)
        case ast.Boolean:
            if node.value:
                return obj.TRUE
            else:
                return obj.FALSE
        case _:
            if node is not None and node.value == "null":
                return obj.NULL
            else:
                return None


def eval_program(stmts: List[ast.Statement]) -> obj.Object:
    result = None
    for stmt in stmts:
        result = eval(stmt)
        if type(result) == obj.ReturnValue:
            return result.value
        if type(result) == obj.Error:
            return result
    return result


def eval_block_statements(stmts: List[ast.Statement]) -> obj.Object:
    result = None
    for stmt in stmts:
        result = eval(stmt)
        if result is not None:
            if type(result) == obj.ReturnValue:
                return result
            if type(result) == obj.Error:
                return result
    return result


def eval_prefix_expression(op: str, right: obj.Object) -> obj.Object:
    match op:
        case "!":
            return eval_bang_operator(right)
        case "-":
            return eval_minus_operator(right)
        case _:
            return new_error(f"unknown operator: {op}{right.otype}")


def eval_infix_expression(op: str, left: obj.Object, right: obj.Object):
    if (type(left) == obj.Integer) and (type(right) == obj.Integer):
        return eval_integer_infix_expression(op, left, right)
    elif (type(left) == obj.Boolean) and (type(right) == obj.Boolean):
        return eval_boolean_infix_expression(op, left, right)
    elif type(left) != type(right):
        return new_error(f"type mismatch: {left.otype} {op} {right.otype}")
    else:
        return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_integer_infix_expression(op: str, left: obj.Integer, right: obj.Integer):
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


def eval_boolean_infix_expression(op: str, left: obj.Boolean, right: obj.Boolean):
    match op:
        case "==":
            return native_bool_to_obj_bool(left == right)  # directly compare
        case "!=":
            return native_bool_to_obj_bool(left != right)
        case _:
            return new_error(f"unknown operator: {left.otype} {op} {right.otype}")


def eval_bang_operator(right: obj.Object) -> obj.Object:
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


def eval_minus_operator(right: obj.Object) -> obj.Object:
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
