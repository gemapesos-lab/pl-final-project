// app.js — ToyLang Playground logic

// ─── EXAMPLES ────────────────────────────────────────────────────────────────
const EXAMPLES = {
  basic: {
    label: 'basic.tl',
    desc: 'Simple arithmetic with operator precedence',
    code: `var x;\nx = 2 + 3 * 4;\noutput x;`,
    stdin: '',
    ok: true,
  },
  comments: {
    label: 'comments.tl',
    desc: 'Block comments (including inline) and integer division',
    code: `/* Comments can appear before the program. */\nvar /* inline */ total;\ntotal = (8 + 4) / 3;\noutput total;`,
    stdin: '',
    ok: true,
  },
  multiline_comments: {
    label: 'multiline_comments.tl',
    desc: 'Block comments spanning multiple lines',
    code: `/*\n  Demonstrates that block comments can span multiple lines\n  without affecting tokenization or evaluation.\n*/\nvar total;\ntotal = (18 / 3) + 2;\noutput total;`,
    stdin: '',
    ok: true,
  },
  precedence: {
    label: 'precedence.tl',
    desc: 'Unary minus and nested operator precedence',
    code: `var x;\nx = 3 - -2 * (4 + 1);\noutput x;`,
    stdin: '',
    ok: true,
  },
  input_output: {
    label: 'input_output.tl',
    desc: 'Reads an integer from stdin, doubles it',
    code: `var number;\ninput number;\nnumber = number * 2;\noutput number;`,
    stdin: '7',
    ok: true,
  },
  invalid_identifier: {
    label: 'invalid_identifier.tl',
    desc: 'Lexer error: non-ASCII character in identifier',
    code: `var café;\noutput café;`,
    stdin: '',
    ok: false,
    phase: 'lexer',
  },
  invalid_semantic: {
    label: 'invalid_semantic.tl',
    desc: 'Semantic error: variable used before declaration',
    code: `output x;\nvar x;`,
    stdin: '',
    ok: false,
    phase: 'semantic',
  },
  invalid_syntax: {
    label: 'invalid_syntax.tl',
    desc: 'Parser error: missing semicolon after var declaration',
    code: `var x\noutput x;`,
    stdin: '',
    ok: false,
    phase: 'parser',
  },
};

// ─── TOKEN DISPLAY HELPERS ───────────────────────────────────────────────────
const TOKEN_CLASS = {
  VAR: 'tok-keyword', INPUT: 'tok-keyword', OUTPUT: 'tok-keyword',
  IDENT: 'tok-ident', INT: 'tok-int',
  PLUS: 'tok-op', MINUS: 'tok-op', STAR: 'tok-op', SLASH: 'tok-op',
  EQUAL: 'tok-eq',
  LPAREN: 'tok-delim', RPAREN: 'tok-delim', SEMI: 'tok-delim',
  EOF: 'tok-eof',
};

const TOKEN_DISPLAY = {
  VAR: 'var', INPUT: 'input', OUTPUT: 'output',
  IDENT: 'ident', INT: 'int',
  PLUS: 'plus', MINUS: 'minus', STAR: 'star', SLASH: 'slash',
  EQUAL: 'equal', LPAREN: 'lparen', RPAREN: 'rparen', SEMI: 'semi', EOF: 'eof',
};

// ─── SYNTAX HIGHLIGHT (for AST output coloring) ──────────────────────────────
function colorizeAST(text) {
  return text
    .replace(/^(Program.*)/gm, '<span class="ast-node-program">$1</span>')
    .replace(/\b(VarDecl|InputStmt|OutputStmt|Assign)\b/g, '<span class="ast-node-stmt">$1</span>')
    .replace(/\b(BinaryExpr|UnaryExpr)\b/g, '<span class="ast-node-expr">$1</span>')
    .replace(/\b(Int)\b/g, '<span class="ast-node-literal">$1</span>')
    .replace(/\b(Ident)\b/g, '<span class="ast-node-ident">$1</span>')
    .replace(/(─|│|└|├)/g, '<span class="ast-branch">$1</span>');
}

// ─── RENDER FUNCTIONS ────────────────────────────────────────────────────────
function renderTokens(tokens) {
  if (!tokens || tokens.length === 0) return emptyState('No tokens yet', 'Run your code to see the token stream');

  const rows = tokens.map(t => {
    const cls = TOKEN_CLASS[t.type] || 'tok-delim';
    const display = TOKEN_DISPLAY[t.type] || t.type.toLowerCase();
    const valueCell = t.value !== null
      ? `<td class="tok-value">${t.value}</td>`
      : `<td style="color:#ddd">—</td>`;
    return `<tr class="${t.type === 'EOF' ? 'eof-row' : ''}">
      <td><span class="tok-badge ${cls}">${display}</span></td>
      <td><span class="tok-lexeme">${escHtml(t.lexeme || 'ε')}</span></td>
      <td class="tok-loc">${t.line}:${t.col}</td>
      ${valueCell}
    </tr>`;
  }).join('');

  return `<table class="token-table">
    <thead><tr>
      <th>Type</th><th>Lexeme</th><th>Loc</th><th>Value</th>
    </tr></thead>
    <tbody>${rows}</tbody>
  </table>`;
}

function renderAST(ast) {
  if (!ast) return emptyState('No AST yet', 'Run your code to see the parse tree');
  const text = formatASTText(ast);
  return `<pre class="ast-pre">${colorizeAST(escHtml(text))}</pre>`;
}

function renderSemantic(result) {
  if (!result.tokens && !result.error) return emptyState('No result yet', 'Run your code to see semantic analysis');

  if (result.error && result.error.phase === 'semantic') {
    return renderError(result.error);
  }
  if (result.error && (result.error.phase === 'lexer' || result.error.phase === 'parser')) {
    return `<div class="callout callout-warn">
      <span class="callout-icon">⚠️</span>
      <div>Semantic analysis was <strong>not reached</strong> — the ${result.error.phase} phase failed first.<br>
      Fix the ${result.error.phase} error and run again.</div>
    </div>`;
  }
  if (result.semanticOk) {
    return `<div class="semantic-ok">
      <div class="semantic-ok-icon">✅</div>
      <div>
        <div class="semantic-ok-text">Semantic analysis passed</div>
        <div class="semantic-ok-sub">All variables declared before use · No duplicate declarations</div>
      </div>
    </div>`;
  }
  return emptyState('No result yet', 'Run your code to see semantic analysis');
}

function renderOutput(result) {
  if (!result.tokens && !result.error) return emptyState('No output yet', 'Run your code to see program output');

  if (result.error) {
    if (result.error.phase === 'runtime') return renderError(result.error);
    return `<div class="callout callout-warn">
      <span class="callout-icon">⚠️</span>
      <div>Program did not execute — ${result.error.phase} phase failed.<br>
      Fix the error and run again.</div>
    </div>`;
  }

  const lines = [];
  // Interleave input prompts and outputs in execution order isn't easily trackable,
  // so show inputs first then outputs
  for (const il of result.inputLog) {
    lines.push(`<div class="output-line-in"><span style="color:#64748B">stdin › </span><span style="color:#94a3b8">${escHtml(il.name)} = ${escHtml(il.value)}</span></div>`);
  }
  if (result.outputs.length === 0 && result.inputLog.length === 0) {
    return `<div class="output-terminal"><span style="color:#475569;font-style:italic">(program produced no output)</span></div>`;
  }
  for (const line of result.outputs) {
    lines.push(`<div class="output-line-out">${escHtml(line)}</div>`);
  }

  return `<div class="output-terminal">${lines.join('')}</div>`;
}

function renderError(err) {
  const phase = err.phase || 'error';
  return `<div class="error-block">
    <span class="error-phase-badge phase-${phase}">
      ${phaseIcon(phase)} ${phase} error
    </span>
    <div class="error-msg-box">${escHtml(err.message)}</div>
  </div>`;
}

function emptyState(text, sub) {
  return `<div class="empty-state">
    <div class="empty-state-icon">🧩</div>
    <div class="empty-state-text">${text}</div>
    <div class="empty-state-sub">${sub}</div>
  </div>`;
}

function phaseIcon(phase) {
  return { lexer: '🔤', parser: '🌳', semantic: '🔍', runtime: '⚡' }[phase] || '❌';
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── SYNTAX HIGHLIGHTER ─────────────────────────────────────────────────────
// Character-by-character pass so comments shield their contents from other rules.
function highlightCode(code) {
  function e(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  let out = '';
  let i = 0;

  while (i < code.length) {
    const ch = code[i];

    // Block comment  /* … */
    if (ch === '/' && code[i + 1] === '*') {
      let j = i + 2;
      while (j < code.length && !(code[j] === '*' && code[j + 1] === '/')) j++;
      if (j < code.length) j += 2;
      out += `<span class="hl-comment">${e(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }

    // Integer literal
    if (ch >= '0' && ch <= '9') {
      let j = i;
      while (j < code.length && code[j] >= '0' && code[j] <= '9') j++;
      out += `<span class="hl-number">${e(code.slice(i, j))}</span>`;
      i = j;
      continue;
    }

    // Identifier / keyword
    if (/[a-zA-Z_]/.test(ch)) {
      let j = i;
      while (j < code.length && /[a-zA-Z0-9_]/.test(code[j])) j++;
      const word = code.slice(i, j);
      const cls = ['var', 'input', 'output'].includes(word) ? 'hl-keyword' : 'hl-ident';
      out += `<span class="${cls}">${e(word)}</span>`;
      i = j;
      continue;
    }

    // Operators
    if ('+-*/='.includes(ch)) {
      out += `<span class="hl-op">${e(ch)}</span>`;
      i++; continue;
    }

    // Delimiters
    if ('();'.includes(ch)) {
      out += `<span class="hl-delim">${e(ch)}</span>`;
      i++; continue;
    }

    // Everything else (whitespace, newlines, unknown chars)
    out += e(ch);
    i++;
  }

  // Trailing newline keeps the pre height in sync with the textarea
  return out + '\n';
}

// ─── LINE NUMBERS ────────────────────────────────────────────────────────────
function updateLineNumbers(textarea, lineNumEl) {
  const n = textarea.value.split('\n').length;
  const nums = Array.from({ length: n }, (_, i) => i + 1).join('\n');
  lineNumEl.textContent = nums;
  lineNumEl.scrollTop = textarea.scrollTop;
}

// ─── TAB COUNTS ──────────────────────────────────────────────────────────────
function updateTabCounts(result) {
  const tokenCount = document.getElementById('token-count');
  const astCount   = document.getElementById('ast-count');

  if (tokenCount) {
    const n = result.tokens ? result.tokens.length : 0;
    tokenCount.textContent = n > 0 ? n : '';
    tokenCount.style.display = n > 0 ? '' : 'none';
  }
  if (astCount) {
    const n = result.ast ? result.ast.stmts.length : 0;
    astCount.textContent = n > 0 ? n : '';
    astCount.style.display = n > 0 ? '' : 'none';
  }
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const editor       = document.getElementById('code-editor');
  const hlLayer      = document.getElementById('highlight-layer');
  const lineNums     = document.getElementById('line-numbers');
  const stdinEl      = document.getElementById('stdin-input');
  const runBtn       = document.getElementById('run-btn');
  const clearBtn     = document.getElementById('clear-btn');
  const exampleSel   = document.getElementById('examples-dropdown');
  const exampleDesc  = document.getElementById('example-desc');
  const tabs         = document.querySelectorAll('.output-tab');
  const contents     = document.querySelectorAll('.output-content');
  const runDot       = document.getElementById('run-dot');

  function syncHighlight() {
    hlLayer.innerHTML = highlightCode(editor.value);
    hlLayer.scrollTop  = editor.scrollTop;
    hlLayer.scrollLeft = editor.scrollLeft;
  }

  let lastResult = {};
  let activeTab = 'tokens';

  // ── populate examples dropdown ──
  for (const [key, ex] of Object.entries(EXAMPLES)) {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = ex.label;
    exampleSel.appendChild(opt);
  }

  // ── load example ──
  function loadExample(key) {
    if (!key || key === 'custom') {
      if (exampleDesc) exampleDesc.innerHTML = '';
      return;
    }
    const ex = EXAMPLES[key];
    if (!ex) return;
    editor.value = ex.code;
    stdinEl.value = ex.stdin;
    updateLineNumbers(editor, lineNums);
    syncHighlight();
    if (exampleDesc) {
      const badge = ex.ok
        ? '<span class="example-badge badge-ok">✓ valid</span>'
        : `<span class="example-badge badge-error">✗ ${ex.phase} error</span>`;
      exampleDesc.innerHTML = `<span style="color:var(--muted);font-size:0.85rem">${escHtml(ex.desc)}</span> ${badge}`;
    }
  }

  exampleSel.addEventListener('change', () => loadExample(exampleSel.value));

  // ── line numbers + highlight sync ──
  editor.addEventListener('input', () => {
    updateLineNumbers(editor, lineNums);
    syncHighlight();
  });
  editor.addEventListener('scroll', () => {
    lineNums.scrollTop  = editor.scrollTop;
    hlLayer.scrollTop   = editor.scrollTop;
    hlLayer.scrollLeft  = editor.scrollLeft;
  });
  editor.addEventListener('keydown', e => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const s = editor.selectionStart, end = editor.selectionEnd;
      editor.value = editor.value.substring(0, s) + '  ' + editor.value.substring(end);
      editor.selectionStart = editor.selectionEnd = s + 2;
    }
  });
  updateLineNumbers(editor, lineNums);

  // ── tab switching ──
  function switchTab(tabName) {
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => { c.classList.remove('active'); c.classList.remove('anim'); });
    const targetTab = document.querySelector(`.output-tab[data-tab="${tabName}"]`);
    const targetContent = document.getElementById(`tab-${tabName}`);
    if (targetTab) targetTab.classList.add('active');
    if (targetContent) {
      targetContent.classList.add('active');
      // retrigger animation
      void targetContent.offsetWidth;
      targetContent.classList.add('anim');
    }
    activeTab = tabName;
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      switchTab(tab.dataset.tab);
      rerenderActiveTab();
    });
  });

  function rerenderActiveTab() {
    const el = document.getElementById(`tab-${activeTab}`);
    if (!el) return;
    if (activeTab === 'tokens')   el.innerHTML = renderTokens(lastResult.tokens);
    if (activeTab === 'ast')      el.innerHTML = renderAST(lastResult.ast);
    if (activeTab === 'semantic') el.innerHTML = renderSemantic(lastResult);
    if (activeTab === 'output')   el.innerHTML = renderOutput(lastResult);
  }

  // ── run pipeline ──
  function run() {
    const source = editor.value;
    const stdinLines = stdinEl.value.trim().split('\n').filter(l => l.trim() !== '');

    if (runDot) runDot.classList.add('running');
    runBtn.disabled = true;

    // small delay so the UI updates
    setTimeout(() => {
      lastResult = runPipeline(source, stdinLines);
      updateTabCounts(lastResult);

      // auto-switch to error tab
      if (lastResult.error) {
        const phase = lastResult.error.phase;
        const tabMap = { lexer: 'tokens', parser: 'ast', semantic: 'semantic', runtime: 'output' };
        const target = tabMap[phase];
        if (target) switchTab(target);
      }

      // render all tabs (lazy-ish: render all, but only active is visible)
      document.getElementById('tab-tokens').innerHTML   = renderTokens(lastResult.tokens);
      document.getElementById('tab-ast').innerHTML      = renderAST(lastResult.ast);
      document.getElementById('tab-semantic').innerHTML = renderSemantic(lastResult);
      document.getElementById('tab-output').innerHTML   = renderOutput(lastResult);

      if (runDot) runDot.classList.remove('running');
      runBtn.disabled = false;
    }, 30);
  }

  runBtn.addEventListener('click', run);

  // Ctrl/Cmd + Enter to run
  editor.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); }
  });

  // ── clear ──
  clearBtn.addEventListener('click', () => {
    editor.value = '';
    stdinEl.value = '';
    exampleSel.value = '';
    if (exampleDesc) exampleDesc.innerHTML = '';
    lastResult = {};
    updateLineNumbers(editor, lineNums);
    syncHighlight();
    document.getElementById('tab-tokens').innerHTML   = renderTokens(null);
    document.getElementById('tab-ast').innerHTML      = renderAST(null);
    document.getElementById('tab-semantic').innerHTML = renderSemantic({});
    document.getElementById('tab-output').innerHTML   = renderOutput({});
    updateTabCounts({});
  });

  // ── init empty state ──
  syncHighlight();
  document.getElementById('tab-tokens').innerHTML   = renderTokens(null);
  document.getElementById('tab-ast').innerHTML      = renderAST(null);
  document.getElementById('tab-semantic').innerHTML = renderSemantic({});
  document.getElementById('tab-output').innerHTML   = renderOutput({});
});
