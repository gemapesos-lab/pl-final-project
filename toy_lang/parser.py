from __future__ import annotations

from toy_lang.errors import ParseError
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
from toy_lang.tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse(self) -> Program:
        statements: list[Statement] = []
        while not self.check(TokenType.EOF):
            statements.append(self.parse_statement())
        eof = self.current()
        return Program(statements=statements, line=eof.line, column=eof.column)

    def parse_statement(self) -> Statement:
        if self.match(TokenType.VAR):
            keyword = self.previous()
            name = self.parse_required_identifier("var")
            self.expect(TokenType.SEMI, "expected ';' after variable declaration")
            return VarDecl(
                name=name,
                line=keyword.line,
                column=keyword.column,
            )
        if self.match(TokenType.INPUT):
            keyword = self.previous()
            name = self.parse_required_identifier("input")
            self.expect(TokenType.SEMI, "expected ';' after input statement")
            return InputStmt(
                name=name,
                line=keyword.line,
                column=keyword.column,
            )
        if self.match(TokenType.OUTPUT):
            keyword = self.previous()
            name = self.parse_required_identifier("output")
            self.expect(TokenType.SEMI, "expected ';' after output statement")
            return OutputStmt(
                name=name,
                line=keyword.line,
                column=keyword.column,
            )
        if self.check(TokenType.IDENT):
            name_token = self.advance()
            self.expect(TokenType.EQUAL, "expected '=' after identifier")
            expression = self.parse_expression()
            self.expect(TokenType.SEMI, "expected ';' after assignment")
            return Assign(
                name=self.identifier_from_token(name_token),
                expression=expression,
                line=name_token.line,
                column=name_token.column,
            )
        token = self.current()
        raise ParseError(f"unexpected token {token.lexeme!r}", token.line, token.column)

    def parse_expression(self) -> Expression:
        expression = self.parse_term()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_term()
            expression = BinaryExpr(
                left=expression,
                operator=operator.lexeme,
                right=right,
                line=operator.line,
                column=operator.column,
            )
        return expression

    def parse_term(self) -> Expression:
        expression = self.parse_unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.parse_unary()
            expression = BinaryExpr(
                left=expression,
                operator=operator.lexeme,
                right=right,
                line=operator.line,
                column=operator.column,
            )
        return expression

    def parse_unary(self) -> Expression:
        if self.match(TokenType.MINUS):
            operator = self.previous()
            return UnaryExpr(
                operator=operator.lexeme,
                operand=self.parse_unary(),
                line=operator.line,
                column=operator.column,
            )
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        if self.match(TokenType.INT):
            token = self.previous()
            if token.value is None:
                raise AssertionError("integer token missing parsed value")
            return IntLiteral(token.value, token.line, token.column)
        if self.match(TokenType.IDENT):
            return self.identifier_from_token(self.previous())
        if self.match(TokenType.LPAREN):
            expression = self.parse_expression()
            self.expect(TokenType.RPAREN, "expected ')' after expression")
            return expression
        token = self.current()
        raise ParseError(f"unexpected token {token.lexeme!r}", token.line, token.column)

    def parse_required_identifier(self, keyword: str) -> Identifier:
        token = self.expect(TokenType.IDENT, f"expected identifier after '{keyword}'")
        return self.identifier_from_token(token)

    def identifier_from_token(self, token: Token) -> Identifier:
        return Identifier(token.lexeme, token.line, token.column)

    def match(self, *token_types: TokenType) -> bool:
        if self.check(*token_types):
            self.advance()
            return True
        return False

    def expect(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        token = self.current()
        raise ParseError(message, token.line, token.column)

    def check(self, *token_types: TokenType) -> bool:
        return self.current().type in token_types

    def advance(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def current(self) -> Token:
        return self.tokens[self.index]

    def previous(self) -> Token:
        return self.tokens[self.index - 1]
