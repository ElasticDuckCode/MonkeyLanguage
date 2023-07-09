from typing import List
from src.monkey import ast, obj


def eval(node: ast.Node) -> obj.Object:
    match type(node):
        case ast.Program:
            return eval_statements(node.statements)
        case ast.BlockStatement:
            return eval_statements(node.statements)
        case ast.IfExpression:
            condition = eval(node.condition)
            if is_truthy(condition):
                return eval(node.consequence)
            elif node.alternative is not None:
                return eval(node.alternative)
            else:
                return obj.NULL
        case ast.ExpressionStatement:
            return eval(node.expression)
        case ast.PrefixExpression:
            right = eval(node.right)
            return eval_prefix_expression(node.operator, right)
        case ast.InfixExpression:
            left = eval(node.left)
            right = eval(node.right)
            return eval_infix_expression(node.operator, left, right)
        case ast.IntegerLiteral:
            return obj.Integer(node.value)
        case ast.Boolean:
            if node.value:
                return obj.TRUE
            else:
                return obj.FALSE
        case _:
            return None


def eval_statements(stmts: List[ast.Statement]) -> obj.Object:
    result = None
    for stmt in stmts:
        result = eval(stmt)
    return result


def eval_prefix_expression(op: str, right: obj.Object) -> obj.Object:
    match op:
        case "!":
            return eval_bang_operator(right)
        case "-":
            return eval_minus_operator(right)
        case _:
            return obj.NULL  # big-brain


def eval_infix_expression(op: str, left: obj.Object, right: obj.Object):
    if (type(left) == obj.Integer) and (type(right) == obj.Integer):
        return eval_integer_infix_expression(op, left, right)
    elif (type(left) == obj.Boolean) and (type(right) == obj.Boolean):
        return eval_boolean_infix_expression(op, left, right)
    else:
        return obj.NULL


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
            return obj.NULL


def eval_boolean_infix_expression(op: str, left: obj.Boolean, right: obj.Boolean):
    match op:
        case "==":
            return native_bool_to_obj_bool(left == right)  # directly compare
        case "!=":
            return native_bool_to_obj_bool(left != right)
        case _:
            return obj.NULL


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
        return obj.NULL
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
