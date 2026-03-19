from __future__ import annotations

from collections.abc import Callable

from toy_lang.errors import RuntimeLangError
from toy_lang.nodes import (
    Assign,
    BinaryExpr,
    Expression,
    Identifier,
    InputStmt,
    IntLiteral,
    OutputStmt,
    Program,
    Statement,
    UnaryExpr,
    VarDecl,
)


class Interpreter:
    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[int], None] = print,
    ) -> None:
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.environment: dict[str, int] = {}

    def run(self, program: Program) -> None:
        for statement in program.statements:
            self.execute(statement)

    def execute(self, statement: Statement) -> None:
        match statement:
            case VarDecl(name=name):
                self.environment[name.name] = 0
            case Assign(name=name, expression=expression):
                self.environment[name.name] = self.evaluate(expression)
            case InputStmt(name=name):
                self.environment[name.name] = self.read_integer(name)
            case OutputStmt(name=name):
                self.output_fn(self.lookup(name))
            case _:
                raise AssertionError(f"unknown statement type: {statement!r}")

    def read_integer(self, identifier: Identifier) -> int:
        try:
            raw_value = self.input_fn(f"{identifier.name} = ")
        except EOFError as exc:
            raise RuntimeLangError(
                "unexpected end of input",
                identifier.line,
                identifier.column,
            ) from exc
        try:
            return int(raw_value)
        except ValueError as exc:
            raise RuntimeLangError(
                f"expected integer input for {identifier.name!r}",
                identifier.line,
                identifier.column,
            ) from exc

    def evaluate(self, expression: Expression) -> int:
        match expression:
            case IntLiteral(value=value):
                return value
            case Identifier() as identifier:
                return self.lookup(identifier)
            case UnaryExpr(operator="-", operand=operand):
                return -self.evaluate(operand)
            case BinaryExpr(left=left, operator=operator, right=right, line=line, column=column):
                left_value = self.evaluate(left)
                right_value = self.evaluate(right)
                if operator == "+":
                    return left_value + right_value
                if operator == "-":
                    return left_value - right_value
                if operator == "*":
                    return left_value * right_value
                if operator == "/":
                    return self.divide(left_value, right_value, line, column)
                raise AssertionError(f"unknown operator: {operator}")
            case _:
                raise AssertionError(f"unknown expression type: {expression!r}")

    def lookup(self, identifier: Identifier) -> int:
        try:
            return self.environment[identifier.name]
        except KeyError as exc:
            raise RuntimeLangError(
                f"variable {identifier.name!r} is not available at runtime",
                identifier.line,
                identifier.column,
            ) from exc

    def divide(self, left: int, right: int, line: int, column: int) -> int:
        if right == 0:
            raise RuntimeLangError("division by zero", line, column)
        quotient = abs(left) // abs(right)
        if (left < 0) ^ (right < 0):
            return -quotient
        return quotient
