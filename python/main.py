import os

from src.monkey.repl import start


def main():
    user = os.getlogin().capitalize()
    print(f"Hello {user}! This is the Monkey programming language!")
    print("Feel free to type in commands.")
    start()
    return


if __name__ == "__main__":
    main()
