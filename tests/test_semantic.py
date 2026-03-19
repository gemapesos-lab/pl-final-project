from __future__ import annotations

import unittest

from toy_lang.errors import SemanticError
from toy_lang.lexer import Lexer
from toy_lang.parser import Parser
from toy_lang.semantic import SemanticAnalyzer


def analyze_source(source: str) -> None:
    program = Parser(Lexer(source).tokenize()).parse()
    SemanticAnalyzer().analyze(program)


class SemanticAnalyzerTests(unittest.TestCase):
    def test_rejects_duplicate_declaration(self) -> None:
        with self.assertRaises(SemanticError) as context:
            analyze_source("var x; var x;")

        self.assertEqual(str(context.exception), "semantic: 1:12: duplicate declaration for 'x'")

    def test_rejects_use_before_declaration_in_expression(self) -> None:
        with self.assertRaises(SemanticError) as context:
            analyze_source("var x; x = y + 1; var y;")

        self.assertEqual(
            str(context.exception),
            "semantic: 1:12: variable 'y' used before declaration",
        )

    def test_rejects_output_before_declaration(self) -> None:
        with self.assertRaises(SemanticError) as context:
            analyze_source("output x; var x;")

        self.assertEqual(
            str(context.exception),
            "semantic: 1:8: variable 'x' used before declaration",
        )

    def test_reports_multiline_semantic_error_position(self) -> None:
        with self.assertRaises(SemanticError) as context:
            analyze_source("var x;\noutput y;\nvar y;")

        self.assertEqual(
            str(context.exception),
            "semantic: 2:8: variable 'y' used before declaration",
        )


if __name__ == "__main__":
    unittest.main()
