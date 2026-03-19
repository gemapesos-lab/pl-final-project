from __future__ import annotations

import unittest

from toy_lang.errors import RuntimeLangError
from toy_lang.interpreter import Interpreter
from toy_lang.lexer import Lexer
from toy_lang.nodes import Program
from toy_lang.parser import Parser
from toy_lang.semantic import SemanticAnalyzer


def build_program(source: str) -> Program:
    program = Parser(Lexer(source).tokenize()).parse()
    SemanticAnalyzer().analyze(program)
    return program


class InterpreterTests(unittest.TestCase):
    def test_declared_variables_default_to_zero(self) -> None:
        outputs: list[int] = []
        interpreter = Interpreter(output_fn=outputs.append)

        interpreter.run(build_program("var x; output x;"))

        self.assertEqual(outputs, [0])

    def test_executes_complex_expression_with_truncating_division(self) -> None:
        outputs: list[int] = []
        source = """
        var x;
        x = (3 - -2) * 4 / -3;
        output x;
        """
        interpreter = Interpreter(output_fn=outputs.append)

        interpreter.run(build_program(source))

        self.assertEqual(outputs, [-6])

    def test_rejects_non_integer_input(self) -> None:
        interpreter = Interpreter(input_fn=lambda prompt: "abc")

        with self.assertRaises(RuntimeLangError) as context:
            interpreter.run(build_program("var x; input x;"))

        self.assertEqual(
            str(context.exception),
            "runtime: 1:14: expected integer input for 'x'",
        )

    def test_rejects_unexpected_end_of_input(self) -> None:
        def eof_input(prompt: str) -> str:
            raise EOFError

        interpreter = Interpreter(input_fn=eof_input)

        with self.assertRaises(RuntimeLangError) as context:
            interpreter.run(build_program("var x; input x;"))

        self.assertEqual(
            str(context.exception),
            "runtime: 1:14: unexpected end of input",
        )

    def test_rejects_division_by_zero(self) -> None:
        interpreter = Interpreter()

        with self.assertRaises(RuntimeLangError) as context:
            interpreter.run(build_program("var x; x = 8 / 0;"))

        self.assertEqual(str(context.exception), "runtime: 1:14: division by zero")

    def test_reports_multiline_runtime_error_position(self) -> None:
        interpreter = Interpreter()
        source = "var x;\nvar y;\ny = 1;\nx = y / 0;"

        with self.assertRaises(RuntimeLangError) as context:
            interpreter.run(build_program(source))

        self.assertEqual(str(context.exception), "runtime: 4:7: division by zero")


if __name__ == "__main__":
    unittest.main()
