from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    VAR = auto()
    INPUT = auto()
    OUTPUT = auto()
    IDENT = auto()
    INT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQUAL = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMI = auto()
    EOF = auto()


KEYWORDS = {
    "var": TokenType.VAR,
    "input": TokenType.INPUT,
    "output": TokenType.OUTPUT,
}


@dataclass(frozen=True, slots=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int
    value: int | None = None
