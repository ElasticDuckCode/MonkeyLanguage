from dataclasses import dataclass
from typing import List, Dict
from abc import ABC, abstractmethod

import src.monkey.ast as ast
import src.monkey.lexer as lexer
import src.monkey.token as token


LOWEST, EQUALS, LESSGREATER, SUM, PRODUCT, PREFIX, CALL = range(1, 8)
precidences = {
    token.EQ:       EQUALS,
    token.NOT_EQ:   EQUALS,
    token.LT:       LESSGREATER,
    token.GT:       LESSGREATER,
    token.PLUS:     SUM,
    token.MINUS:    SUM,
    token.SLASH:    PRODUCT,
    token.ASTERISK: PRODUCT
}


# TODO: Not sure the best way to do this...
class PrefixParseFn(ABC):
    @abstractmethod
    def __call__(self) -> ast.Expression: pass


class InfixParseFn(ABC):
    @abstractmethod
    def __call__(self, exp: ast.Expression) -> ast.Expression: pass


@dataclass
class Parser:
    lex: lexer.Lexer
    curr_token: token.Token = None
    peek_token: token.Token = None
    prefix_parse_fns: Dict[token.TokenType, PrefixParseFn] = None
    infix_parse_fns: Dict[token.TokenType, InfixParseFn] = None
    _errors: List[str] = None

    def __post_init__(self) -> None:
        self.next_token()
        self.next_token()
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}
        self._errors = []

        self.register_prefix(token.INT, self.parse_integer_literal)
        self.register_prefix(token.IDENT, self.parse_identifier)
        self.register_prefix(token.BANG, self.parse_prefix_expression)
        self.register_prefix(token.MINUS, self.parse_prefix_expression)
        self.register_infix(token.PLUS, self.parse_infix_expression)
        self.register_infix(token.MINUS, self.parse_infix_expression)
        self.register_infix(token.SLASH, self.parse_infix_expression)
        self.register_infix(token.ASTERISK, self.parse_infix_expression)
        self.register_infix(token.EQ, self.parse_infix_expression)
        self.register_infix(token.NOT_EQ, self.parse_infix_expression)
        self.register_infix(token.LT, self.parse_infix_expression)
        self.register_infix(token.GT, self.parse_infix_expression)

    @ property
    def errors(self):
        return self._errors

    def next_token(self) -> None:
        self.curr_token = self.peek_token
        self.peek_token = self.lex.next_token()

    def register_prefix(self, tt: token.TokenType, fn: PrefixParseFn) -> None:
        self.prefix_parse_fns[tt] = fn

    def register_infix(self, tt: token.TokenType, fn: PrefixParseFn) -> None:
        self.infix_parse_fns[tt] = fn

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
        elif self.curr_token.token_type == token.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        tok = self.curr_token
        expression = self.parse_expression(LOWEST)
        if self.is_peek_token(token.SEMICOLON):
            self.next_token()
        return ast.ExpressionStatement(tok, expression)

    def parse_expression(self, precidence: int) -> ast.Expression:
        if self.curr_token.token_type not in self.prefix_parse_fns.keys():
            self.missing_prefix_parse_fn_error(self.curr_token.token_type)
            return None
        else:
            prefix = self.prefix_parse_fns[self.curr_token.token_type]
            exp = prefix()

        while not self.is_peek_token(token.SEMICOLON) and (precidence < self.peek_precidence):
            self.next_token()
            if self.curr_token.token_type not in self.infix_parse_fns.keys():
                self.missing_infix_parse_fn_error(self.curr_token.token_type)
                return exp
            else:
                infix = self.infix_parse_fns[self.curr_token.token_type]
                exp = infix(exp)

        return exp

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

    def parse_return_statement(self) -> ast.ReturnStatement:
        tok = self.curr_token
        self.next_token()
        while not self.is_curr_token(token.SEMICOLON):
            self.next_token()
        return ast.ReturnStatement(tok)

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(self.curr_token, self.curr_token.literal)

    def parse_integer_literal(self) -> ast.Expression:
        try:
            value = int(self.curr_token.literal)
            return ast.IntegerLiteral(self.curr_token, value)
        except ValueError:
            self.int_val_error()
            return None

    def parse_prefix_expression(self) -> ast.Expression:
        tok = self.curr_token
        operator = self.curr_token.literal
        self.next_token()
        right = self.parse_expression(PREFIX)
        return ast.PrefixExpression(tok, operator, right)

    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        tok = self.curr_token
        operator = self.curr_token.literal
        precidence = self.curr_precidence
        self.next_token()
        right = self.parse_expression(precidence)
        return ast.InfixExpression(tok, left, operator, right)

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

    @property
    def peek_precidence(self) -> int:
        ttype = self.peek_token.token_type
        if ttype in precidences.keys():
            return precidences[ttype]
        else:
            return LOWEST

    @property
    def curr_precidence(self) -> int:
        ttype = self.curr_token.token_type
        if ttype in precidences.keys():
            return precidences[ttype]
        else:
            return LOWEST

    def peek_error(self, t: token.TokenType):
        msg = (f"Expected next token to be {t}, "
               f"not {self.peek_token.token_type}.")
        self._errors.append(msg)

    def int_val_error(self):
        msg = f"Could not parse {self.curr_token.literal} as integer."
        self._errors.append(msg)

    def missing_prefix_parse_fn_error(self, t: token.TokenType):
        msg = f"Missing prefix parse function for {t} found."
        self._errors.append(msg)

    def missing_infix_parse_fn_error(self, t: token.TokenType):
        msg = f"Missing infix parse function for {t} found."
        self._errors.append(msg)
