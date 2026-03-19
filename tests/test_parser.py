from __future__ import annotations

import unittest

from toy_lang.errors import ParseError
from toy_lang.lexer import Lexer
from toy_lang.nodes import Assign, BinaryExpr, Program, UnaryExpr
from toy_lang.parser import Parser


def parse_program(source: str) -> Program:
    return Parser(Lexer(source).tokenize()).parse()


class ParserTests(unittest.TestCase):
    def test_parses_empty_program(self) -> None:
        program = parse_program("/**/")
        self.assertEqual(program.statements, [])

    def test_parses_double_negation_and_subtract_negative(self) -> None:
        program = parse_program("var x; x = 3 - -2; x = --5;")
        first_assign = program.statements[1]
        second_assign = program.statements[2]

        self.assertIsInstance(first_assign, Assign)
        self.assertIsInstance(first_assign.expression, BinaryExpr)
        self.assertIsInstance(first_assign.expression.right, UnaryExpr)

        self.assertIsInstance(second_assign, Assign)
        self.assertIsInstance(second_assign.expression, UnaryExpr)
        self.assertIsInstance(second_assign.expression.operand, UnaryExpr)

    def test_rejects_missing_semicolon(self) -> None:
        with self.assertRaises(ParseError) as context:
            parse_program("var x")

        self.assertEqual(str(context.exception), "parser: 1:6: expected ';' after variable declaration")

    def test_rejects_expression_in_output_statement(self) -> None:
        with self.assertRaises(ParseError) as context:
            parse_program("output 1 + 2;")

        self.assertEqual(
            str(context.exception),
            "parser: 1:8: expected identifier after 'output'",
        )

    def test_reports_multiline_parser_error_position(self) -> None:
        with self.assertRaises(ParseError) as context:
            parse_program("var x\noutput x;")

        self.assertEqual(
            str(context.exception),
            "parser: 2:1: expected ';' after variable declaration",
        )


if __name__ == "__main__":
    unittest.main()
