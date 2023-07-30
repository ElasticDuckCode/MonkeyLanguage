import time
import argparse
from src.monkey import ast, compiler, lexer, obj, parser, vm, code, env, eval


def main():
    aparser = argparse.ArgumentParser()
    aparser.add_argument(
        "-m",
        "--mode",
        choices=["interp", "vm"],
        default="interp",
        help="Run interpreter 'interp', or virtual machine 'vm'",
    )
    args = aparser.parse_args()

    script = """
    let fibonacci = fn(x) {
        if (x == 0) {
            return 0;
        }
        else {
            if (x == 1) {
                return 1;
            }
            else {
                return fibonacci(x - 1) + fibonacci(x - 2);
            }
        }
    }
    fibonacci(20);
    """
    engine = args.mode
    lex = lexer.Lexer(script)
    par = parser.Parser(lex)
    program = par.parse_program()

    if engine == "vm":
        comp = compiler.Compiler()
        comp.compile(program)
        if len(comp.errors):
            print("Failed to Compile! " + comp.error_str)
            return
        machine = vm.VirtualMachine(comp.bytecode)
        start = time.perf_counter()
        machine.run()
        end = time.perf_counter()
        result = machine.last_popped
        duration = end - start
    else:
        e = env.Environment()
        start = time.perf_counter()
        result = eval.eval(program, e)
        end = time.perf_counter()
        duration = end - start
    result = result.inspect
    print(f"{engine = }\n{result = }\n{duration = }")
    return


if __name__ == "__main__":
    main()
