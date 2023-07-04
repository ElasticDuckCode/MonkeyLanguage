from unittest import TestCase, main
from src.monkey import lexer, parser, ast

example_code = """\
let x = 5;
let y = 10;
let foobar = 838383;
"""

bad_code = """\
let x 5;
let = 10;
let 838383;
"""


class TestParser(TestCase):

    def test_lexer_example_code(self):
        expected_identifiers = [
            "x",
            "y",
            "foobar"
        ]

        lex = lexer.Lexer(example_code)
        par = parser.Parser(lex)
        program = par.parse_program()

        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 3)

        for stmt, ident in zip(program.statements, expected_identifiers):
            self.assertEqual(stmt.token_literal, "let")
            self.assertIsInstance(stmt, ast.LetStatement)
            self.assertEqual(stmt.name.value, ident)
            self.assertEqual(stmt.name.token_literal, ident)

    def test_lexer_bad_code(self):
        def check_parser_errors(par):
            errors = par.errors
            self.assertEqual(len(errors), 3)

        lex = lexer.Lexer(bad_code)
        par = parser.Parser(lex)
        program = par.parse_program()

        self.assertIsNotNone(program)
        self.assertEqual(len(program.statements), 0)
        check_parser_errors(par)


if __name__ == "__main__":
    main()
