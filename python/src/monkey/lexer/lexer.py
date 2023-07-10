from dataclasses import dataclass

from ..token import token


@dataclass
class Lexer:
    input: str = ""
    position: int = 0
    read_position: int = 0
    ch: int = 0

    def __post_init__(self) -> None:
        self.read_char()

    def is_letter(self) -> bool:
        lower = ord('a') <= self.ch <= ord('z')
        upper = ord('A') <= self.ch <= ord('Z')
        under = ord('_') == self.ch
        return lower or upper or under

    def is_number(self) -> bool:
        return ord('0') <= self.ch <= ord('9')

    def read_char(self) -> None:
        if self.read_position >= len(self.input):
            self.ch = 0
        else:
            self.ch = ord(self.input[self.read_position])
        self.position = self.read_position
        self.read_position += 1

    def peak_char(self) -> int:
        if self.read_position >= len(self.input):
            return 0
        else:
            return ord(self.input[self.read_position])

    def skip_whitespace(self) -> None:
        while chr(self.ch) in [' ', '\t', '\n', '\r']:
            self.read_char()

    def read_identifier(self) -> str:
        start = self.position
        while self.is_letter():
            self.read_char()
        return self.input[start:self.position]

    def read_number(self) -> str:
        start = self.position
        while self.is_number():
            self.read_char()
        return self.input[start:self.position]

    def read_string(self) -> str:
        start = self.position + 1
        esc = False
        esc_idx = []
        while True:
            self.read_char()
            if self.ch == 0:
                break
            if not esc:
                if self.ch == ord('"'):
                    break
                if self.ch == ord('\\'):
                    esc = True
                    esc_idx.append(self.position)
            else:
                esc = False
        # process escape chars using python decode
        bytestring = self.input[start:self.position].encode()
        return bytestring.decode("unicode_escape")

    def next_token(self) -> token.Token:
        tok = None
        self.skip_whitespace()
        match chr(self.ch):
            case '=':
                if chr(self.peak_char()) == '=':
                    ch = chr(self.ch)
                    self.read_char()
                    tok = token.Token(token.EQ, ch+chr(self.ch))
                else:
                    tok = token.Token(token.ASSIGN, chr(self.ch))
            case ';':
                tok = token.Token(token.SEMICOLON, chr(self.ch))
            case ':':
                tok = token.Token(token.COLON, chr(self.ch))
            case '(':
                tok = token.Token(token.LPAREN, chr(self.ch))
            case ')':
                tok = token.Token(token.RPAREN, chr(self.ch))
            case ',':
                tok = token.Token(token.COMMA, chr(self.ch))
            case '+':
                tok = token.Token(token.PLUS, chr(self.ch))
            case '-':
                tok = token.Token(token.MINUS, chr(self.ch))
            case '!':
                if chr(self.peak_char()) == '=':
                    ch = chr(self.ch)
                    self.read_char()
                    tok = token.Token(token.NOT_EQ, ch+chr(self.ch))
                else:
                    tok = token.Token(token.BANG, chr(self.ch))
            case '*':
                tok = token.Token(token.ASTERISK, chr(self.ch))
            case '/':
                tok = token.Token(token.SLASH, chr(self.ch))
            case '<':
                tok = token.Token(token.LT, chr(self.ch))
            case '>':
                tok = token.Token(token.GT, chr(self.ch))
            case '{':
                tok = token.Token(token.LBRACE, chr(self.ch))
            case '}':
                tok = token.Token(token.RBRACE, chr(self.ch))
            case '[':
                tok = token.Token(token.LBRACKET, chr(self.ch))
            case ']':
                tok = token.Token(token.RBRACKET, chr(self.ch))
            case '\0':
                tok = token.Token(token.EOF, "")
            case '"':
                tok = token.Token(token.STRING, self.read_string())
            case _:
                if self.is_letter():
                    ident = self.read_identifier()
                    tok = token.Token(token.lookup_ident(ident), ident)
                    return tok
                elif self.is_number():
                    number = self.read_number()
                    tok = token.Token(token.INT, number)
                    return tok
                else:
                    tok = token.Token(token.ILLEGAL, chr(self.ch))
        self.read_char()
        return tok
