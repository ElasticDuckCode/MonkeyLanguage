from dataclasses import dataclass
from src.monkey import token


@dataclass
class Lexer:
    input: str = ""
    position: int = 0
    read_position: int = 0
    ch: int = 0

    def __post_init__(self) -> None:
        self.read_char()

    def read_char(self) -> None:
        if self.read_position >= len(self.input):
            self.ch = 0
        else:
            self.ch = ord(self.input[self.read_position])
        self.position = self.read_position
        self.read_position += 1

    def next_token(self) -> token.Token:
        tok = None
        match self.ch.to_bytes(1):
            case b'=':
                tok = token.Token(token.ASSIGN, chr(self.ch))
            case b';':
                tok = token.Token(token.SEMICOLON, chr(self.ch))
            case b'(':
                tok = token.Token(token.LPAREN, chr(self.ch))
            case b')':
                tok = token.Token(token.RPAREN, chr(self.ch))
            case b',':
                tok = token.Token(token.COMMA, chr(self.ch))
            case b'+':
                tok = token.Token(token.PLUS, chr(self.ch))
            case b'{':
                tok = token.Token(token.LBRACE, chr(self.ch))
            case b'}':
                tok = token.Token(token.RBRACE, chr(self.ch))
            case b'\0':
                tok = token.Token(token.EOF, "")
            case _:
                if self.is_letter():
                    tok = token.Token(token.IDENT, self.read_identifier())
                else:
                    tok = token.Token(token.ILLEGAL, chr(self.ch))
        self.read_char()
        return tok

    def is_letter(self) -> bool:
        lower = ord('a') <= self.ch <= ord('z')
        upper = ord('A') <= self.ch <= ord('Z')
        under = ord('_') == self.ch
        return lower or upper or under

    def read_identifier(self) -> str:
        start = self.position
        while self.is_letter():
            self.read_char()
        return self.input[start:self.position]
