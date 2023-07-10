from unittest import TestCase, main
from src.monkey import lexer, token

example_script = r'''
let five = 5;
let ten = 10;

let add = fn(x, y) {
    x + y;
};

let result = add(five, ten);

!-/*5;
5 < 10 > 5;

if (5 < 10) {
    return true;
}
else {
    return false;
}

10 == 10;
10 != 9;
"foobar"
"foo bar"
"foo\\bar"
"foo\"bar"
"hello\n world"
[1, 2];
[];
{ "hello" : 5 };
'''


class TestToken(TestCase):
    def test_lexer_next_token_single_chars(self):
        input = "=+(){},;"
        lex = lexer.Lexer(input)
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

    def test_lexer_next_token_example_script(self):
        input = example_script
        lex = lexer.Lexer(input)
        expected = [
            (token.LET, "let"),
            (token.IDENT, "five"),
            (token.ASSIGN, "="),
            (token.INT, "5"),
            (token.SEMICOLON, ";"),
            (token.LET, "let"),
            (token.IDENT, "ten"),
            (token.ASSIGN, "="),
            (token.INT, "10"),
            (token.SEMICOLON, ";"),
            (token.LET, "let"),
            (token.IDENT, "add"),
            (token.ASSIGN, "="),
            (token.FUNCTION, "fn"),
            (token.LPAREN, "("),
            (token.IDENT, "x"),
            (token.COMMA, ","),
            (token.IDENT, "y"),
            (token.RPAREN, ")"),
            (token.LBRACE, "{"),
            (token.IDENT, "x"),
            (token.PLUS, "+"),
            (token.IDENT, "y"),
            (token.SEMICOLON, ";"),
            (token.RBRACE, "}"),
            (token.SEMICOLON, ";"),
            (token.LET, "let"),
            (token.IDENT, "result"),
            (token.ASSIGN, "="),
            (token.IDENT, "add"),
            (token.LPAREN, "("),
            (token.IDENT, "five"),
            (token.COMMA, ","),
            (token.IDENT, "ten"),
            (token.RPAREN, ")"),
            (token.SEMICOLON, ";"),
            (token.BANG, "!"),
            (token.MINUS, "-"),
            (token.SLASH, "/"),
            (token.ASTERISK, "*"),
            (token.INT, "5"),
            (token.SEMICOLON, ";"),
            (token.INT, "5"),
            (token.LT, "<"),
            (token.INT, "10"),
            (token.GT, ">"),
            (token.INT, "5"),
            (token.SEMICOLON, ";"),
            (token.IF, "if"),
            (token.LPAREN, "("),
            (token.INT, "5"),
            (token.LT, "<"),
            (token.INT, "10"),
            (token.RPAREN, ")"),
            (token.LBRACE, "{"),
            (token.RETURN, "return"),
            (token.TRUE, "true"),
            (token.SEMICOLON, ";"),
            (token.RBRACE, "}"),
            (token.ELSE, "else"),
            (token.LBRACE, "{"),
            (token.RETURN, "return"),
            (token.FALSE, "false"),
            (token.SEMICOLON, ";"),
            (token.RBRACE, "}"),
            (token.INT, "10"),
            (token.EQ, "=="),
            (token.INT, "10"),
            (token.SEMICOLON, ";"),
            (token.INT, "10"),
            (token.NOT_EQ, "!="),
            (token.INT, "9"),
            (token.SEMICOLON, ";"),
            (token.STRING, "foobar"),
            (token.STRING, "foo bar"),
            (token.STRING, "foo\\bar"),
            (token.STRING, "foo\"bar"),
            (token.STRING, "hello\n world"),
            (token.LBRACKET, "["),
            (token.INT, "1"),
            (token.COMMA, ","),
            (token.INT, "2"),
            (token.RBRACKET, "]"),
            (token.SEMICOLON, ";"),
            (token.LBRACKET, "["),
            (token.RBRACKET, "]"),
            (token.SEMICOLON, ";"),
            (token.LBRACE, "{"),
            (token.STRING, "hello"),
            (token.COLON, ":"),
            (token.INT, "5"),
            (token.RBRACE, "}"),
            (token.SEMICOLON, ";"),
            (token.EOF, ""),
        ]
        for token_type, literal in expected:
            t = lex.next_token()
            self.assertEqual(t.token_type, token_type)
            self.assertEqual(t.literal, literal)


if __name__ == "__main__":
    main()
