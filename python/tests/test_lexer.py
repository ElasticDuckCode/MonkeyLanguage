from unittest import TestCase, main
from src.monkey import lexer, token


class TestToken(TestCase):
    def test_lexer_next_token(self):

        input = r"=+(){},;"
        lex = lexer.new(input)

        expected = [
            (token.ASSIGN, "="),
            (token.PLUS, "+"),
            (token.LPAREN, "("),
            (token.RPAREN, ")"),
            (token.LBRACE, "{"),
            (token.RBRACE, "}"),
            (token.COMMA, ","),
            (token.SEMICOLON, ";"),
            (token.EOF, ""),
        ]

        for token_type, literal in expected:
            t = lex.next_token()
            self.assertEqual(t.token_type, token_type)
            self.assertEqual(t.literal, literal)


if __name__ == "__main__":
    main()
