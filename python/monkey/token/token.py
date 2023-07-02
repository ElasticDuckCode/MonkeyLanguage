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
ASSIGN:    Final[TokenType] = "ASSIGN"
PLUS:      Final[TokenType] = "PLUS"
COMMA:     Final[TokenType] = "COMMA"
SEMICOLON: Final[TokenType] = "SEMICOLON"
LPAREN:    Final[TokenType] = "LPAREN"
RPAREN:    Final[TokenType] = "RPAREN"
LBRACE:    Final[TokenType] = "LBRACE"
RBRACE:    Final[TokenType] = "RBRACE"
FUNCTION:  Final[TokenType] = "FUNCTION"
LET:       Final[TokenType] = "LET"
