from unittest import TestCase, main
from src.monkey import lexer, parser, ast


class TestParser(TestCase):

    def verify_integer_literal(self, intlit: ast.IntegerLiteral, value: int):
        self.assertIsInstance(intlit, ast.IntegerLiteral)
        self.assertEqual(intlit.value, value)
        self.assertEqual(intlit.token_literal, str(value))

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

    def verify_prefix_expression(self, exp: ast.PrefixExpression, operator: str, right):
        self.assertIsInstance(exp, ast.PrefixExpression)
        self.assertEqual(exp.operator, operator)
        self.verify_literal_expression(exp.right, right)

    def verify_infix_expression(self, exp: ast.InfixExpression, left, operator: str, right):
        self.assertIsInstance(exp, ast.InfixExpression)
        self.verify_literal_expression(exp.left, left)
        self.assertEqual(exp.operator, operator)
        self.verify_literal_expression(exp.right, right)

    def test_parser_let_statement(self):
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
        self.assertEqual(len(par.errors), 4, str(par.errors))

    def test_parser_return_statement(self):
        code = ("return 5;\n"
                "return 10;\n"
                "return 993322;\n")

        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, str(par.errors))
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
        self.assertEqual(len(par.errors), 0, str(par.errors))
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
        self.assertEqual(len(par.errors), 0, str(par.errors))
        self.assertEqual(len(program.statements), 1)

        stmt = program.statements[0]
        self.assertIsInstance(stmt, ast.ExpressionStatement)
        self.verify_integer_literal(stmt.expression, 5)

    def test_parser_booleans(self):
        examples = [
            ("true;", True),
            ("false;", False)
        ]

        for example in examples:
            code, expected = example
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, str(par.errors))
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
            self.assertEqual(len(par.errors), 0, str(par.errors))
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
            self.assertEqual(len(par.errors), 0, str(par.errors))
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
            ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
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
            # ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
            # ("add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            # "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))"),
            # ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"),
        ]

        for example in code_examples:
            code, expected = example
            lex = lexer.Lexer(code)
            par = parser.Parser(lex)
            program = par.parse_program()
            self.assertIsNotNone(program)
            self.assertEqual(len(par.errors), 0, str(par.errors))
            self.assertEqual(program.string, expected)

        return


if __name__ == "__main__":
    main()
