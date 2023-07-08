from typing import Final, TextIO
from src.monkey import token, lexer, parser
import sys
import os

PROMPT: Final[str] = ">> "


def start(rin: TextIO = sys.stdin, rout: TextIO = sys.stdout) -> None:

    print(PROMPT, end="", flush=True, file=rout)
    user_input = rin.readline()
    while True:
        if user_input.strip() == "exit":
            break
        elif user_input.strip() == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
        else:
            lex = lexer.Lexer(user_input)
            par = parser.Parser(lex)
            program = par.parse_program()

            if len(par.errors):
                print("Oops! Errors while parsing:")
                print(par.error_str + "\n", file=rout)
                print("For encouragement, please see: " +
                      "https://shorturl.at/fgBU4")
            else:
                print(program.string + "\n", file=rout)

        print(PROMPT, end="", flush=True, file=rout)
        user_input = rin.readline()
