from typing import Final, TextIO
from src.monkey import lexer, token
import sys

PROMPT: Final[str] = ">> "


def start(rin: TextIO = sys.stdin, rout: TextIO = sys.stdout):

    print(PROMPT, end="", flush=True, file=rout)
    user_input = rin.readline()
    while user_input:

        lex = lexer.Lexer(user_input)

        tok = lex.next_token()
        while tok.token_type != token.EOF:
            print(tok, file=rout)
            tok = lex.next_token()

        print(PROMPT, end="", flush=True, file=rout)
        user_input = rin.readline()
