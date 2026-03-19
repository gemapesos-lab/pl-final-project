from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Program:
    statements: list["Statement"]
    line: int = 1
    column: int = 1


@dataclass(frozen=True, slots=True)
class Identifier:
    name: str
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class IntLiteral:
    value: int
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class UnaryExpr:
    operator: str
    operand: "Expression"
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class BinaryExpr:
    left: "Expression"
    operator: str
    right: "Expression"
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class VarDecl:
    name: Identifier
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class Assign:
    name: Identifier
    expression: "Expression"
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class InputStmt:
    name: Identifier
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class OutputStmt:
    name: Identifier
    line: int
    column: int


Expression = BinaryExpr | UnaryExpr | IntLiteral | Identifier
Statement = VarDecl | Assign | InputStmt | OutputStmt
