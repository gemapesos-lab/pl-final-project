from __future__ import annotations


class LangError(Exception):
    phase = "error"

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"{self.phase}: {self.line}:{self.column}: {self.message}"


class LexError(LangError):
    phase = "lexer"


class ParseError(LangError):
    phase = "parser"


class SemanticError(LangError):
    phase = "semantic"


class RuntimeLangError(LangError):
    phase = "runtime"
