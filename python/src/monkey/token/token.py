from dataclasses import dataclass
from typing import Final


class TokenType(str):
    pass


@dataclass
class Token:
    token_type: TokenType
    literal: str


# Define Constant TokenTypes
ILLEGAL:   Final[TokenType] = "ILLEGAL"
EOF:       Final[TokenType] = "EOF"
IDENT:     Final[TokenType] = "INDENT"
INT:       Final[TokenType] = "INT"
ASSIGN:    Final[TokenType] = "="
PLUS:      Final[TokenType] = "+"
COMMA:     Final[TokenType] = ","
SEMICOLON: Final[TokenType] = ";"
LPAREN:    Final[TokenType] = "("
RPAREN:    Final[TokenType] = ")"
LBRACE:    Final[TokenType] = "{"
RBRACE:    Final[TokenType] = "}"
FUNCTION:  Final[TokenType] = "FUNCTION"
LET:       Final[TokenType] = "LET"
