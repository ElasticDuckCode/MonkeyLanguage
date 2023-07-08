from typing import List
from src.monkey import ast, obj


def eval(node: ast.Node) -> obj.Object:
    match type(node):
        case ast.Program:
            return eval_statements(node.statements)
        case ast.ExpressionStatement:
            return eval(node.expression)
        case ast.IntegerLiteral:
            return obj.Integer(node.value)
        case _:
            return None


def eval_statements(stmts: List[ast.Statement]) -> obj.Object:
    result = None
    for stmt in stmts:
        result = eval(stmt)
    return result
