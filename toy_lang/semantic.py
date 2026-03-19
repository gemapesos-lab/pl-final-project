from __future__ import annotations

from toy_lang.errors import SemanticError
from toy_lang.nodes import (
    Assign,
    BinaryExpr,
    Identifier,
    InputStmt,
    IntLiteral,
    OutputStmt,
    Program,
    UnaryExpr,
    VarDecl,
)


class SemanticAnalyzer:
    def analyze(self, program: Program) -> None:
        declared: set[str] = set()
        for statement in program.statements:
            match statement:
                case VarDecl(name=name):
                    if name.name in declared:
                        raise SemanticError(
                            f"duplicate declaration for {name.name!r}",
                            name.line,
                            name.column,
                        )
                    declared.add(name.name)
                case Assign(name=name, expression=expression):
                    self.require_declared(name, declared)
                    self.analyze_expression(expression, declared)
                case InputStmt(name=name):
                    self.require_declared(name, declared)
                case OutputStmt(name=name):
                    self.require_declared(name, declared)
                case _:
                    raise AssertionError(f"unknown statement type: {statement!r}")

    def analyze_expression(self, expression, declared: set[str]) -> None:
        match expression:
            case Identifier() as identifier:
                self.require_declared(identifier, declared)
            case IntLiteral():
                return
            case UnaryExpr(operand=operand):
                self.analyze_expression(operand, declared)
            case BinaryExpr(left=left, right=right):
                self.analyze_expression(left, declared)
                self.analyze_expression(right, declared)
            case _:
                raise AssertionError(f"unknown expression type: {expression!r}")

    def require_declared(self, identifier: Identifier, declared: set[str]) -> None:
        if identifier.name not in declared:
            raise SemanticError(
                f"variable {identifier.name!r} used before declaration",
                identifier.line,
                identifier.column,
            )
