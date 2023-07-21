import argparse
import os

from src.monkey import repl

TEXT = r"""
                              _
  _ __ ___     ___    _ __   | | __   ___
 | '_ ` _ \   / _ \  | '_ \  | |/ /  / _ \
 | | | | | | | (_) | | | | | |   <  |  __/
 |_| |_| |_|  \___/  |_| |_| |_|\_\  \___|
"""
ICON = r"""
                      ██████████████
                    ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓████
                  ████▓▓▓▓▓▓░░░░▓▓▓▓░░██
                ██▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░██
                ██▓▓▓▓▓▓░░░░░░██░░░░██░░██
                ██▓▓██▓▓░░░░░░██░░░░██░░██
                ██▓▓██▓▓░░██░░░░░░░░░░░░░░██
                  ██▓▓▓▓██░░░░░░░░░░░░░░░░░░██
      ██████        ██▓▓██░░░░░░░░████░░░░░░██
    ██▓▓▓▓▓▓██        ██░░████████░░░░██████
  ██▓▓▓▓▓▓▓▓▓▓██      ████░░░░░░░░░░░░░░██
  ██▓▓▓▓██▓▓▓▓██    ██▓▓▓▓██████████████
  ██▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██▓▓▓▓██
    ██▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓██▓▓▓▓██▓▓▓▓██
      ████████████▓▓▓▓▓▓▓▓▓▓██▓▓▓▓██▓▓▓▓██
                ██████████▓▓██░░░░░░██░░░░██
              ██░░░░░░░░░░██░░░░░░░░██░░░░██
              ██░░░░░░░░░░██░░░░░░██░░░░██
              ██████████████████████████
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["interp", "vm"],
        default="interp",
        help="Run interpreter 'interp', or virtual machine 'vm'",
    )
    args = parser.parse_args()

    if args.file is None:
        user = os.getlogin().capitalize()
        print(ICON)
        print(f"Hello {user}! This is the Monkey programming language!")
        print("Feel free to type in commands.")
        if args.mode != "interp":
            repl.start(mode=args.mode)
        else:
            repl.start()
    else:
        with open(args.file, "r") as f:
            repl.start(rin=f)
    return


if __name__ == "__main__":
    main()
