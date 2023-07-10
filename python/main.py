import os
import argparse

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
    parser.add_argument('file', nargs='?')
    args = parser.parse_args()

    if args.file is None:
        user = os.getlogin().capitalize()
        print(ICON)
        print(f"Hello {user}! This is the Monkey programming language!")
        print("Feel free to type in commands.")
        repl.start()
    else:
        with open(args.file, "r") as f:
            repl.start(rin=f)
    return


if __name__ == "__main__":
    main()
