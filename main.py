#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from toy_lang.errors import LangError
from toy_lang.formatters import format_ast, format_tokens
from toy_lang.interpreter import Interpreter
from toy_lang.lexer import Lexer
from toy_lang.parser import Parser
from toy_lang.semantic import SemanticAnalyzer


def read_source_text(source_path: Path) -> str:
    try:
        return source_path.read_text(encoding="utf-8")
    except OSError as exc:
        reason = exc.strerror or str(exc)
        raise OSError(f"unable to read source file {source_path}: {reason}") from exc


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the toy-language front end and interpreter.",
        epilog=(
            "Examples:\n"
            "  ./main.py examples/basic.tl\n"
            "  ./main.py examples/basic.tl --tokens\n"
            "  ./main.py examples/basic.tl --check-only\n"
            "  python3 main.py examples/basic.tl"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("source", help="Path to the source file to analyze or execute.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--tokens",
        action="store_true",
        help="Print the token stream and stop after lexical analysis.",
    )
    mode_group.add_argument(
        "--ast",
        action="store_true",
        help="Print the parsed abstract syntax tree and stop after parsing.",
    )
    mode_group.add_argument(
        "--check-only",
        action="store_true",
        help="Run semantic analysis only and skip execution.",
    )
    return parser


def run_pipeline(args: argparse.Namespace) -> int:
    source_path = Path(args.source)
    source_text = read_source_text(source_path)

    tokens = Lexer(source_text).tokenize()
    if args.tokens:
        print(format_tokens(tokens))
        return 0

    program = Parser(tokens).parse()
    if args.ast:
        print(format_ast(program))
        return 0

    SemanticAnalyzer().analyze(program)
    if args.check_only:
        print("semantic: ok")
        return 0

    Interpreter().run(program)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        return run_pipeline(args)
    except LangError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"io: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
