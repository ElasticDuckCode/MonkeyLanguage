from dataclasses import dataclass
from typing import List, Dict, Callable

from ..ast import ast
from ..lexer import lexer
from ..token import token


LOWEST, EQUALS, LESSGREATER, SUM, PRODUCT, PREFIX, CALL, INDEX = range(1, 9)
precidences = {
    token.EQ:       EQUALS,
    token.NOT_EQ:   EQUALS,
    token.LT:       LESSGREATER,
    token.GT:       LESSGREATER,
    token.PLUS:     SUM,
    token.MINUS:    SUM,
    token.SLASH:    PRODUCT,
    token.ASTERISK: PRODUCT,
    token.LPAREN:   CALL,
    token.LBRACKET: INDEX
}


@dataclass
class Parser:
    lex: lexer.Lexer
    curr_token: token.Token = None
    peek_token: token.Token = None
    prefix_parse_fns:\
        Dict[
            token.TokenType,
            Callable[[], ast.Expression]
        ] = None
    infix_parse_fns:\
        Dict[
            token.TokenType,
            Callable[[ast.Expression], ast.Expression]
        ] = None
    _errors: List[str] = None

    def __post_init__(self) -> None:
        self.next_token()
        self.next_token()
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}
        self._errors = []

        self.register_prefix(token.INT, self.parse_integer_literal)
        self.register_prefix(token.STRING, self.parse_string_literal)
        self.register_prefix(token.TRUE, self.parse_boolean)
        self.register_prefix(token.FALSE, self.parse_boolean)
        self.register_prefix(token.IDENT, self.parse_identifier)
        self.register_prefix(token.BANG, self.parse_prefix_expression)
        self.register_prefix(token.MINUS, self.parse_prefix_expression)
        self.register_prefix(token.LPAREN, self.parse_group_expression)
        self.register_prefix(token.LBRACKET, self.parse_array_literal)
        self.register_prefix(token.LBRACE, self.parser_hash_literal)
        self.register_prefix(token.IF, self.parse_if_expression)
        self.register_prefix(token.FUNCTION, self.parse_function_literal)

        self.register_infix(token.PLUS, self.parse_infix_expression)
        self.register_infix(token.MINUS, self.parse_infix_expression)
        self.register_infix(token.SLASH, self.parse_infix_expression)
        self.register_infix(token.ASTERISK, self.parse_infix_expression)
        self.register_infix(token.EQ, self.parse_infix_expression)
        self.register_infix(token.NOT_EQ, self.parse_infix_expression)
        self.register_infix(token.LT, self.parse_infix_expression)
        self.register_infix(token.GT, self.parse_infix_expression)
        self.register_infix(token.LPAREN, self.parse_call_expression)
        self.register_infix(token.LBRACKET, self.parse_index_expression)

    @ property
    def errors(self):
        return self._errors

    @ property
    def error_str(self):
        return "\n".join(self._errors)

    def next_token(self) -> None:
        self.curr_token = self.peek_token
        self.peek_token = self.lex.next_token()

    def register_prefix(
        self,
        tt: token.TokenType,
        fn: Callable[[], ast.Expression]
    ) -> None:
        self.prefix_parse_fns[tt] = fn

    def register_infix(
        self,
        tt: token.TokenType,
        fn: Callable[[ast.Expression], ast.Expression]
    ) -> None:
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

        not_semicolon = not self.is_peek_token(token.SEMICOLON)
        peek_greater_precidence = precidence < self.peek_precidence

        while not_semicolon and peek_greater_precidence:
            self.next_token()
            if self.curr_token.token_type not in self.infix_parse_fns.keys():
                self.missing_infix_parse_fn_error(self.curr_token.token_type)
                return exp
            else:
                infix = self.infix_parse_fns[self.curr_token.token_type]
                exp = infix(exp)

            not_semicolon = not self.is_peek_token(token.SEMICOLON)
            peek_greater_precidence = precidence < self.peek_precidence

        return exp

    def parse_let_statement(self) -> ast.LetStatement:
        tok = self.curr_token

        if not self.expect_peek(token.IDENT):
            return None

        name = ast.Identifier(self.curr_token, self.curr_token.literal)

        if not self.expect_peek(token.ASSIGN):
            return None
        self.next_token()

        value = self.parse_expression(LOWEST)

        if self.is_peek_token(token.SEMICOLON):
            self.next_token()

        return ast.LetStatement(tok, name, value)

    def parse_return_statement(self) -> ast.ReturnStatement:
        tok = self.curr_token
        self.next_token()
        value = self.parse_expression(LOWEST)
        if self.is_peek_token(token.SEMICOLON):
            self.next_token()
        return ast.ReturnStatement(tok, value)

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(self.curr_token, self.curr_token.literal)

    def parse_integer_literal(self) -> ast.Expression:
        try:
            value = int(self.curr_token.literal)
            return ast.IntegerLiteral(self.curr_token, value)
        except ValueError:
            self.int_val_error()
            return None

    def parse_string_literal(self) -> ast.Expression:
        value = self.curr_token.literal
        return ast.StringLiteral(self.curr_token, value)

    def parse_boolean(self) -> ast.Expression:
        try:
            bool_map = {"true": True, "false": False}
            value = bool_map[self.curr_token.literal]
            return ast.Boolean(self.curr_token, value)
        except ValueError:
            self.bool_val_error()
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

    def parse_group_expression(self) -> ast.Expression:
        self.next_token()
        exp = self.parse_expression(LOWEST)
        if not self.expect_peek(token.RPAREN):
            return None
        return exp

    def parse_if_expression(self) -> ast.Expression:
        tok = self.curr_token
        if not self.expect_peek(token.LPAREN):
            return None
        self.next_token()
        condition = self.parse_expression(LOWEST)
        if not self.expect_peek(token.RPAREN):
            return None
        if not self.expect_peek(token.LBRACE):
            return None
        consequence = self.parse_block_statement()
        if self.is_peek_token(token.ELSE):
            self.next_token()
            if not self.expect_peek(token.LBRACE):
                return None
            alternative = self.parse_block_statement()
        else:
            alternative = None
        return ast.IfExpression(tok, condition, consequence, alternative)

    def parse_block_statement(self) -> ast.BlockStatement:
        tok = self.curr_token
        stmts = []
        self.next_token()

        not_rbrace = not self.is_curr_token(token.RBRACE)
        not_eof = not self.is_curr_token(token.EOF)

        while not_rbrace and not_eof:
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self.next_token()
            not_rbrace = not self.is_curr_token(token.RBRACE)
            not_eof = not self.is_curr_token(token.EOF)

        return ast.BlockStatement(tok, stmts)

    def parse_function_literal(self) -> ast.Expression:
        tok = self.curr_token
        if not self.expect_peek(token.LPAREN):
            return None
        params = self.parse_function_params()
        if not self.expect_peek(token.LBRACE):
            return None
        body = self.parse_block_statement()
        return ast.FunctionLiteral(tok, params, body)

    def parse_function_params(self) -> List[ast.Identifier]:
        idents = []

        if self.is_peek_token(token.RPAREN):
            self.next_token()
            return idents

        while True:
            self.next_token()
            ident = ast.Identifier(self.curr_token, self.curr_token.literal)
            idents.append(ident)
            if not self.is_peek_token(token.COMMA):
                break
            else:
                self.next_token()

        if not self.expect_peek(token.RPAREN):
            return None

        return idents

    def parse_expression_list(self, end: token.TokenType) -> ast.Expression:
        exps = []
        if self.is_peek_token(end):
            self.next_token()
            return exps
        while True:
            self.next_token()
            exps.append(self.parse_expression(LOWEST))
            if not self.is_peek_token(token.COMMA):
                break
            else:
                self.next_token()
        if not self.expect_peek(end):
            return None
        return exps

    def parse_call_expression(self, f: ast.Expression) -> ast.Expression:
        tok = self.curr_token
        args = self.parse_expression_list(token.RPAREN)
        return ast.CallExpression(tok, f, args)

    def parse_index_expression(self, left: ast.Expression) -> ast.Expression:
        tok = self.curr_token
        self.next_token()
        index = self.parse_expression(LOWEST)
        if not self.expect_peek(token.RBRACKET):
            return None
        return ast.IndexExpression(tok, left, index)

    def parse_array_literal(self) -> ast.Expression:
        tok = self.curr_token
        elements = self.parse_expression_list(token.RBRACKET)
        return ast.ArrayLiteral(tok, elements)

    def parser_hash_literal(self) -> ast.Expression:
        tok = self.curr_token
        pairs = dict()
        while not self.is_peek_token(token.RBRACE):
            self.next_token()
            key = self.parse_expression(LOWEST)
            if not self.expect_peek(token.COLON):
                return None
            self.next_token()
            value = self.parse_expression(LOWEST)
            pairs[key] = value
            if not self.is_peek_token(token.RBRACE):
                if not self.expect_peek(token.COMMA):
                    return None
        if not self.expect_peek(token.RBRACE):
            return None
        return ast.HashLiteral(tok, pairs)

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

    @ property
    def peek_precidence(self) -> int:
        ttype = self.peek_token.token_type
        if ttype in precidences.keys():
            return precidences[ttype]
        else:
            return LOWEST

    @ property
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

    def bool_val_error(self):
        msg = f"Could not parse {self.curr_token.literal} as boolean."
        self._errors.append(msg)

    def missing_prefix_parse_fn_error(self, t: token.TokenType):
        msg = f"Missing prefix parse function for {t} found."
        self._errors.append(msg)

    def missing_infix_parse_fn_error(self, t: token.TokenType):
        msg = f"Missing infix parse function for {t} found."
        self._errors.append(msg)
