from dataclasses import dataclass
from typing import Final, NewType


TokenType = NewType('TokenType', str)


ILLEGAL:   Final[TokenType] = "ILLEGAL"
EOF:       Final[TokenType] = "EOF"
IDENT:     Final[TokenType] = "INDENT"
INT:       Final[TokenType] = "INT"
STRING:    Final[TokenType] = "STRING"
ASSIGN:    Final[TokenType] = "="
PLUS:      Final[TokenType] = "+"
MINUS:     Final[TokenType] = "-"
BANG:      Final[TokenType] = "!"
ASTERISK:  Final[TokenType] = "*"
SLASH:     Final[TokenType] = "/"
LT:        Final[TokenType] = "<"
GT:        Final[TokenType] = ">"
EQ:        Final[TokenType] = "=="
NOT_EQ:    Final[TokenType] = "!="
COMMA:     Final[TokenType] = ","
SEMICOLON: Final[TokenType] = ";"
LPAREN:    Final[TokenType] = "("
RPAREN:    Final[TokenType] = ")"
LBRACE:    Final[TokenType] = "{"
RBRACE:    Final[TokenType] = "}"
FUNCTION:  Final[TokenType] = "FUNCTION"
LET:       Final[TokenType] = "LET"
TRUE:      Final[TokenType] = "TRUE"
FALSE:     Final[TokenType] = "FALSE"
IF:        Final[TokenType] = "IF"
ELSE:      Final[TokenType] = "ELSE"
RETURN:    Final[TokenType] = "RETURN"


KEYWORDS: Final[dict[TokenType]] = {
    "fn": FUNCTION,
    "let": LET,
    "true": TRUE,
    "false": FALSE,
    "if": IF,
    "else": ELSE,
    "return": RETURN
}


@dataclass
class Token:
    token_type: TokenType
    literal: str


def lookup_ident(ident: str) -> TokenType:
    if ident in KEYWORDS.keys():
        return KEYWORDS[ident]
    else:
        return IDENT
