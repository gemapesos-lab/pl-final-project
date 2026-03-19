# Project Specification

## Course Information

- **Department:** Computer Science
- **Subject Code:** CSTPLANGS
- **Description:** Translation of Programming Language
- **Term/Academic Year:** 1st Term SY 2016-2017
- **Topic:** Lessons 1-9
- **Project:** 1
- **Project Activity:** Project Presentation
- **CLO:** 1, 2, 3

## Overview

A compiler translates (or compiles) a program written in a high-level programming language that is suitable for human programmers into the low-level machine language that is required by computers.

Compiler design covers basic translation mechanism and error detection and recovery. It includes lexical, syntax, and semantic analysis as the front end, and code generation and optimization as the back end.

A lexical analysis stage basically divides the input text into a list of “words.” This is the initial part of reading and analyzing the program text: the text is read and divided into tokens, each of which corresponds to a symbol in the programming language, such as a variable name, keyword, or number.

The next process is a syntax analysis stage that analyzes the way these words form structures and converts the text into a data structure that reflects the textual structure. For finding the structure of the input text, the syntax analysis must also reject invalid texts by reporting syntax errors. This phase takes the list of tokens produced by the lexical analysis and arranges them in a tree structure (called the syntax tree) that reflects the structure of the program. This phase is often called parsing.

## Syntax Rules

1. All statements will end in a semicolon.
2. Whitespace is not significant; for example, `a+b` is the same as `a + b`.
3. Comments begin with `/*` and end with `*/`, and they can extend across multiple lines.
4. The only keywords are `var`, `input`, and `output`. Their functions are as follows:
   - `var` declares a new variable. All variables must be declared before they are used.
   - `input` reads a variable from the console.
   - `output` displays the value of a variable on the console.
5. All variables are integers.
6. The only operations allowed are `+`, `-`, `*`, `/`, and `=`. Parentheses may be used to force operation ordering.
7. Variable names may only consist of uppercase and lowercase letters, underscores (`_`), and numbers. A variable name may not start with a number.

## Semantic Analysis and Project Directions

After syntax analysis, type checking is performed. This phase analyzes the syntax tree to determine whether the program violates certain consistency requirements, such as using a variable before it is declared or using a value in a context that does not make sense given the variable type.

### Project directions

- **Design:** Invent a language, or a language fragment, for some particular purpose or with some particular characteristic.
- **Modeling:** Try to formalize some interesting aspect of some existing language.
- Make sure that computations are sufficiently documented and supported by theories and literature.
- **Implementation:** Explore novel techniques for implementing a given language fragment.
- You may choose any programming language (for example: C, C++, Java, C#, Python, etc.).
- A copy of the software (executable and source code) needs to be submitted.

## Assessment Rubric

> Note: The following rubrics/metrics will be used to grade students’ output in the project.

### Specifications (40%)

- **Exceptional (31-40):** The project works and meets all of the specifications.
- **Acceptable (21-30):** The project works, produces the correct results, displays them correctly, and meets most of the other specifications.
- **Amateur (11-20):** The project produces correct results but does not display them correctly.
- **Unsatisfactory (1-10):** The project is producing incorrect results.

### Design (15%)

- **Exceptional (13-15):** The design is exceptionally attractive. The project is user-friendly with informative and consistent prompts and messages.
- **Acceptable (9-12):** The design is fairly attractive. The project is user-friendly with informative and consistent prompts and messages.
- **Amateur (5-8):** The design is fairly attractive. The project is not user-friendly but still provides informative and consistent prompts and messages.
- **Unsatisfactory (1-4):** The design is unattractive and not user-friendly.

### Efficiency (20%)

- **Exceptional (16-20):** The code is extremely efficient without sacrificing readability and understanding.
- **Acceptable (11-15):** The code is fairly efficient without sacrificing readability and understanding.
- **Amateur (6-10):** The code is brute force and unnecessarily long.
- **Unsatisfactory (1-5):** The code is huge and appears to be patched together.

### Readability (10%)

- **Exceptional (8-10):** The code is exceptionally well organized and very easy to follow.
- **Acceptable (5-7):** The code is fairly easy to read.
- **Amateur (3-4):** The code is readable only by someone who knows what it is supposed to be.
- **Unsatisfactory (1-2):** The code is poorly organized and very difficult to read.

### Documentation (15%)

- **Exceptional (13-15):** The team provides written documentation that clarifies their experimental results for that week. Objectives for the past week are clearly stated in relation to project goals, and the report is structured around their accomplishment.
- **Acceptable (9-12):** Written documentation is generally complete, but occasional omissions create some lack of clarity. Objectives for the past week are included with no relationship to project goals.
- **Amateur (5-8):** Written documentation is incomplete, with some lack of clarity. Objectives for the past week are included with no relationship to project goals.
- **Unsatisfactory (1-4):** There is no supporting written documentation.

**Total:** 100%
