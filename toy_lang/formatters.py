from __future__ import annotations

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
from toy_lang.tokens import Token, TokenType


def format_tokens(tokens: list[Token]) -> str:
    lines = []
    for token in tokens:
        lexeme = token.lexeme if token.type is not TokenType.EOF else "<EOF>"
        lines.append(f"{token.type.name} {lexeme!r} @ {token.line}:{token.column}")
    return "\n".join(lines)


def format_ast(program: Program) -> str:
    lines: list[str] = []
    render_node(program, lines, 0)
    return "\n".join(lines)


def render_node(node, lines: list[str], depth: int) -> None:
    indent = "  " * depth
    match node:
        case Program(statements=statements):
            lines.append(f"{indent}Program")
            for statement in statements:
                render_node(statement, lines, depth + 1)
        case VarDecl(name=name):
            lines.append(f"{indent}VarDecl {name.name}")
        case Assign(name=name, expression=expression):
            lines.append(f"{indent}Assign {name.name}")
            render_node(expression, lines, depth + 1)
        case InputStmt(name=name):
            lines.append(f"{indent}Input {name.name}")
        case OutputStmt(name=name):
            lines.append(f"{indent}Output {name.name}")
        case BinaryExpr(left=left, operator=operator, right=right):
            lines.append(f"{indent}BinaryExpr {operator}")
            render_node(left, lines, depth + 1)
            render_node(right, lines, depth + 1)
        case UnaryExpr(operator=operator, operand=operand):
            lines.append(f"{indent}UnaryExpr {operator}")
            render_node(operand, lines, depth + 1)
        case IntLiteral(value=value):
            lines.append(f"{indent}IntLiteral {value}")
        case Identifier(name=name):
            lines.append(f"{indent}Identifier {name}")
        case _:
            raise AssertionError(f"unknown node type: {node!r}")
