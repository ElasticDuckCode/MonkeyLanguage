from dataclasses import dataclass, field
from typing import List

import src.monkey.ast as ast
import src.monkey.lexer as lexer
import src.monkey.token as token


@dataclass
class Parser:
    lex: lexer.Lexer
    curr_token: token.Token = None
    peek_token: token.Token = None
    _errors: List[str] = None

    def __post_init__(self) -> None:
        self.next_token()
        self.next_token()
        self._errors = []

    @property
    def errors(self):
        return self._errors

    def next_token(self) -> None:
        self.curr_token = self.peek_token
        self.peek_token = self.lex.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while not self.is_curr_token(token.EOF):
            statement = self.parse_statement()
            if statement is not None:
                program.statements.append(statement)
            self.next_token()

        return program

    def parse_statement(self) -> ast.Statement:
        if self.curr_token.token_type == token.LET:
            return self.parse_let_statement()
        else:
            return None

    def parse_let_statement(self) -> ast.LetStatement:
        tok = self.curr_token

        if not self.expect_peek(token.IDENT):
            return None

        name = ast.Identifier(self.curr_token, self.curr_token.literal)

        if not self.expect_peek(token.ASSIGN):
            return None

        while not self.is_curr_token(token.SEMICOLON):
            self.next_token()

        return ast.LetStatement(tok, name)

    def is_curr_token(self, t: token.TokenType) -> bool:
        return self.curr_token.token_type == t

    def is_peek_token(self, t: token.TokenType) -> bool:
        return self.peek_token.token_type == t

    def expect_peek(self, t: token.TokenType) -> bool:
        """Advance only if token type matches expected.
        """
        if self.is_peek_token(t):
            self.next_token()
            return True
        else:
            self.peek_error(t)
            return False

    def peek_error(self, t: token.TokenType):
        msg = (f"Expected next token to be {t}, "
               f"not {self.peek_token.token_type}.")
        self._errors.append(msg)
