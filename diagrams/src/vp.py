"""Reading the vp-vnp formalization and the facts of its paper at build time, and drawing a statement card.

Everything a poster says about the proof is derived here from the files: a checkout of anthropics/formal-math at
another commit than FM_COMMIT, a paper.pdf or a paper-facts.json that does not hash to its pin, a Lean name of the
paper's Table 3 that no file declares, or one declared twice, raises, so that the generator prints ERROR instead of
drawing something stale.

  load()                 the sources, after the commit and hash checks: a Source with
    .facts               diagrams/src/paper-facts.json: the paper's Table 1, Table 3, statement headers, Sections 1-2
    .modules             every Lean file of the folder: its module name, library, lines and imports
    .decls               every declaration at the head of a line: full name, kind, file, line, docstring, signature
    .statements          the numbered statements of Table 3, each joined to its Lean declarations
    .uses                statement -> the statements its Lean proofs name (read from the text, see below)
  lean_url(path, line)   the file and line in formal-math at FM_COMMIT
  node(canvas, ...)      a card: title, pill, Lean panel, the paper's words in italics, bullets, footer

How the Lean is read. Nothing is built or elaborated. Each file is read as text: comments and strings are blanked,
`namespace`/`section`/`end` give the full names, and a declaration runs from its keyword at the head of a line to the
next command at the head of a line. A statement uses another when the text of one of its declarations names one of
the other's Lean theorems, bare or as `Paper.<name>`, directly or through declarations of the Paper library that
belong to no statement. A name is matched as written: an `open`, a local variable of the same name, or a reference
made by a tactic without naming the theorem are not seen. The posters say so where they draw these edges.
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import tomllib
from xml.sax.saxutils import escape

import lib
from lib import MONO_EM, fill, fs, render_line, wrap

ROOT = pathlib.Path(__file__).resolve().parents[2]          # this repository
SRC = pathlib.Path(__file__).resolve().parent

# ------------------------------------------------------------------------------------------------ pins
# The commit of anthropics/formal-math every file is read from. The build fails if the checkout is at another; bump
# it after reading what changed (proof-posters:moving-pins). CI checks the repository out at exactly this.
FM_COMMIT = "11b6c7e3c9"
FM_REPO = "anthropics/formal-math"
FM_URL = f"https://github.com/{FM_REPO}"
FM_SUB = "vp-vnp"                    # the folder of the formalization inside formal-math
# paper.pdf at FM_COMMIT, from which diagrams/src/paper-facts.json was read by tools/paper-facts/extract.py.
PAPER_SHA256 = "882f5eefb1e067cc8c99ddfe660c10d1d67f9fcee7b69364bd0bab06c0c1f97c"
# diagrams/src/paper-facts.json as that script wrote it (tools/paper-facts/meta.json records both, and the commit).
PAPER_FACTS_SHA256 = "dfe6b5b575857a897459ec91ced42d595d7cfc051463ae49f41133605b2ce94d"

VP = pathlib.Path(os.environ.get("VP_VNP") or ROOT.parent / "vp-np")

LIBRARIES = ("Statement", "Challenge", "Solution", "Paper", "Nc", "NS1", "Ov")
KIND_WORD = {"Theorem": "theorem", "Lemma": "lemma", "Proposition": "proposition", "Corollary": "corollary",
             "Definition": "definition", "Remark": "remark", "Display": "display"}
KIND_ACCENT = {"Theorem": "blue", "Corollary": "blue", "Proposition": "teal", "Lemma": "teal",
               "Definition": "violet", "Display": "grey", "Remark": "grey"}
CASE_ACCENT = {"flat": "amber", "contracting": "pink", "both": "grey"}
CASE_LABEL = {"flat": "flat case", "contracting": "contracting case", "both": "both cases"}

NOT_BUILT = ("Nothing here builds or elaborates the Lean: names are read from the source text at the pinned commit, "
             "and a card says what a statement is, not that it is proved. That the proofs check is the claim of the "
             "formal-math repository's own CI (Comparator, with the nanoda kernel), not of these posters.")


# ------------------------------------------------------------------------------------------------ git and hashes
def git_rev(path, pin, what):
    """The full commit of a checkout, checked against `pin`."""
    out = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True)
    if out.returncode:
        raise ValueError(f"{path}: not a git checkout; set VP_VNP to the vp-vnp folder of formal-math")
    full = out.stdout.strip()
    if not full.startswith(pin):
        raise ValueError(f"{what} is at {full[:10]}, the posters were written against {pin}")
    return full


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def lean_url(full, path, line=None):
    """A file of the vp-vnp folder, and a line in it, at the pinned commit."""
    return f"{FM_URL}/blob/{full}/{FM_SUB}/{path}" + (f"#L{line}" if line else "")


def linked(url, text):
    return f"[[@{url}|{text}]]" if url else text


# ------------------------------------------------------------------------------------------------ Lean text
_CMD = ("theorem", "lemma", "def", "abbrev", "structure", "class", "inductive", "instance", "axiom", "example",
        "opaque", "noncomputable", "private", "protected", "partial", "unsafe", "nonrec", "irreducible_def",
        "namespace", "end", "section", "open", "variable", "universe", "attribute", "set_option", "local", "scoped",
        "notation", "infix", "infixl", "infixr", "prefix", "postfix", "macro", "syntax", "elab", "import", "export",
        "mutual", "deriving", "omit", "include", "@[", "#")
_DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?((?:(?:private|protected|noncomputable|nonrec|partial|unsafe) )*)"
                   r"(theorem|lemma|def|abbrev|structure|class|inductive|instance|irreducible_def|opaque|axiom)"
                   r"(?:\s+([^\s:({\[⦃]+))?")
_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_'.!?]*")


def blank(text):
    """The text with comments and string literals replaced by spaces (newlines kept), and the docstrings: a list of
    (start, end, text) of every /-- ... -/ comment."""
    out, docs, i, n = list(text), [], 0, len(text)
    def wipe(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "
    while i < n:
        if text.startswith("/-", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith("/-", j):
                    depth, j = depth + 1, j + 2
                elif text.startswith("-/", j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            if text.startswith("/--", i):
                docs.append((i, j, text[i + 3:j - 2].strip()))
            elif text.startswith("/-!", i):
                docs.append((i, j, None, text[i + 3:j - 2].strip()))
            wipe(i, j)
            i = j
        elif text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            wipe(i, j)
            i = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            wipe(i, j + 1)
            i = j + 1
        elif text[i] == "'" and i + 2 < n and text[i + 2] == "'" and not (i and (text[i - 1].isalnum() or text[i - 1] in "_'")):
            wipe(i, i + 3)          # a character literal; a prime after a name (x') is left alone
            i += 3
        else:
            i += 1
    return "".join(out), docs


def read_file(path, rel):
    """One Lean file: its imports, and its declarations with namespace, line, docstring, signature and tokens."""
    raw = path.read_text(encoding="utf-8")
    code, docs = blank(raw)
    lines = code.split("\n")
    starts, pos = [], 0
    for ln in raw.split("\n"):
        starts.append(pos)
        pos += len(ln) + 1
    imports = []
    scopes, decls = [], []
    binders = []                                        # the `variable` binders seen so far, (name, type)
    cur = None
    for no, ln in enumerate(lines):
        head = ln[:1]
        if not head.strip():
            continue                                    # indented, or empty: inside a declaration if there is one
        word = ln.split(None, 1)[0]
        if not (word in _CMD or word.startswith("@[") or word.startswith("#")):
            continue                                    # a continuation at the head of a line (a `|` case, `where`)
        if cur:
            cur["end"] = no
            cur = None
        if word == "import":
            imports.append(ln.split()[1])
        elif word == "variable":
            full = "\n".join(lines[no:no + 6]).split("\n\n")[0]
            for m in re.finditer(r"[{(\[⦃]([^{}()\[\]⦃⦄:]+):\s*([^{}()\[\]⦃⦄]+)[})\]⦄]", full):
                for nm in m.group(1).split():
                    binders.append((nm, m.group(2).strip()))
        elif word == "namespace":
            scopes += [("ns", p) for p in ln.split()[1].split(".")]
        elif word == "section":
            scopes.append(("sec", ln.split()[1] if len(ln.split()) > 1 else ""))
        elif word == "end":
            name = ln.split()[1] if len(ln.split()) > 1 else ""
            k = len(name.split(".")) if name else 1
            if scopes and scopes[-1][0] == "ns":
                del scopes[-k:]
            elif scopes:
                scopes.pop()
        m = _DECL.match(ln)
        if m and word not in ("namespace", "end", "section", "open", "attribute", "variable"):
            name = m.group(3)
            if m.group(2) == "instance" and (not name or name.startswith("[") or ":" in name):
                name = None
            if not name:
                continue
            ns = [p for kind, p in scopes if kind == "ns"]
            full = name[len("_root_."):] if name.startswith("_root_.") else ".".join(ns + [name])
            off = starts[no]
            doc = None
            for a, b, t, *_ in docs:      # the docstring that ends just before the declaration, attributes between
                if t is not None and b <= off and not re.sub(r"@\[[^\]]*\]", "", raw[b:off]).strip():
                    doc = t
            cur = {"name": full, "short": name, "kind": m.group(2), "private": "private" in m.group(1),
                   "file": rel, "line": no + 1, "doc": doc, "start": no, "variables": list(binders)}
            decls.append(cur)
    if cur:
        cur["end"] = len(lines)
    for d in decls:
        body = "\n".join(lines[d["start"]:d["end"]])
        d["tokens"] = sorted(set(_TOKEN.findall(body)))
        sig = []
        for ln in raw.split("\n")[d["start"]:d["end"]]:
            cut = re.split(r"\s:=(\s|$)|\swhere$", ln, maxsplit=1)
            sig.append(cut[0].rstrip())
            if len(cut) > 1:
                break
        d["signature"] = "\n".join(s for s in sig if s.strip())
        d["sig_tokens"] = sorted(set(_TOKEN.findall("\n".join(lines[d["start"]:d["start"] + len(sig)]).split(":=")[0])))
        last = max(i for i in range(d["start"], d["end"]) if lines[i].strip())   # the trailing comments are not its own
        d["source"] = "\n".join(raw.split("\n")[d["start"]:last + 1]).rstrip()
        d["lines"] = d["end"] - d["start"]
        del d["start"], d["end"]
    mdoc = next((d[3] for d in docs if len(d) == 4), None)
    return {"imports": imports, "decls": decls, "lines": raw.count("\n") + (0 if raw.endswith("\n") else 1),
            "doc": mdoc}


class Source:
    pass


def label_of(name):
    """The paper's LaTeX label of a Lean name: thm_cut -> thm:cut, lem_few_approx -> lem:few-approx."""
    head, _, rest = name.partition("_")
    return f"{head}:{rest.replace('_', '-')}"


_PAPER_DOC = re.compile(r"^\*\*Paper: (Theorem|Lemma|Proposition|Corollary|Definition|Remark|display) "
                        r"([a-z]+:[A-Za-z0-9-]+)\.\*\*\s*(.*)$", re.S)


def quote_of(doc):
    """The first quotation of the paper in a docstring, "…", or None."""
    m = re.search(r'"([^"]+)"', doc or "")
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def load():
    if not VP.is_dir():
        raise ValueError(f"no vp-vnp folder at {VP}; set VP_VNP")
    s = Source()
    s.full = git_rev(VP, FM_COMMIT, "formal-math")
    s.commit = s.full[:10]
    pdf = VP / "paper.pdf"
    if pdf.exists() and sha256(pdf) != PAPER_SHA256:
        raise ValueError(f"vp-vnp/paper.pdf hashes to {sha256(pdf)}, the facts were read from {PAPER_SHA256}: run "
                         "tools/paper-facts/extract.py, re-read what it changed, and bump PAPER_SHA256")
    facts_path = SRC / "paper-facts.json"
    if sha256(facts_path) != PAPER_FACTS_SHA256:
        raise ValueError(f"src/paper-facts.json hashes to {sha256(facts_path)}, pinned {PAPER_FACTS_SHA256}")
    meta = json.loads((ROOT / "tools" / "paper-facts" / "meta.json").read_text(encoding="utf-8"))
    if meta["paper_sha256"] != PAPER_SHA256 or meta["output_sha256"] != PAPER_FACTS_SHA256 \
            or not meta["commit"].startswith(FM_COMMIT):
        raise ValueError("tools/paper-facts/meta.json does not record the pinned commit and hashes")
    s.facts = json.loads(facts_path.read_text(encoding="utf-8"))
    lib.PINNED[:] = [f"{FM_URL}/blob/{s.full}/", f"{FM_URL}/tree/{s.full}/"]
    # The papers behind the reference list, this repository's own data (src/papers.toml): every id is a reference.
    s.papers = tomllib.loads((SRC / "papers.toml").read_text(encoding="utf-8"))
    keys = {e["key"] for e in s.facts["references"]["entries"]}
    bad = sorted(set(s.papers) - keys)
    if bad:
        raise ValueError(f"src/papers.toml names ids that are not references of the paper: {bad}")
    lib.PAPERS.clear()
    lib.PAPERS.update({k: v["url"] for k, v in s.papers.items() if v.get("url")})   # a work with no stable copy has none
    bare = sorted(k for k, v in s.papers.items() if not v.get("url") and not v.get("note"))
    if bare:
        raise ValueError(f"src/papers.toml: entries with neither a url nor a note saying why: {bare}")

    # every Lean file of the folder, outside .lake
    s.modules, s.decls, s.challenge = {}, {}, {}
    files = sorted(p for p in VP.rglob("*.lean") if ".lake" not in p.parts)
    by_short = {}
    for p in files:
        rel = p.relative_to(VP).as_posix()
        mod = rel[:-5].replace("/", ".")
        if mod.split(".")[0] not in LIBRARIES and mod != "Paper" and not rel.startswith("scripts/"):
            raise ValueError(f"{rel}: a Lean file outside the libraries the posters know, {LIBRARIES}")
        if rel.startswith("scripts/"):
            continue
        f = read_file(p, rel)
        s.modules[mod] = {"file": rel, "library": mod.split(".")[0], "lines": f["lines"], "imports": f["imports"],
                          "decls": [d["name"] for d in f["decls"]], "doc": f["doc"]}
        for d in f["decls"]:
            d["module"] = mod
            if mod == "Challenge":          # Solution's theorems again, with sorry: nothing imports this file
                s.challenge[d["name"]] = d
                continue
            if d["name"] in s.decls:
                raise ValueError(f"{d['name']} is declared twice: {s.decls[d['name']]['file']} and {rel}")
            s.decls[d["name"]] = d
            by_short.setdefault(d["short"], []).append(d["name"])
    s.by_short = by_short

    # the numbered statements: Table 3, each Lean name a declaration Paper.<name>
    s.statements = {}
    s.lean_of = {}                      # Lean full name -> the statements Table 3 gives it to
    for r in s.facts["table3"]:
        key = f"{r['kind']} {r['number']}"
        st = dict(r, key=key, header=s.facts["headers"].get(key), decls=[])
        for n in r["lean"]:
            full = f"Paper.{n}"
            if full not in s.decls:
                raise ValueError(f"Table 3 gives {key} the Lean theorem {full}, which no file of vp-vnp declares")
            st["decls"].append(full)
            s.lean_of.setdefault(full, []).append(key)
        if st["decls"]:
            d = s.decls[st["decls"][0]]
            m = _PAPER_DOC.match(d["doc"] or "")
            st["doc_kind"], st["doc_label"] = (m.group(1), m.group(2)) if m else (None, None)
            st["quote"] = quote_of(d["doc"])
        else:
            st["doc_kind"] = st["doc_label"] = st["quote"] = None
        s.statements[key] = st
    s.reach = {}
    s.uses = _statement_uses(s)
    return s


def closure(s, key):
    """Every declaration of vp-vnp under a statement's own Lean theorems, in any library: the walk from them through
    every declaration their text names, stopping at the theorems of other statements. A token names a declaration
    when it is the full name, or a dotted suffix of exactly one full name (`foo` for `Nc.Price.foo` after `open`),
    of a declaration in a file the naming file imports, directly or not, and has at least three characters; an
    ambiguous token names nothing. A local variable that is also the last
    part of exactly one declaration's name is counted as a use of it. Returns the set of full names."""
    if not hasattr(s, "_last"):
        s._last = {}
        for n in s.decls:
            s._last.setdefault(n.rsplit(".", 1)[-1], []).append(n)
        s._resolved = {}
        s._sees = {}
    def sees(mod):
        """The files a file can name: itself and every file of vp-vnp it imports, directly or not."""
        if mod not in s._sees:
            out, stack = {mod}, [mod]
            while stack:
                for i in s.modules[stack.pop()]["imports"]:
                    if i in s.modules and i not in out:
                        out.add(i)
                        stack.append(i)
            s._sees[mod] = out
        return s._sees[mod]
    def resolve(t, mod):
        if (t, mod) in s._resolved:
            return s._resolved[(t, mod)]
        t2 = t.strip(".")
        hit = None
        vis = sees(mod)
        if t2 in s.decls and s.decls[t2]["module"] in vis:
            hit = t2
        elif len(t2) >= 3:
            for cut in range(t2.count(".") + 1):           # a projection after the name (`foo.1`, `foo.mp`)
                head = t2.rsplit(".", cut)[0] if cut else t2
                cands = [n for n in s._last.get(head.rsplit(".", 1)[-1], ())
                         if (n == head or n.endswith("." + head)) and s.decls[n]["module"] in vis]
                if len(cands) == 1:
                    hit = cands[0]
                    break
                if cands:
                    break
        s._resolved[(t, mod)] = hit
        return hit
    st = s.statements[key]
    seen, stack = set(st["decls"]), list(st["decls"])
    while stack:
        d = s.decls[stack.pop()]
        for t in d["tokens"]:
            m = resolve(t, d["module"])
            if m and m not in seen and not (m in s.lean_of and key not in s.lean_of[m]):
                seen.add(m)
                stack.append(m)
    return seen


def _statement_uses(s):
    """statement -> sorted statements its declarations name, directly or through Paper declarations that belong to
    no statement. A token names a declaration when it is its full name, or its name inside Paper written bare or with
    `Paper.`; a projection after it (`thm_approx.1`) is allowed."""
    paper = {n: d for n, d in s.decls.items() if d["module"].split(".")[0] == "Paper"}
    short = {}
    for n, d in paper.items():
        short.setdefault(n[len("Paper."):] if n.startswith("Paper.") else n, set()).add(n)
    def refs(d):
        out = set()
        for t in d["tokens"]:
            parts = t.split(".")
            for i in range(len(parts)):
                cand = ".".join(parts[:i + 1])
                for c in (cand, cand[len("Paper."):] if cand.startswith("Paper.") else None):
                    if c and c in short:
                        out |= short[c]
        out.discard(d["name"])
        return out
    edges = {n: refs(d) for n, d in paper.items()}
    s.paper_refs = edges
    owner = s.lean_of
    uses = {}
    for key, st in s.statements.items():
        # walk from the statement's declarations through declarations that belong to no statement, or to this one;
        # stop at a declaration of another statement, which is a use: direct if one of its own names it
        # A name Table 3 gives two statements (scales_setting: K.5 and K.6) is each one's own, but what it names of
        # the other is a bundle, not a use: a walk that starts from it does not count the other co-owner.
        found = {}
        seen = set(st["decls"])
        frontier = [(n, True, frozenset(owner[n]) - {key}) for n in st["decls"]]
        while frontier:
            n, own, skip = frontier.pop()
            for m in sorted(edges.get(n, ())):
                others = [k for k in owner.get(m, ()) if k != key]
                if others:
                    for k in others:
                        if k in skip:
                            continue
                        found[k] = "direct" if (own or found.get(k) == "direct") else found.get(k, "through")
                    continue
                if m not in seen and m not in owner:
                    seen.add(m)
                    frontier.append((m, False, skip))
        uses[key] = {k: found[k] for k in sorted(found, key=order_key)}
        s.reach[key] = seen                 # the statement's own theorems and the Paper helpers its walk passed
    return uses


def route(s):
    """(roots, on): the statements Solution's theorems name, and every statement reached from them by uses."""
    roots = sorted({k for n, d in s.decls.items() if d["module"] == "Solution" and d["kind"] == "theorem"
                    for k in statements_named(s, d)}, key=order_key)
    on, stack = set(roots), list(roots)
    while stack:
        for u in s.uses[stack.pop()]:
            if u not in on:
                on.add(u)
                stack.append(u)
    return roots, on


POLY = re.compile(r"Type u\b|Type\*|Type _|Sort u\b|Sort \*")


def polymorphic(decl):
    """Whether a declaration takes a type in any universe: its signature says so (`Type u`, `Type*`), or it uses a
    name that a `variable` of its file binds so and that the signature does not bind again."""
    sig = decl["signature"]
    if POLY.search(sig):
        return True
    toks = set(decl["sig_tokens"])
    for name, typ in decl["variables"]:
        if name in toks and POLY.fullmatch(typ) and not re.search(r"[{(\[⦃][^:{}()\[\]]*\b" + re.escape(name)
                                                                   + r"\b[^:{}()\[\]]*:", sig):
            return True
    return False


def statements_named(s, decl):
    """The numbered statements whose Lean theorems a declaration's text names, bare or as Paper.<name>."""
    out = set()
    for t in decl["tokens"]:
        parts = [p for p in t.split(".") if p]
        for i in range(len(parts)):
            cand = ".".join(parts[:i + 1])
            full = cand if cand.startswith("Paper.") else f"Paper.{cand}"
            out |= set(s.lean_of.get(full, ()))
    return sorted(out, key=order_key)


def order_key(key):
    """Paper order: Section A to O, then the number."""
    kind, num = key.split(" ", 1)
    num = num.strip("()")
    sec, _, n = num.partition(".")
    return ("123456789ABCDEFGHIJKLMNO".index(sec), int(n), kind != "Display")


# ------------------------------------------------------------------------------------------------ drawing
def cells(s):
    return lib.em(s, "m") / MONO_EM


def lean_block(sig, cols, max_lines=9):
    """A Lean signature as formula lines (indent, text, is_comment), wrapped at `cols` cells. A wrapped line continues
    four columns in from the line it came from."""
    out = []
    for src in sig.splitlines():
        src = src.rstrip()
        if not src:
            continue
        ind = len(src) - len(src.lstrip(" "))
        line, cur, cont = [], ind, ind
        words = []
        for w in src.strip().split(" "):
            while len(w) > cols - ind - 4:
                words.append(w[:cols - ind - 4])
                w = w[cols - ind - 4:]
            words.append(w)
        for w in words:
            if line and cur + 1 + cells(w) > cols:
                out.append((cont, " ".join(line), False))
                cont = ind + 4
                line, cur = [w], cont + cells(w)
            else:
                cur += (1 if line else 0) + cells(w)
                line.append(w)
        out.append((cont, " ".join(line), False))
    if len(out) > max_lines:
        rest = len(out) - (max_lines - 1)
        out = out[:max_lines - 1] + [(out[max_lines - 1][0], f"… {rest} more lines", True)]
    return out


def columns(w, pad=16, fpad=11, fsize=13.5):
    return int((w - 2 * pad - 2 * fpad) / (MONO_EM * fsize))


def mono_line(x, y, s, size, color="ink", bold=False, italic=False):
    lib.TEXT_BOXES.append((x, y - size * 0.75, x + lib.mono_width(s, size, bold), y + size * 0.2, s))
    b = ' font-weight="bold"' if bold else ""
    it = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{lib.MONO}" font-size="{size}"{b}{it} '
            f'xml:space="preserve" {fill(color)}>{escape(s)}</text>')


def formula_width(formula, size):
    return max(lib.mono_width(" " * ind + t, size) for ind, t, _ in formula) if formula else 0


def node(c, x, y, w, name, accent, formula=(), pill=None, say=None, bullets=(), foot=(), h=None, draw=True,
         size=13.5, fsize=13, tsize=17, pad=16, dash=None, anchor=None):
    """A card. formula: lean_block() output. say: a rich string set in italics (a quotation). bullets and foot: rich
    strings. anchor: an id set on a group around the card, so that poster.svg#id lands on it. Returns the height;
    draw=False measures only."""
    inner = w - 2 * pad
    lead, flead, fpad = round(size * 1.42, 1), round(fsize * 1.5, 1), 11
    pw = lib.text_width(pill, 11.5, bold=True) + 18 + 12 if pill else 0
    while True:
        tlines = wrap(name, inner - pw, tsize, bold=True)
        tw = max(lib.line_width(ln, tsize) for ln in tlines) + pw
        if tw <= inner + 0.5 and len(tlines) <= 2:
            break
        if tsize <= 14:
            raise ValueError(f"node {name}: the title needs {tw:.0f} px or {len(tlines)} lines, the card has {inner:.0f}")
        tsize -= 1
    theight = tsize + (tsize + 4) * (len(tlines) - 1)
    need = formula_width(formula, fsize) + 2 * fpad
    if need > inner + 0.5:
        raise ValueError(f"node {name}: formula needs {need:.0f} px, the card has {inner:.0f}")
    say_lines = wrap(" ".join(say.split()), inner - 4, size, italic=True) if say else []   # a docstring's breaks are not its own
    blines = [wrap(b, inner - lib.width("•  ", size), size) for b in bullets]
    flines = [wrap(f, inner, size - 1) for f in foot]
    panel_h = len(formula) * flead + 2 * fpad - 5 if formula else 0
    hh = pad + theight + 12 + (panel_h + 12 if formula else 0)
    if say_lines:
        hh += len(say_lines) * lead + 8
    for ls in blines:
        hh += len(ls) * lead + 3
    if flines:
        hh += 10 + sum(len(ls) * round((size - 1) * 1.42, 1) + 2 for ls in flines)
    hh += pad - 6
    if h is not None:
        hh = max(h, hh)
    if not draw:
        return hh
    if anchor:
        c.add(f'<g id="{anchor}">')
        c.anchors.append(anchor)
        c.out.append(lib.halo(x, y, w, hh, accent))
    c.blocks.append((x, y, x + w, y + hh, "node " + name))
    c.rect(x, y, w, hh, accent, dash=dash)
    for i, ln in enumerate(tlines):
        c.add(render_line(x + pad, y + pad + tsize - 3 + i * (tsize + 4), ln, tsize, accent, bold=True))
    if pill:
        c.pill(x + w - pad, y + pad - 3, pill, accent, 11.5, anchor="end", solid=True)
    cy = y + pad + theight + 12
    if formula:
        c.add(f'<rect x="{x + pad:.1f}" y="{cy:.1f}" width="{inner:.1f}" height="{panel_h:.1f}" rx="6" '
              f'{fs("bg", "line")} stroke-width="1"/>')
        for i, (ind, t, is_comment) in enumerate(formula):
            ly = cy + fpad + fsize - 1 + i * flead
            lx = x + pad + fpad + ind * MONO_EM * fsize
            c.add(mono_line(lx, ly, t, fsize, "faint" if is_comment else "ink", italic=is_comment))
        cy += panel_h + 12
    if say_lines:
        for ln in say_lines:
            c.add(render_line(x + pad + 2, cy + size - 1, ln, size, "muted", italic=True))
            cy += lead
        cy += 8
    for ls in blines:
        for i, ln in enumerate(ls):
            if i == 0:
                c.add(render_line(x + pad, cy + size - 1, [("•", "b", None)], size, accent))
            c.add(render_line(x + pad + lib.width("•  ", size), cy + size - 1, ln, size, "ink"))
            cy += lead
        cy += 3
    if flines:
        fy = y + hh - pad + 6 - sum(len(ls) * round((size - 1) * 1.42, 1) + 2 for ls in flines)
        c.line(x + pad, fy - 6, x + w - pad, fy - 6, "line", sw=1)
        for ls in flines:
            for ln in ls:
                c.add(render_line(x + pad, fy + size - 2, ln, size - 1, "muted"))
                fy += round((size - 1) * 1.42, 1)
            fy += 2
    if anchor:
        c.add("</g>")
    return hh


def code(s, limit=34):
    """A code run the wrapper can break at its separators."""
    if len(s) <= limit:
        return f"`{s}`"
    parts = re.split(r"(?<=[/._])", s)
    runs, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > limit:
            runs.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        runs.append(cur)
    return " ".join(f"`{r}`" for r in runs)


def names(xs, limit=10):
    xs = list(xs)
    head = ", ".join(code(x) for x in xs[:limit])
    return head + (f" … and {len(xs) - limit} more" if len(xs) > limit else "")


def abridge(s, limit):
    """At most `limit` characters, cut at a word and marked with ' …'."""
    if s is None or len(s) <= limit:
        return s
    return s[:limit].rsplit(" ", 1)[0].rstrip(",;:") + " …"


def anchor_of(key):
    """The id a statement's card carries: 'Lemma A.2' -> A.2, 'Display (F.1)' -> F.1-display."""
    kind, num = key.split(" ", 1)
    return num.strip("()") + ("-display" if kind == "Display" else "")


def compare(what, expected, actual, reread):
    """Fail the build, in both directions, with both values and what to re-read."""
    if expected != actual:
        exp, act = expected, actual
        if isinstance(expected, (list, tuple, set, dict)) and isinstance(actual, type(expected)):
            e, a = (set(map(repr, expected)), set(map(repr, actual))) if not isinstance(expected, dict) else \
                (set(map(repr, expected.items())), set(map(repr, actual.items())))
            exp, act = sorted(e - a), sorted(a - e)
            raise ValueError(f"{what}: recorded but not in the sources {exp}; in the sources but not recorded {act}. "
                             f"Re-read {reread}")
        raise ValueError(f"{what}: recorded {exp!r}, the sources say {act!r}. Re-read {reread}")
