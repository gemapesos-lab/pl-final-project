// toylang.js — ToyLang compiler pipeline implemented in JavaScript
// Ported from the Python reference implementation.

// ─── TOKEN TYPES ────────────────────────────────────────────────────────────
const TT = Object.freeze({
  VAR: 'VAR', INPUT: 'INPUT', OUTPUT: 'OUTPUT',
  IDENT: 'IDENT', INT: 'INT',
  PLUS: 'PLUS', MINUS: 'MINUS', STAR: 'STAR', SLASH: 'SLASH',
  EQUAL: 'EQUAL', LPAREN: 'LPAREN', RPAREN: 'RPAREN',
  SEMI: 'SEMI', EOF: 'EOF',
});

const KEYWORDS = { var: TT.VAR, input: TT.INPUT, output: TT.OUTPUT };

class Token {
  constructor(type, lexeme, line, col, value = null) {
    this.type = type; this.lexeme = lexeme;
    this.line = line; this.col = col; this.value = value;
  }
}

// ─── ERROR ───────────────────────────────────────────────────────────────────
class ToyError extends Error {
  constructor(phase, line, col, msg) {
    super(`${phase}: ${line}:${col}: ${msg}`);
    this.phase = phase; this.line = line; this.col = col; this.raw = msg;
  }
}

// ─── LEXER ────────────────────────────────────────────────────────────────────
class Lexer {
  constructor(source) {
    this.src = source; this.pos = 0; this.line = 1; this.col = 1;
  }

  fail(msg, line, col) {
    throw new ToyError('lexer', line ?? this.line, col ?? this.col, msg);
  }

  peek(off = 0) {
    const i = this.pos + off;
    return i < this.src.length ? this.src[i] : '\0';
  }

  advance() {
    const ch = this.src[this.pos++];
    if (ch === '\n') { this.line++; this.col = 1; } else { this.col++; }
    return ch;
  }

  isDigit(c) { return c >= '0' && c <= '9'; }
  isLetter(c) { return /[a-zA-Z_]/.test(c); }
  isAlnum(c)  { return /[a-zA-Z0-9_]/.test(c); }

  tokenize() {
    const toks = [];
    while (this.pos < this.src.length) {
      // skip whitespace
      while (this.pos < this.src.length && /\s/.test(this.peek())) this.advance();
      if (this.pos >= this.src.length) break;

      const line = this.line, col = this.col, ch = this.peek();

      // block comment
      if (ch === '/' && this.peek(1) === '*') {
        this.advance(); this.advance();
        let closed = false;
        while (this.pos < this.src.length) {
          if (this.peek() === '*' && this.peek(1) === '/') {
            this.advance(); this.advance(); closed = true; break;
          }
          this.advance();
        }
        if (!closed) this.fail('unterminated block comment', line, col);
        continue;
      }

      // integer literal
      if (this.isDigit(ch)) {
        let lex = '';
        while (this.pos < this.src.length && this.isDigit(this.peek())) lex += this.advance();
        if (this.pos < this.src.length && this.isLetter(this.peek()))
          this.fail('identifier cannot start with a digit');
        const v = Number(lex);
        if (!Number.isSafeInteger(v)) this.fail('integer literal too large', line, col);
        toks.push(new Token(TT.INT, lex, line, col, v));
        continue;
      }

      // identifier or keyword
      if (this.isLetter(ch)) {
        let lex = '';
        while (this.pos < this.src.length) {
          const c = this.peek();
          if (c.charCodeAt(0) >= 128) this.fail(`invalid character '${c}'`);
          if (!this.isAlnum(c)) break;
          lex += this.advance();
        }
        toks.push(new Token(KEYWORDS[lex] ?? TT.IDENT, lex, line, col));
        continue;
      }

      // non-ASCII
      if (ch.charCodeAt(0) >= 128) this.fail(`invalid character '${ch}'`);

      // single-char tokens
      const OPS = {
        '+': TT.PLUS, '-': TT.MINUS, '*': TT.STAR, '/': TT.SLASH,
        '=': TT.EQUAL, '(': TT.LPAREN, ')': TT.RPAREN, ';': TT.SEMI,
      };
      if (OPS[ch] !== undefined) {
        this.advance();
        toks.push(new Token(OPS[ch], ch, line, col));
        continue;
      }

      this.fail(`invalid character '${ch}'`);
    }
    toks.push(new Token(TT.EOF, '', this.line, this.col));
    return toks;
  }
}

// ─── PARSER ───────────────────────────────────────────────────────────────────
class Parser {
  constructor(tokens) { this.toks = tokens; this.pos = 0; }

  cur() { return this.toks[this.pos]; }

  expect(type, msg) {
    const t = this.cur();
    if (t.type !== type) throw new ToyError('parser', t.line, t.col, msg);
    return this.toks[this.pos++];
  }

  eat(type) {
    return this.cur().type === type ? this.toks[this.pos++] : null;
  }

  parse() {
    const stmts = [];
    while (this.cur().type !== TT.EOF) stmts.push(this.stmt());
    return { type: 'Program', stmts, line: 1, col: 1 };
  }

  stmt() {
    const t = this.cur();
    if (t.type === TT.VAR) {
      this.pos++;
      const id = this.expect(TT.IDENT, "expected identifier after 'var'");
      this.expect(TT.SEMI, "expected ';' after variable declaration");
      return { type: 'VarDecl', name: id.lexeme, line: t.line, col: t.col };
    }
    if (t.type === TT.INPUT) {
      this.pos++;
      const id = this.expect(TT.IDENT, "expected identifier after 'input'");
      this.expect(TT.SEMI, "expected ';' after input statement");
      return { type: 'InputStmt', name: id.lexeme, line: t.line, col: t.col };
    }
    if (t.type === TT.OUTPUT) {
      this.pos++;
      const id = this.expect(TT.IDENT, "expected identifier after 'output'");
      this.expect(TT.SEMI, "expected ';' after output statement");
      return { type: 'OutputStmt', name: id.lexeme, line: t.line, col: t.col };
    }
    if (t.type === TT.IDENT) {
      this.pos++;
      this.expect(TT.EQUAL, `expected '=' after '${t.lexeme}'`);
      const expr = this.expr();
      this.expect(TT.SEMI, "expected ';' after assignment");
      return { type: 'Assign', name: t.lexeme, expr, line: t.line, col: t.col };
    }
    throw new ToyError('parser', t.line, t.col, `unexpected token '${t.lexeme || t.type}'`);
  }

  expr() {
    let l = this.term();
    while (this.cur().type === TT.PLUS || this.cur().type === TT.MINUS) {
      const op = this.toks[this.pos++];
      const r = this.term();
      l = { type: 'BinaryExpr', op: op.lexeme, left: l, right: r, line: op.line, col: op.col };
    }
    return l;
  }

  term() {
    let l = this.unary();
    while (this.cur().type === TT.STAR || this.cur().type === TT.SLASH) {
      const op = this.toks[this.pos++];
      const r = this.unary();
      l = { type: 'BinaryExpr', op: op.lexeme, left: l, right: r, line: op.line, col: op.col };
    }
    return l;
  }

  unary() {
    if (this.cur().type === TT.MINUS) {
      const op = this.toks[this.pos++];
      return { type: 'UnaryExpr', op: '-', operand: this.unary(), line: op.line, col: op.col };
    }
    return this.primary();
  }

  primary() {
    const t = this.cur();
    if (t.type === TT.INT)    { this.pos++; return { type: 'IntLiteral', value: t.value, line: t.line, col: t.col }; }
    if (t.type === TT.IDENT)  { this.pos++; return { type: 'Identifier', name: t.lexeme, line: t.line, col: t.col }; }
    if (t.type === TT.LPAREN) {
      this.pos++;
      const e = this.expr();
      this.expect(TT.RPAREN, "expected ')' after expression");
      return e;
    }
    throw new ToyError('parser', t.line, t.col, `unexpected token '${t.lexeme || t.type}'`);
  }
}

// ─── SEMANTIC ANALYZER ────────────────────────────────────────────────────────
class SemanticAnalyzer {
  constructor(program) { this.prog = program; this.declared = new Set(); }

  analyze() { for (const s of this.prog.stmts) this.checkStmt(s); }

  checkStmt(s) {
    if (s.type === 'VarDecl') {
      if (this.declared.has(s.name))
        throw new ToyError('semantic', s.line, s.col, `duplicate declaration for '${s.name}'`);
      this.declared.add(s.name);
    } else if (s.type === 'Assign') {
      if (!this.declared.has(s.name))
        throw new ToyError('semantic', s.line, s.col, `variable '${s.name}' used before declaration`);
      this.checkExpr(s.expr);
    } else if (s.type === 'InputStmt' || s.type === 'OutputStmt') {
      if (!this.declared.has(s.name))
        throw new ToyError('semantic', s.line, s.col, `variable '${s.name}' used before declaration`);
    }
  }

  checkExpr(e) {
    if (e.type === 'Identifier') {
      if (!this.declared.has(e.name))
        throw new ToyError('semantic', e.line, e.col, `variable '${e.name}' used before declaration`);
    } else if (e.type === 'UnaryExpr') {
      this.checkExpr(e.operand);
    } else if (e.type === 'BinaryExpr') {
      this.checkExpr(e.left); this.checkExpr(e.right);
    }
  }
}

// ─── INTERPRETER ──────────────────────────────────────────────────────────────
class Interpreter {
  constructor(program, inputs = []) {
    this.prog = program; this.env = {};
    this.inputs = inputs; this.inputIdx = 0;
    this.outputs = []; this.inputLog = [];
  }

  run() {
    for (const s of this.prog.stmts) this.exec(s);
    return { outputs: this.outputs, inputLog: this.inputLog };
  }

  exec(s) {
    if (s.type === 'VarDecl') { this.env[s.name] = 0; }
    else if (s.type === 'Assign') { this.env[s.name] = this.eval(s.expr); }
    else if (s.type === 'InputStmt') {
      if (this.inputIdx >= this.inputs.length)
        throw new ToyError('runtime', s.line, s.col, 'unexpected end of input');
      const raw = String(this.inputs[this.inputIdx++]).trim();
      const v = parseInt(raw, 10);
      if (isNaN(v) || String(v) !== raw)
        throw new ToyError('runtime', s.line, s.col, `expected integer, got '${raw}'`);
      this.inputLog.push({ name: s.name, value: raw });
      this.env[s.name] = v;
    } else if (s.type === 'OutputStmt') {
      this.outputs.push(String(this.env[s.name]));
    }
  }

  eval(e) {
    if (e.type === 'IntLiteral') return e.value;
    if (e.type === 'Identifier') return this.env[e.name];
    if (e.type === 'UnaryExpr')  return -this.eval(e.operand);
    if (e.type === 'BinaryExpr') {
      const l = this.eval(e.left), r = this.eval(e.right);
      if (e.op === '+') return l + r;
      if (e.op === '-') return l - r;
      if (e.op === '*') return l * r;
      if (e.op === '/') {
        if (r === 0) throw new ToyError('runtime', e.line, e.col, 'division by zero');
        return Math.trunc(l / r);
      }
    }
  }
}

// ─── FORMATTERS ───────────────────────────────────────────────────────────────
function formatASTText(node, prefix = '', childPfx = '') {
  if (!node) return '';
  let label = '', children = [];
  switch (node.type) {
    case 'Program':    label = `Program  (${node.stmts.length} stmt${node.stmts.length !== 1 ? 's' : ''})`; children = node.stmts; break;
    case 'VarDecl':   label = `VarDecl    "${node.name}"`; break;
    case 'Assign':    label = `Assign     "${node.name}"`; children = [node.expr]; break;
    case 'InputStmt': label = `Input      "${node.name}"`; break;
    case 'OutputStmt':label = `Output     "${node.name}"`; break;
    case 'IntLiteral':label = `Int        ${node.value}`; break;
    case 'Identifier':label = `Ident      "${node.name}"`; break;
    case 'UnaryExpr': label = `Unary      (${node.op})`; children = [node.operand]; break;
    case 'BinaryExpr':label = `Binary     (${node.op})`; children = [node.left, node.right]; break;
    default:          label = node.type;
  }
  let out = prefix + label + '\n';
  for (let i = 0; i < children.length; i++) {
    const last = i === children.length - 1;
    out += formatASTText(children[i],
      childPfx + (last ? '└── ' : '├── '),
      childPfx + (last ? '    ' : '│   '));
  }
  return out;
}

// ─── PIPELINE ─────────────────────────────────────────────────────────────────
function runPipeline(source, inputs = []) {
  const result = {
    tokens: null, ast: null, semanticOk: false,
    outputs: [], inputLog: [], error: null,
  };
  try {
    result.tokens = new Lexer(source).tokenize();
  } catch (e) { result.error = e; return result; }

  try {
    result.ast = new Parser(result.tokens).parse();
  } catch (e) { result.error = e; return result; }

  try {
    new SemanticAnalyzer(result.ast).analyze();
    result.semanticOk = true;
  } catch (e) { result.error = e; return result; }

  try {
    const { outputs, inputLog } = new Interpreter(result.ast, inputs).run();
    result.outputs = outputs; result.inputLog = inputLog;
  } catch (e) { result.error = e; return result; }

  return result;
}
