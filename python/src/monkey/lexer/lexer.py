from dataclasses import dataclass


@dataclass
class Lexer:
    input: str = ""
    position: int = 0
    read_position: int = 0
    ch: bytes = ""


def new(input: str):
    return Lexer(input)
