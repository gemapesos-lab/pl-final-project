from __future__ import annotations

from toy_lang.errors import LexError
from toy_lang.tokens import KEYWORDS, Token, TokenType


SINGLE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "=": TokenType.EQUAL,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ";": TokenType.SEMI,
}


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while not self.is_at_end():
            char = self.current_char()
            if char.isspace():
                self.skip_whitespace()
                continue
            if char == "/" and self.peek() == "*":
                self.skip_comment()
                continue
            if self.is_identifier_start(char):
                tokens.append(self.scan_identifier())
                continue
            if self.is_ascii_digit(char):
                tokens.append(self.scan_number())
                continue
            token_type = SINGLE_CHAR_TOKENS.get(char)
            if token_type is not None:
                line, column = self.line, self.column
                self.advance()
                tokens.append(Token(token_type, char, line, column))
                continue
            raise LexError(f"invalid character {char!r}", self.line, self.column)

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def is_at_end(self) -> bool:
        return self.index >= len(self.source)

    def current_char(self) -> str:
        return self.source[self.index]

    def peek(self, offset: int = 1) -> str:
        target = self.index + offset
        if target >= len(self.source):
            return "\0"
        return self.source[target]

    def advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def skip_whitespace(self) -> None:
        while not self.is_at_end() and self.current_char().isspace():
            self.advance()

    def skip_comment(self) -> None:
        start_line, start_column = self.line, self.column
        self.advance()
        self.advance()
        while not self.is_at_end():
            if self.current_char() == "*" and self.peek() == "/":
                self.advance()
                self.advance()
                return
            self.advance()
        raise LexError("unterminated block comment", start_line, start_column)

    def scan_identifier(self) -> Token:
        start = self.index
        line, column = self.line, self.column
        while not self.is_at_end():
            char = self.current_char()
            if self.is_identifier_part(char):
                self.advance()
                continue
            break
        lexeme = self.source[start:self.index]
        token_type = KEYWORDS.get(lexeme, TokenType.IDENT)
        return Token(token_type, lexeme, line, column)

    def scan_number(self) -> Token:
        start = self.index
        line, column = self.line, self.column
        while not self.is_at_end() and self.is_ascii_digit(self.current_char()):
            self.advance()
        if not self.is_at_end():
            next_char = self.current_char()
            if self.is_identifier_start(next_char):
                while not self.is_at_end():
                    char = self.current_char()
                    if self.is_identifier_part(char):
                        self.advance()
                        continue
                    break
                lexeme = self.source[start:self.index]
                raise LexError(
                    f"identifier cannot start with a digit: {lexeme!r}",
                    line,
                    column,
                )
        lexeme = self.source[start:self.index]
        return Token(TokenType.INT, lexeme, line, column, value=int(lexeme))

    def is_ascii_digit(self, char: str) -> bool:
        return "0" <= char <= "9"

    def is_ascii_letter(self, char: str) -> bool:
        return ("a" <= char <= "z") or ("A" <= char <= "Z")

    def is_identifier_start(self, char: str) -> bool:
        return char == "_" or self.is_ascii_letter(char)

    def is_identifier_part(self, char: str) -> bool:
        return self.is_identifier_start(char) or self.is_ascii_digit(char)
