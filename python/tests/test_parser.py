from unittest import TestCase, main
from src.monkey import lexer, parser, ast


class TestParser(TestCase):

    def verify_integer_literal(self, intlit: ast.IntegerLiteral, value: int):
        self.assertIsInstance(intlit, ast.IntegerLiteral)
        self.assertEqual(intlit.value, value)
        self.assertEqual(intlit.token_literal, str(value))

    def verify_string_literal(self, slit: ast.StringLiteral, value: str):
        self.assertIsInstance(slit, ast.StringLiteral)
        self.assertEqual(slit.value, value)
        self.assertEqual(slit.token_literal, value)

    def verify_boolean(self, b: ast.Boolean, value: bool):
        self.assertIsInstance(b, ast.Boolean)
        self.assertEqual(b.value, value)
        self.assertEqual(b.token_literal, str(value).lower())  # "True"->"true"

    def verify_identifier(self, exp: ast.Identifier, value: str):
        self.assertIsInstance(exp, ast.Identifier)
        self.assertEqual(exp.value, value)
        self.assertEqual(exp.token_literal, value)

    def verify_literal_expression(self, exp: ast.Expression, expected):
        if type(expected) == int:
            self.verify_integer_literal(exp, expected)
        elif type(expected) == bool:
            self.verify_boolean(exp, expected)
        else:
            self.verify_identifier(exp, expected)

    def verify_let_statement(self, stmt: ast.LetStatement, name: str):
        self.assertIsInstance(stmt, ast.LetStatement)
        self.assertEqual(stmt.token_literal, "let")
        self.assertEqual(stmt.name.value, name)
        self.assertEqual(stmt.name.token_literal, name)

    def verify_return_statement(self, stmt: ast.ReturnStatement):
        self.assertIsInstance(stmt, ast.ReturnStatement)
        self.assertEqual(stmt.token_literal, "return")

    def verify_prefix_expression(self, exp: ast.PrefixExpression, operator: str, right):
        self.assertIsInstance(exp, ast.PrefixExpression)
        self.assertEqual(exp.operator, operator)
        self.verify_literal_expression(exp.right, right)

    def verify_infix_expression(self, exp: ast.InfixExpression, left, operator: str, right):
        self.assertIsInstance(exp, ast.InfixExpression)
        self.verify_literal_expression(exp.left, left)
        self.assertEqual(exp.operator, operator)
        self.verify_literal_expression(exp.right, right)

    def test_parser_let_statement_identifiers(self):
        code = ("let x = 5;\n"
                "let y = 10;\n"
                "let foobar = 838383;\n")

        expected_identifiers = [
            "x",
            "y",
            "foobar"
        ]

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()

        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 3)

        for stmt, ident in zip(program.statements, expected_identifiers):
            self.assertEqual(stmt.token_literal, "let")
            self.assertIsInstance(stmt, ast.LetStatement)
            self.assertEqual(stmt.name.value, ident)
            self.assertEqual(stmt.name.token_literal, ident)

    def test_parser_errors(self):
        bad_code = ("let x 5;\n"
                    "let = 10;\n"
                    "let 838383;\n")

        lex = lexer.Lexer(bad_code)
        par = parser.Parser(lex)
        program = par.parse_program()

        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 4, par.error_str)

    def test_parser_return_statement_identifiers(self):
        code = ("return 5;\n"
                "return 10;\n"
                "return 993322;\n")

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 3)

        for stmt in program.statements:
            self.assertIsInstance(stmt, ast.ReturnStatement)
            self.assertEqual(stmt.token_literal, "return")

    def test_parser_identifier_expressions(self):
        code = "foobar;"

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)

        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.verify_identifier(stmt.expression, "foobar")

    def test_parser_integer_literal_expressions(self):
        code = "5;"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)

        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.verify_integer_literal(stmt.expression, 5)

    def test_parser_booleans(self):
        examples = [
            ("true;", True),
            ("false;", False)
        ]

        for code, expected in examples:
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.assertIsInstance(stmt, ast.ExpressionStatement)
            self.verify_boolean(stmt.expression, expected)

    def test_parser_unary_prefix_expressions(self):
        prefix_tests = {
            "!5;": ("!", 5),
            "-15;": ("-", 15),
            "!true;": ("!", True),
            "!false;": ("!", False),
        }
        for code in prefix_tests.keys():
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.assertIsInstance(stmt, ast.ExpressionStatement)
            self.verify_prefix_expression(stmt.expression, *prefix_tests[code])

    def test_parse_binary_infix_expressions(self):
        infix_tests = {
            "5 + 5;": (5, "+", 5),
            "5 - 5": (5, "-", 5),
            "5 * 5": (5, "*", 5),
            "5 / 5": (5, "/", 5),
            "5 > 5": (5, ">", 5),
            "5 < 5": (5, "<", 5),
            "5 == 5": (5, "==", 5),
            "5 != 5": (5, "!=", 5),
            "true == true": (True, "==", True),
            "true != false": (True, "!=", False),
            "false == false": (False, "==", False),
        }
        for code in infix_tests.keys():
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.assertIsInstance(stmt, ast.ExpressionStatement)
            self.verify_infix_expression(stmt.expression, *infix_tests[code])

    def test_parser_infix_expression_precidence(self):
        code_examples = [
            ("-a * b", "((-a) * b)"),
            ("!-a", "(!(-a))"),
            ("a + b + c", "((a + b) + c)"),
            ("a + b - c", "((a + b) - c)"),
            ("a * b * c", "((a * b) * c)"),
            ("a * b / c", "((a * b) / c)"),
            ("a + b / c", "(a + (b / c))"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
            ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
            ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
            (
                "3 + 4 * 5 == 3 * 1 + 4 * 5",
                "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"
            ),
            ("true", "true"),
            ("false", "false"),
            ("3 > 5 == false", "((3 > 5) == false)"),
            ("3 < 5 == true", "((3 < 5) == true)"),
            ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
            ("(5 + 5) * 2", "((5 + 5) * 2)"),
            ("2 / (5 + 5)", "(2 / (5 + 5))"),
            ("(5 + 5) * 2 * (5 + 5)", "(((5 + 5) * 2) * (5 + 5))"),
            ("-(5 + 5)", "(-(5 + 5))"),
            ("!(true == true)", "(!(true == true))"),
            ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
            (
                "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
                "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))"
            ),
            (
                "add(a + b + c * d / f + g)",
                "add((((a + b) + ((c * d) / f)) + g))"
            ),
            (
                "a * [1, 2, 3, 4][b * c] * d",
                "((a * ([1, 2, 3, 4][(b * c)])) * d)",
            ),
            (
                "add(a * b[2], b[1], 2 * [1, 2][1])",
                "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
            ),
        ]

        for code, expected in code_examples:
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(program.string, expected)

        return

    def test_parser_if_expression(self):
        code = "if (x < y) { x }"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.assertIsInstance(stmt.expression, ast.IfExpression)
        exp = stmt.expression
        self.verify_infix_expression(exp.condition, "x", "<", "y")
        cons_stmts = exp.consequence.statements
        self.assertEqual(len(cons_stmts), 1)
        self.assertIsInstance(cons_stmts[0], ast.ExpressionStatement)
        con_exp = cons_stmts[0].expression
        self.verify_identifier(con_exp, "x")
        self.assertEqual(exp.alternative, None)

    def test_parser_if_else_expression(self):
        code = "if (x < y) { x } else { y }"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.assertIsInstance(stmt.expression, ast.IfExpression)
        exp = stmt.expression
        self.verify_infix_expression(exp.condition, "x", "<", "y")
        cons_stmts = exp.consequence.statements
        self.assertEqual(len(cons_stmts), 1)
        self.assertIsInstance(cons_stmts[0], ast.ExpressionStatement)
        con_exp = cons_stmts[0].expression
        self.verify_identifier(con_exp, "x")
        alt_stmts = exp.alternative.statements
        self.assertEqual(len(alt_stmts), 1)
        self.assertIsInstance(alt_stmts[0], ast.ExpressionStatement)
        alt_exp = alt_stmts[0].expression
        self.verify_identifier(alt_exp, "y")

    def test_parser_function_literal(self):
        code = "fn(x, y) { x + y; }"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.assertIsInstance(stmt.expression, ast.FunctionLiteral)
        params = stmt.expression.parameters
        self.assertEqual(len(params), 2)
        self.verify_literal_expression(params[0], "x")
        self.verify_literal_expression(params[1], "y")
        body = stmt.expression.body.statements
        body = stmt.expression.body.statements[0]
        self.assertIsInstance(body, ast.ExpressionStatement)
        self.verify_infix_expression(body.expression, "x", "+", "y")

    def test_parser_function_param_cases(self):
        cases = [
            ("fn() {};", []),
            ("fn(x) {};", ["x"]),
            ("fn(x, y, z) {};", ["x", "y", "z"]),
        ]
        for code, expected_params in cases:
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.assertIsInstance(stmt, ast.ExpressionStatement)
            self.assertIsInstance(stmt.expression, ast.FunctionLiteral)
            params = stmt.expression.parameters
            self.assertEqual(len(params), len(expected_params))
            for ident, expected_ident in zip(params, expected_params):
                self.verify_literal_expression(ident, expected_ident)

    def test_parser_call_expression(self):
        code = "add(1, 2 * 3, 4 + 5);"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        self.assertIsInstance(exp, ast.CallExpression)
        self.verify_identifier(exp.function, "add")
        self.assertEqual(len(exp.arguements), 3)
        self.verify_literal_expression(exp.arguements[0], 1)
        self.verify_infix_expression(exp.arguements[1], 2, "*", 3)
        self.verify_infix_expression(exp.arguements[2], 4, "+", 5)

    def test_parser_call_arguement_cases(self):
        cases = [
            ("add();", []),
            ("add(x);", ["x"]),
            ("add(x, y, z);", ["x", "y", "z"]),
        ]
        for code, expected_args in cases:
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.assertIsInstance(stmt, ast.ExpressionStatement)
            self.assertIsInstance(stmt.expression, ast.CallExpression)
            self.verify_identifier(stmt.expression.function, "add")
            args = stmt.expression.arguements
            self.assertEqual(len(args), len(expected_args))
            for arg, expected_arg in zip(args, expected_args):
                self.verify_literal_expression(arg, expected_arg)

    def test_parser_let_statement(self):
        cases = [
            ("let x = 5;", ("x", 5)),
            ("let y = true;", ("y", True)),
            ("let foobar = y;", ("foobar", "y")),
        ]
        for code, expected in cases:
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.verify_let_statement(stmt, expected[0])
            self.verify_literal_expression(stmt.value, expected[1])

    def test_parser_return_statement(self):
        cases = [
            ("return 5;", 5),
            ("return true;", True),
            ("return foobar;", "foobar")
        ]
        for code, expected in cases:
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, par.error_str)
            self.assertEqual(len(program.statements), 1)
            stmt = program.statements[0]
            self.verify_return_statement(stmt)
            self.verify_literal_expression(stmt.value, expected)

    def test_parser_string_literal_expressions(self):
        code, expected = (r'"hello world";', "hello world")
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.verify_string_literal(stmt.expression, expected)

    def test_parser_array_literal(self):
        code = "[1, 2 * 2, 3 + 3];"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        array = stmt.expression
        self.verify_integer_literal(array.elements[0], 1)
        self.verify_infix_expression(array.elements[1], 2, "*", 2)
        self.verify_infix_expression(array.elements[2], 3, "+", 3)

        code = "[];"
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        array = stmt.expression
        self.assertEqual(len(array.elements), 0)

    def test_parser_index_expression(self):
        code = 'myArray[1 + 1];'
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        self.assertIsInstance(exp, ast.IndexExpression)
        self.verify_identifier(exp.left, "myArray")
        self.verify_infix_expression(exp.index, 1, "+", 1)
        self.assertEqual(exp.string, "(myArray[(1 + 1)])")

    def test_parser_hash_literals_string_keys(self):
        code = '{"one": 1, "two": 2, "three": 3}'
        expect = (
            ("one", 1),
            ("two", 2),
            ("three", 3),
        )
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        self.assertIsInstance(exp, ast.HashLiteral)
        self.assertEqual(len(exp.pairs), 3)
        for i, [key, val] in enumerate(exp.pairs.items()):
            self.assertIsInstance(key, ast.StringLiteral)
            self.verify_string_literal(key, expect[i][0])
            self.verify_integer_literal(val, expect[i][1])
        self.assertEqual(exp.string, "{one: 1, two: 2, three: 3}")

        code = '{}'
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        self.assertEqual(len(program.statements), 1)
        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        self.assertIsInstance(exp, ast.HashLiteral)
        self.assertEqual(len(exp.pairs), 0)
        self.assertEqual(exp.string, "{}")

        # TODO: with infix


if __name__ == "__main__":
    main()
