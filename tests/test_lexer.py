from __future__ import annotations

import unittest

from toy_lang.errors import LexError
from toy_lang.lexer import Lexer
from toy_lang.tokens import TokenType


class LexerTests(unittest.TestCase):
    def test_skips_comments_and_whitespace(self) -> None:
        source = "var/* comment */x; output x; /**/"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            [token.type for token in tokens],
            [
                TokenType.VAR,
                TokenType.IDENT,
                TokenType.SEMI,
                TokenType.OUTPUT,
                TokenType.IDENT,
                TokenType.SEMI,
                TokenType.EOF,
            ],
        )
        self.assertEqual(tokens[1].lexeme, "x")
        self.assertEqual(tokens[4].lexeme, "x")

    def test_rejects_unterminated_comment(self) -> None:
        with self.assertRaises(LexError) as context:
            Lexer("var x; /* never closes").tokenize()

        self.assertEqual(str(context.exception), "lexer: 1:8: unterminated block comment")

    def test_rejects_identifier_starting_with_digit(self) -> None:
        with self.assertRaises(LexError) as context:
            Lexer("var x; x = 12abc;").tokenize()

        self.assertEqual(
            str(context.exception),
            "lexer: 1:12: identifier cannot start with a digit: '12abc'",
        )

    def test_rejects_non_ascii_identifier_characters(self) -> None:
        with self.assertRaises(LexError) as context:
            Lexer("var café;").tokenize()

        self.assertEqual(str(context.exception), "lexer: 1:8: invalid character 'é'")


if __name__ == "__main__":
    unittest.main()
