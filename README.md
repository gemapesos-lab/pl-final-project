# Python Toy-Language Front End and Interpreter

## Overview

This project implements a small compiler front end and interpreter for the toy language described in `Project Specification.md`. It covers:

- lexical analysis
- syntax analysis through an abstract syntax tree (AST)
- semantic analysis with declaration checks
- execution through AST interpretation

The implementation is intentionally small and predictable so each compiler stage can be demonstrated clearly during testing and presentation.

## Submission Contents

This submission includes:

- source code for the lexer, parser, semantic analyzer, interpreter, and CLI
- an executable script entrypoint in `main.py`
- automated tests in `tests/`
- sample source programs in `examples/`
- a formal submission report in `PROJECT_REPORT.md`
- this README

## Project Objectives

- Implement lexical analysis that converts source text into tokens while handling whitespace and block comments correctly.
- Implement syntax and semantic analysis that builds an AST and rejects invalid programs such as missing semicolons or use before declaration.
- Execute valid programs correctly with integer arithmetic, console input/output, and clear phase-based diagnostics.

These objectives directly match the project requirement to document the front-end stages and support the implementation with clear evidence.

For a rubric-oriented compliance summary, see `PROJECT_REPORT.md`.

## Language Rules

### Supported statements

- `var IDENT;`
- `IDENT = expr;`
- `input IDENT;`
- `output IDENT;`

### Expression grammar

```text
program    := statement* EOF
statement  := "var" IDENT ";"
           | IDENT "=" expr ";"
           | "input" IDENT ";"
           | "output" IDENT ";"
expr       := term (("+" | "-") term)*
term       := unary (("*" | "/") unary)*
unary      := "-" unary | primary
primary    := INT | IDENT | "(" expr ")"
```

### Token categories

- Keywords: `var`, `input`, `output`
- Identifiers: ASCII letters, digits, and `_`, but never starting with a digit
- Integers: decimal integer literals
- Operators: `+`, `-`, `*`, `/`, `=`
- Delimiters: `(`, `)`, `;`
- Comments: `/* ... */`

## Implementation Constraints

- Declared variables initialize to `0`.
- `output` accepts exactly one identifier, not an arbitrary expression.
- Each `var` statement declares exactly one variable.
- All variables store integers only.
- Empty programs are valid.
- Comments are block comments only and do not nest.
- Error handling is fail-fast by phase.
- Integer division truncates toward zero. For example, `(3 - -2) * 4 / -3` evaluates to `-6`.

These decisions keep the implementation simple, predictable, and easy to explain during presentation.

## Specification Compliance Snapshot

| Specification Item | Implementation Evidence | Verification Evidence |
| --- | --- | --- |
| Statements end with semicolons | The parser requires `;` after every supported statement form. | Parser tests and `examples/invalid_syntax.tl` verify missing-semicolon failures. |
| Whitespace is not significant | The lexer skips whitespace before scanning each token. | Lexer tests cover compact token streams and comments between tokens. |
| Comments use `/* ... */` and may span multiple lines | The lexer skips block comments and advances line/column positions across newlines. | `examples/multiline_comments.tl` and automated example tests validate the feature. |
| Variables must be declared before use | `toy_lang/semantic.py` checks assignments, expressions, input targets, and outputs against a declaration set. | Semantic tests and `examples/invalid_semantic.tl` verify the rule. |
| Variables are integers | Integer literals, input coercion, and arithmetic evaluation all operate on `int` values. | Interpreter tests cover arithmetic, invalid input, truncating division, and runtime errors. |
| Identifiers cannot start with digits | The lexer explicitly rejects digit-prefixed identifiers. | Lexer tests reject `12abc` and non-ASCII names such as `café`. |

## Theory and Literature Basis

The implementation follows standard compiler-construction ideas:

- lexical analysis scans characters into tokens with line and column tracking
- recursive-descent parsing applies a context-free grammar with explicit operator precedence
- the AST separates syntax structure from raw tokens
- semantic analysis uses a symbol table to detect duplicate declarations and use before declaration
- interpretation walks the AST to evaluate expressions and execute statements

This design is supported by classic compiler literature and by the Python and LLVM references listed at the end of this document.

## Architecture

### Pipeline

1. `toy_lang/lexer.py` converts source text into location-aware tokens.
2. `toy_lang/parser.py` builds an AST with recursive-descent parsing.
3. `toy_lang/semantic.py` checks duplicate declarations and use-before-declaration errors.
4. `toy_lang/interpreter.py` executes the AST using an integer environment map.
5. `main.py` provides the CLI and consistent diagnostics.

### Core AST node types

- `Program`
- `VarDecl`
- `Assign`
- `InputStmt`
- `OutputStmt`
- `BinaryExpr`
- `UnaryExpr`
- `IntLiteral`
- `Identifier`

## Stage Walkthrough

This walkthrough uses `examples/basic.tl`:

```text
var x;
x = 2 + 3 * 4;
output x;
```

### 1. Lexical analysis

The lexer reads characters and emits tokens such as:

- `VAR 'var'`
- `IDENT 'x'`
- `EQUAL '='`
- `INT '2'`
- `PLUS '+'`
- `INT '3'`
- `STAR '*'`
- `INT '4'`
- `SEMI ';'`

Whitespace is ignored, and each token records its source line and column.

### 2. Syntax analysis

The parser turns the token stream into an AST that preserves operator precedence:

```text
Program
  VarDecl x
  Assign x
    BinaryExpr +
      IntLiteral 2
      BinaryExpr *
        IntLiteral 3
        IntLiteral 4
  Output x
```

This structure makes it explicit that `3 * 4` is grouped before `2 + ...`.

### 3. Semantic analysis

The semantic analyzer checks rules that the parser cannot enforce on its own:

- `x` must be declared before use
- duplicate declarations are rejected
- identifiers inside expressions must already exist

For this example, semantic analysis succeeds because `x` is declared before assignment and output.

### 4. Interpretation

The interpreter executes each statement in order:

1. `var x;` creates `x` with default value `0`
2. `x = 2 + 3 * 4;` evaluates to `14` and stores it
3. `output x;` prints `14`

The final result is:

```text
14
```

## CLI Usage

### Run a program

```bash
./main.py examples/basic.tl
```

### Print tokens

```bash
./main.py examples/basic.tl --tokens
```

### Print the AST

```bash
./main.py examples/basic.tl --ast
```

### Check semantics only

```bash
./main.py examples/basic.tl --check-only
```

### Run the automated tests

```bash
python3 -m unittest discover -v
```

If executable permissions are unavailable in the submission environment, use `python3 main.py ...` instead.

## Sample Programs

- `examples/basic.tl`: arithmetic and output
- `examples/comments.tl`: block comments and precedence
- `examples/multiline_comments.tl`: multi-line block comments
- `examples/precedence.tl`: nested unary minus and parentheses
- `examples/input_output.tl`: console input and output
- `examples/invalid_identifier.tl`: lexer error for a non-ASCII identifier
- `examples/invalid_semantic.tl`: semantic error example
- `examples/invalid_syntax.tl`: parser error example

## Verified Results

| Case | Command | Expected | Actual |
| --- | --- | --- | --- |
| Basic execution | `./main.py examples/basic.tl` | `14` | `14` |
| Comment handling | `./main.py examples/comments.tl` | `4` | `4` |
| Multi-line comment handling | `./main.py examples/multiline_comments.tl` | `8` | `8` |
| Unary minus and precedence | `./main.py examples/precedence.tl` | `13` | `13` |
| Semantic-only mode | `./main.py examples/basic.tl --check-only` | `semantic: ok` | `semantic: ok` |
| Runtime input | `printf '7\n' \| ./main.py examples/input_output.tl` | `number = 14` | `number = 14` |
| Lexer failure | `./main.py examples/invalid_identifier.tl` | `lexer: 1:8: invalid character 'é'` | `lexer: 1:8: invalid character 'é'` |
| Semantic failure | `./main.py examples/invalid_semantic.tl` | `semantic: 1:8: variable 'x' used before declaration` | `semantic: 1:8: variable 'x' used before declaration` |
| Syntax failure | `./main.py examples/invalid_syntax.tl` | `parser: 2:1: expected ';' after variable declaration` | `parser: 2:1: expected ';' after variable declaration` |

## Test Coverage

The automated tests cover:

- empty programs
- empty comments and comments between tokens
- malformed identifiers such as `12abc` and non-ASCII names such as `café`
- missing semicolons, unexpected tokens, and unsupported `output` expressions
- duplicate declarations
- use before declaration in assignments, expressions, and `output`, including multi-line diagnostics
- default-zero behavior after declaration
- unary minus edge cases such as `--5` and `3 - -2`
- truncation toward zero for division
- division by zero, including multi-line diagnostics
- non-integer input and unexpected EOF during `input`
- CLI modes `--help`, `--tokens`, `--ast`, and `--check-only`
- missing-source-file CLI diagnostics
- end-to-end execution of every example program in `examples/`

## Objectives to Evidence

| Objective | Implementation Evidence | Verification Evidence |
| --- | --- | --- |
| Lexical analysis of the language | `toy_lang/lexer.py` handles keywords, identifiers, integers, operators, delimiters, whitespace, and block comments | `python3 -m unittest discover -v` includes lexer tests for comments, invalid characters, and malformed identifiers |
| Syntax and semantic analysis | `toy_lang/parser.py` builds the AST and `toy_lang/semantic.py` rejects duplicate declarations and use before declaration | Verified syntax and semantic failures are listed in the results table above |
| Correct execution of valid programs | `toy_lang/interpreter.py` executes assignments, input, output, precedence, unary minus, and integer division | `./main.py examples/basic.tl`, `./main.py examples/precedence.tl`, and `./main.py examples/input_output.tl` produce the expected outputs |
| User-friendly submission package | `main.py` is both source code and an executable script entrypoint with `--help` examples, while `PROJECT_REPORT.md` documents compliance and results | CLI tests verify help text, executable invocation, analysis modes, and missing-file diagnostics |

## Official References

- Aho, A. V., Lam, M. S., Sethi, R., and Ullman, J. D. *Compilers: Principles, Techniques, and Tools* (2nd ed.).
- Python `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python `argparse`: https://docs.python.org/3/library/argparse.html
- Python built-in I/O functions: https://docs.python.org/3/library/functions.html
- Python `unittest`: https://docs.python.org/3/library/unittest.html
- LLVM frontend tutorial: https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html
