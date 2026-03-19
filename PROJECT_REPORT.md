# Project Report

## Course Information

- Department: Computer Science
- Subject Code: CSTPLANGS
- Description: Translation of Programming Language
- Topic Coverage: Lessons 1-9
- Project: 1
- Activity: Project Presentation

## Submission Summary

This submission implements a small compiler front end and interpreter for the toy language in `Project Specification.md`. The project covers lexical analysis, syntax analysis, semantic analysis, and execution. The implementation is intentionally compact so each phase can be demonstrated clearly during presentation while still satisfying the required language rules.

## Objectives and Accomplishments

| Objective | Accomplishment |
| --- | --- |
| Build a lexer for the required language | `toy_lang/lexer.py` tokenizes keywords, identifiers, integers, operators, delimiters, whitespace, and block comments with line/column tracking. |
| Build a parser for the language grammar | `toy_lang/parser.py` constructs an AST with correct precedence for `+`, `-`, `*`, `/`, unary minus, and parentheses. |
| Enforce semantic correctness | `toy_lang/semantic.py` rejects duplicate declarations and variable use before declaration. |
| Execute valid programs correctly | `toy_lang/interpreter.py` evaluates integer expressions, handles input/output, defaults declared variables to `0`, and reports runtime errors clearly. |
| Provide a presentation-ready submission | `main.py`, `examples/`, `tests/`, this report, and `README.md` form a complete and runnable package. |

## Specification Compliance Matrix

| Specification Item | Implementation Evidence | Verification Evidence |
| --- | --- | --- |
| All statements end with a semicolon | The parser requires `;` after `var`, assignment, `input`, and `output` statements. | Parser tests reject missing semicolons; `examples/invalid_syntax.tl` demonstrates the failure case. |
| Whitespace is not significant | The lexer skips whitespace before scanning the next token. | Lexer tests cover comments and compact token sequences; valid examples execute with normal spacing and inline comments. |
| Comments use `/* ... */` and may span multiple lines | The lexer detects block comments and advances correctly across newlines. | `examples/multiline_comments.tl` demonstrates multi-line comments; automated example tests run it successfully. |
| Only `var`, `input`, and `output` are keywords | `toy_lang/tokens.py` defines exactly those keywords. | Token and parser tests validate keyword handling. |
| All variables are integers | Integer literals, integer input, integer arithmetic, and integer storage are enforced throughout the pipeline. | Interpreter tests cover arithmetic, invalid input, truncating division, and division by zero. |
| Allowed operators are `+`, `-`, `*`, `/`, and `=` with parentheses for grouping | The lexer and parser accept only those operators plus delimiters `(` and `)`. | Parser and interpreter tests verify precedence, grouping, and unary minus behavior. |
| Identifiers use letters, digits, and `_`, but cannot start with a digit | The lexer scans identifiers with ASCII letters, digits, and `_`, and rejects digit-prefixed identifiers. | Lexer tests reject `12abc` and non-ASCII names such as `café`. |
| Variables must be declared before use | The semantic analyzer checks assignments, expressions, input targets, and output targets against a symbol table. | Semantic tests reject undeclared use; `examples/invalid_semantic.tl` demonstrates the failure case. |

## Design and Implementation Notes

The project models a classic compiler pipeline:

1. Lexical analysis converts characters into tokens.
2. Recursive-descent parsing converts tokens into an AST.
3. Semantic analysis checks declaration correctness using a symbol table.
4. Interpretation executes the validated AST.

This structure matches the course focus on translation phases while keeping the code small enough for a live walkthrough during presentation.

## Experimental Results

The following commands were verified against the current submission:

| Case | Command | Result |
| --- | --- | --- |
| Basic arithmetic | `python3 main.py examples/basic.tl` | `14` |
| Inline and block comments | `python3 main.py examples/comments.tl` | `4` |
| Multi-line comments | `python3 main.py examples/multiline_comments.tl` | `8` |
| Precedence and unary minus | `python3 main.py examples/precedence.tl` | `13` |
| Input and output | `printf '7\n' \| python3 main.py examples/input_output.tl` | `number = 14` |
| Semantic-only validation | `python3 main.py examples/basic.tl --check-only` | `semantic: ok` |
| Automated regression suite | `python3 -m unittest discover -v` | all tests passed |

## Rubric Alignment

### Specifications

The project satisfies the required syntax rules, semantic checks, and execution behavior. Valid programs produce the expected results, and invalid programs fail with clear phase-specific diagnostics.

### Design

The command-line interface provides `--help`, token inspection, AST inspection, and semantic-only checking. Error messages identify the phase and source location, and source file read failures now use a clearer `io:` diagnostic.

### Efficiency

The implementation uses a single-pass lexer, a recursive-descent parser with explicit precedence levels, and a simple symbol table and environment map. The code remains small and direct without unnecessary indirection.

### Readability

The codebase is organized by compiler stage, uses dataclasses for syntax nodes and tokens, and keeps each module focused on one responsibility. Automated tests are separated by phase for easy inspection.

### Documentation

`README.md` explains the language, architecture, walkthrough, and verified results. This report adds a formal compliance matrix, rubric-focused summary, and experiment record suitable for submission and presentation.

## Files Included in the Submission

- `main.py`
- `toy_lang/`
- `examples/`
- `tests/`
- `README.md`
- `PROJECT_REPORT.md`
- `Project Specification.md`

## References

- Aho, A. V., Lam, M. S., Sethi, R., and Ullman, J. D. *Compilers: Principles, Techniques, and Tools* (2nd ed.).
- Python `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python `argparse`: https://docs.python.org/3/library/argparse.html
- Python built-in I/O functions: https://docs.python.org/3/library/functions.html
- Python `unittest`: https://docs.python.org/3/library/unittest.html
- LLVM frontend tutorial: https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html
