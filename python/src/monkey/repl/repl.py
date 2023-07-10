from typing import Final, TextIO
import os
import sys

from ..lexer import lexer
from ..parser import parser
from ..eval import eval
from ..obj import env

PROMPT: Final[str] = "monke >> "


def log_error(msg: str, details: str, f):
    print(f"Oops! {msg}:", file=f)
    if details != "":
        print(details, file=f)
    print("For encouragement, please see: " +
          "https://shorturl.at/fgBU4", file=f)
    return


def start(rin: TextIO = sys.stdin, rout: TextIO = sys.stdout) -> None:
    e = env.Environment()

    if rin == sys.stdin:
        print(PROMPT, end="", flush=True, file=rout)
        user_input = rin.readline()

        while user_input:
            if user_input.strip() == "exit":
                break
            elif user_input.strip() == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                lex = lexer.Lexer(user_input)
                par = parser.Parser(lex)
                program = par.parse_program()

                if len(par.errors):
                    log_error("Parsing Error!", par.error_str + "\n:(", rout)
                else:
                    evaluated = eval.eval(program, e)
                    if evaluated is not None:
                        print("[Output] " + evaluated.inspect + "\n", file=rout)

            print(PROMPT, end="", flush=True, file=rout)
            user_input = rin.readline()
    else:
        code = "".join(rin.readlines())
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()

        if len(par.errors):
            log_error("Parsing Error!", par.error_str + "\n:(", rout)
        else:
            evaluated = eval.eval(program, e)
            if evaluated is not None:
                print(evaluated.inspect, file=rout)
