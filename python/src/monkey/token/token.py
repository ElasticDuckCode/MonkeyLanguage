from dataclasses import dataclass
from typing import Final, NewType


TokenType = NewType('TokenType', str)


ILLEGAL:   Final[TokenType] = TokenType("ILLEGAL")
EOF:       Final[TokenType] = TokenType("EOF")
IDENT:     Final[TokenType] = TokenType("INDENT")
INT:       Final[TokenType] = TokenType("INT")
STRING:    Final[TokenType] = TokenType("STRING")
ASSIGN:    Final[TokenType] = TokenType("=")
PLUS:      Final[TokenType] = TokenType("+")
MINUS:     Final[TokenType] = TokenType("-")
BANG:      Final[TokenType] = TokenType("!")
ASTERISK:  Final[TokenType] = TokenType("*")
SLASH:     Final[TokenType] = TokenType("/")
LT:        Final[TokenType] = TokenType("<")
GT:        Final[TokenType] = TokenType(">")
EQ:        Final[TokenType] = TokenType("==")
NOT_EQ:    Final[TokenType] = TokenType("!=")
COMMA:     Final[TokenType] = TokenType(",")
SEMICOLON: Final[TokenType] = TokenType(";")
COLON:     Final[TokenType] = TokenType(":")
LPAREN:    Final[TokenType] = TokenType("(")
RPAREN:    Final[TokenType] = TokenType(")")
LBRACE:    Final[TokenType] = TokenType("{")
RBRACE:    Final[TokenType] = TokenType("}")
LBRACKET:  Final[TokenType] = TokenType("[")
RBRACKET:  Final[TokenType] = TokenType("]")
FUNCTION:  Final[TokenType] = TokenType("FUNCTION")
LET:       Final[TokenType] = TokenType("LET")
TRUE:      Final[TokenType] = TokenType("TRUE")
FALSE:     Final[TokenType] = TokenType("FALSE")
IF:        Final[TokenType] = TokenType("IF")
ELSE:      Final[TokenType] = TokenType("ELSE")
RETURN:    Final[TokenType] = TokenType("RETURN")


KEYWORDS: Final[dict[str, TokenType]] = {
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
