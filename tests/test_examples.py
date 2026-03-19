from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


class ExampleProgramsTests(unittest.TestCase):
    def run_example(
        self,
        filename: str,
        *args: str,
        stdin: str = "",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "main.py", str(EXAMPLES / filename), *args],
            cwd=ROOT,
            input=stdin,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_examples_match_documented_outputs(self) -> None:
        cases = [
            ("basic.tl", "", "14"),
            ("comments.tl", "", "4"),
            ("multiline_comments.tl", "", "8"),
            ("precedence.tl", "", "13"),
            ("input_output.tl", "7\n", "number = 14"),
        ]

        for filename, stdin, expected_output in cases:
            with self.subTest(filename=filename):
                result = self.run_example(filename, stdin=stdin)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout.strip(), expected_output)
                self.assertEqual(result.stderr, "")

    def test_invalid_examples_report_expected_errors(self) -> None:
        cases = [
            ("invalid_identifier.tl", "lexer: 1:8: invalid character 'é'"),
            ("invalid_semantic.tl", "semantic: 1:8: variable 'x' used before declaration"),
            ("invalid_syntax.tl", "parser: 2:1: expected ';' after variable declaration"),
        ]

        for filename, expected_error in cases:
            with self.subTest(filename=filename):
                result = self.run_example(filename)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr.strip(), expected_error)

    def test_basic_example_semantics_succeeds_in_check_only_mode(self) -> None:
        result = self.run_example("basic.tl", "--check-only")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "semantic: ok")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
