import os
import sys
from typing import Final, TextIO

from ..code import code
from ..compiler import compiler, symbols
from ..eval import eval
from ..lexer import lexer
from ..obj import env, obj
from ..parser import parser
from ..vm import vm

PROMPT: Final[str] = "monke >> "


def log_error(msg: str, details: str, f):
    print(f"Oops! {msg}:", file=f)
    if details != "":
        print(details, file=f)
    print("For encouragement, please see: " + "https://shorturl.at/fgBU4", file=f)
    return


def start(
    rin: TextIO = sys.stdin, mode: str = "interp", rout: TextIO = sys.stdout
) -> None:
    e = env.Environment()
    table = symbols.Table()
    constants: list[obj.Object] = []
    globals: list[obj.Object] = vm.build_new_globals()

    if rin == sys.stdin:
        print(PROMPT, end="", flush=True, file=rout)
        user_input = rin.readline()

        while user_input:
            if user_input.strip() == "exit":
                break
            elif user_input.strip() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
            else:
                lex = lexer.Lexer(user_input)
                par = parser.Parser(lex)
                program = par.parse_program()

                if len(par.errors):
                    log_error("Parsing Error!", par.error_str + "\n:(", rout)
                else:
                    if mode == "interp":
                        evaluated = eval.eval(program, e)
                        if evaluated is not None:
                            print("[Output] " + evaluated.inspect + "\n", file=rout)
                    elif mode == "vm":
                        comp = compiler.Compiler(constants, table)
                        comp.compile(program)
                        if len(comp.errors):
                            log_error(
                                "Failed to Compile!", comp.error_str + "\n:(", rout
                            )
                        else:
                            machine = vm.VirtualMachine(comp.bytecode, globals)
                            machine.run()
                            if len(machine.errors):
                                log_error("VM Error!", machine.error_str + "\n:(", rout)
                            elif machine.last_popped:
                                print(
                                    "[Output]: " + machine.last_popped.inspect + "\n",
                                    file=rout,
                                )
                    else:
                        print(f"unsupported mode: {mode}", file=rout)

            print(PROMPT, end="", flush=True, file=rout)
            user_input = rin.readline()
    else:
        src_code = "".join(rin.readlines())
        lex = lexer.Lexer(src_code)
        par = parser.Parser(lex)
        program = par.parse_program()
        _ = eval.eval(program, e)
