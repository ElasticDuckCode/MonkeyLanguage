from dataclasses import dataclass

import src.monkey.ast as ast
import src.monkey.lexer as lexer
import src.monkey.token as token


@dataclass
class Parser:
    lex: lexer.Lexer
    curr_token: token.Token
    peek_token: token.Token

    def __init__(self) -> None:
        self.next_token()
        self.next_token()

    def next_token(self) -> None:
        self.curr_token = self.peek_token
        self.peek_token = self.lex.next_token()

    def parse_program(self) -> ast.Program:
        return None
