from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class CliTests(unittest.TestCase):
    def run_cli(self, source: str, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "program.tl"
            source_path.write_text(textwrap.dedent(source), encoding="utf-8")
            return subprocess.run(
                [sys.executable, "main.py", str(source_path), *args],
                cwd=ROOT,
                input=stdin,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_help_includes_examples(self) -> None:
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Examples:", result.stdout)
        self.assertIn("./main.py examples/basic.tl --check-only", result.stdout)
        self.assertIn("python3 main.py examples/basic.tl", result.stdout)

    def test_script_is_executable(self) -> None:
        self.assertTrue(os.access(ROOT / "main.py", os.X_OK))

    def test_executable_entrypoint_runs(self) -> None:
        result = subprocess.run(
            [str(ROOT / "main.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Run the toy-language front end and interpreter.", result.stdout)

    def test_reports_missing_source_file(self) -> None:
        missing_path = ROOT / "examples" / "does_not_exist.tl"
        result = subprocess.run(
            [sys.executable, "main.py", str(missing_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("io: unable to read source file", result.stderr)
        self.assertIn("does_not_exist.tl", result.stderr)

    def test_tokens_mode(self) -> None:
        result = self.run_cli("var x; output x;", "--tokens")

        self.assertEqual(result.returncode, 0)
        self.assertIn("VAR 'var' @ 1:1", result.stdout)
        self.assertIn("EOF '<EOF>' @ 1:17", result.stdout)

    def test_ast_mode(self) -> None:
        result = self.run_cli("var x; x = 2 + 3 * 4; output x;", "--ast")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "\n".join(
                [
                    "Program",
                    "  VarDecl x",
                    "  Assign x",
                    "    BinaryExpr +",
                    "      IntLiteral 2",
                    "      BinaryExpr *",
                    "        IntLiteral 3",
                    "        IntLiteral 4",
                    "  Output x",
                ]
            ),
        )

    def test_check_only_mode(self) -> None:
        result = self.run_cli("var x; output x;", "--check-only")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "semantic: ok")

    def test_cli_reports_errors(self) -> None:
        result = self.run_cli("output x;")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "semantic: 1:8: variable 'x' used before declaration")

    def test_reports_non_utf8_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "binary.tl"
            source_path.write_bytes(b"\xff\xfe")
            result = subprocess.run(
                [sys.executable, "main.py", str(source_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("io: unable to read source file", result.stderr)

    def test_reports_deep_expression_nesting(self) -> None:
        source = "var x; x = " + " + ".join(["1"] * 2000) + ";"
        result = self.run_cli(source)

        self.assertEqual(result.returncode, 1)
        self.assertIn("expression nesting too deep", result.stderr)

    def test_cli_reports_lexer_errors(self) -> None:
        result = self.run_cli("var café;")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr.strip(), "lexer: 1:8: invalid character 'é'")


if __name__ == "__main__":
    unittest.main()
