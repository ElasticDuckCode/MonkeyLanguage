import os
import sys
from typing import Final, TextIO

from ..code import code
from ..compiler import compiler
from ..eval import eval
from ..lexer import lexer
from ..obj import env
from ..parser import parser
from ..vm import vm

PROMPT: Final[str] = "monke >> "


def log_error(msg: str, details: str, f):
    print(f"Oops! {msg}:", file=f)
    if details != "":
        print(details, file=f)
    print("For encouragement, please see: " + "https://shorturl.at/fgBU4", file=f)
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
                os.system("cls" if os.name == "nt" else "clear")
            else:
                lex = lexer.Lexer(user_input)
                par = parser.Parser(lex)
                program = par.parse_program()

                if len(par.errors):
                    log_error("Parsing Error!", par.error_str + "\n:(", rout)
                else:
                    # evaluated = eval.eval(program, e)
                    # if evaluated is not None:
                    #     print("[Output] " + evaluated.inspect + "\n", file=rout)
                    comp = compiler.Compiler()
                    try:
                        comp.compile(program)
                    except RuntimeError as exx:
                        log_error("Failed to Compile!", str(exx), rout)

                    insts = comp.bytecode.instructions
                    print(code.instructions_to_string(insts), file=rout)

                    machine = vm.VirtualMachine(comp.bytecode)
                    try:
                        machine.run()
                    except NotImplementedError as exx:
                        log_error("Failed to run Virtual Machine!", str(exx), rout)

                    if machine.last_popped:
                        print(
                            "[Last Popped]: " + machine.last_popped.inspect, file=rout
                        )
                        print("", file=rout)

            print(PROMPT, end="", flush=True, file=rout)
            user_input = rin.readline()
    else:
        src_code = "".join(rin.readlines())
        lex = lexer.Lexer(src_code)
        par = parser.Parser(lex)
        program = par.parse_program()
        _ = eval.eval(program, e)
