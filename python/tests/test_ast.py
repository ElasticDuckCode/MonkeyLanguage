from unittest import TestCase, main
from src.monkey import token, ast


class TestAST(TestCase):
    def test_ast_string(self):
        program = ast.Program(
            [ast.LetStatement(
                tok=token.Token(token.LET, "let"),
                name=ast.Identifier(token.Token(token.IDENT, "x"), "x"),
                value=ast.Identifier(token.Token(token.IDENT, "y"), "y")
            )]
        )
        self.assertEqual(program.string, "let x = y;")


if __name__ == "__main__":
    main()
