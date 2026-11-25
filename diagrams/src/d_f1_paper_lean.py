"""F1 — The paper against the Lean: every numbered statement of the appendix, row by row.

The paper's Table 3 names, for each numbered statement of Sections A to N, the Lean theorems (prefix Paper.) that
belong to it. This poster reads that table from src/paper-facts.json and joins each row to the Lean source at
FM_COMMIT: the file and line of each theorem, the label its docstring opens with, the paper's words the docstring
quotes, and the other numbered statements its proof uses, read from the elaborated Lean (src/lean-uses.json; F9
sets that reading against the source text). The build fails if the statements, their kinds, the rows without a Lean theorem, the rows whose docstring
does not open with the paper's label, the Lean names Table 3 gives two statements, or any use between statements
differ from what is recorded here, in either direction."""
import collections

import vp
from vp import anchor_of, code, compare, linked
from lib import Canvas

ID, SLUG = "F1", "paper-lean"

W = 3080
S = 13

N_STATEMENTS = 65
KINDS = {"Corollary": 3, "Definition": 7, "Display": 1, "Lemma": 21, "Proposition": 16, "Remark": 1, "Theorem": 16}
NOT_FORMALIZED = ["Remark N.6"]
# Rows whose first Lean theorem's docstring does not open with "**Paper: <Kind> <label>.**" for the row's kind and the
# label of the theorem's name (thm_cut -> thm:cut).
NO_DOC_LABEL = ["Display (F.1)", "Remark N.6"]
# A name given to two rows is each one's own; what it names of the other row is not a use (vp._statement_uses).
SHARED = {"Paper.scales_setting": ["Proposition K.5", "Theorem K.6"]}
# Every use between numbered statements that the elaborated Lean shows (src/lean-uses.json), as (used, user); DIRECT,
# those a theorem of the user's own row refers to, the rest through declarations of vp-vnp that belong to no row.
EXPECTED = [
    ('Definition A.1', 'Lemma A.2'), ('Definition A.1', 'Theorem A.6'), ('Proposition A.5', 'Theorem A.6'),
    ('Definition A.1', 'Proposition A.7'), ('Proposition A.5', 'Proposition A.7'),
    ('Definition A.1', 'Proposition A.8'), ('Lemma A.2', 'Proposition A.8'), ('Proposition A.7', 'Proposition A.8'),
    ('Definition A.1', 'Proposition B.3'), ('Lemma A.3', 'Proposition B.3'), ('Lemma B.1', 'Proposition B.3'),
    ('Proposition B.2', 'Proposition B.3'), ('Definition A.1', 'Theorem C.1'), ('Lemma A.2', 'Theorem C.1'),
    ('Lemma C.2', 'Theorem C.1'), ('Proposition A.8', 'Theorem C.1'), ('Proposition B.3', 'Theorem C.1'),
    ('Definition A.1', 'Lemma C.2'), ('Lemma A.2', 'Lemma C.2'), ('Proposition B.3', 'Lemma C.2'),
    ('Definition A.1', 'Proposition C.3'), ('Lemma A.2', 'Proposition C.3'), ('Proposition A.8', 'Proposition C.3'),
    ('Theorem C.1', 'Proposition C.3'), ('Definition A.1', 'Theorem D.2'), ('Lemma A.2', 'Theorem D.2'),
    ('Lemma C.4', 'Theorem D.2'), ('Proposition C.3', 'Theorem D.2'), ('Proposition E.1', 'Corollary E.2'),
    ('Corollary E.2', 'Lemma E.3'), ('Definition A.1', 'Proposition E.5'), ('Lemma A.3', 'Proposition E.5'),
    ('Lemma E.4', 'Proposition E.5'), ('Lemma E.3', 'Theorem E.6'), ('Proposition E.5', 'Theorem E.6'),
    ('Definition A.1', 'Lemma E.7'), ('Definition A.1', 'Lemma E.8'), ('Lemma A.2', 'Lemma E.8'),
    ('Proposition A.7', 'Lemma E.8'), ('Theorem C.1', 'Lemma E.8'), ('Definition A.1', 'Proposition E.9'),
    ('Lemma E.8', 'Proposition E.9'), ('Definition A.1', 'Proposition E.10'), ('Lemma A.3', 'Proposition E.10'),
    ('Lemma E.4', 'Proposition E.10'), ('Lemma E.7', 'Proposition E.10'), ('Proposition E.9', 'Proposition E.10'),
    ('Lemma E.3', 'Theorem E.11'), ('Proposition E.10', 'Theorem E.11'), ('Lemma F.1', 'Lemma F.3'),
    ('Lemma F.2', 'Lemma F.3'), ('Lemma C.4', 'Display (F.1)'), ('Lemma F.3', 'Display (F.1)'),
    ('Display (F.1)', 'Lemma F.4'), ('Lemma C.4', 'Lemma F.4'), ('Display (F.1)', 'Lemma F.5'),
    ('Lemma C.4', 'Lemma F.5'), ('Lemma F.4', 'Lemma F.5'), ('Display (F.1)', 'Theorem F.6'),
    ('Lemma C.4', 'Theorem F.6'), ('Lemma F.2', 'Theorem F.6'), ('Lemma F.3', 'Theorem F.6'),
    ('Lemma F.5', 'Theorem F.6'), ('Proposition C.3', 'Theorem F.6'), ('Definition A.1', 'Theorem G.2'),
    ('Lemma A.2', 'Theorem G.2'), ('Lemma F.2', 'Theorem G.2'), ('Theorem A.6', 'Theorem G.2'),
    ('Theorem F.6', 'Theorem G.2'), ('Lemma F.2', 'Proposition H.1'), ('Proposition H.1', 'Theorem H.2'),
    ('Lemma I.2', 'Proposition J.2'), ('Theorem H.2', 'Proposition J.2'), ('Proposition I.1', 'Theorem J.3'),
    ('Proposition J.2', 'Theorem J.3'), ('Theorem G.2', 'Theorem J.4'), ('Theorem J.3', 'Theorem J.4'),
    ('Lemma K.2', 'Lemma K.3'), ('Proposition E.1', 'Lemma K.3'), ('Proposition I.1', 'Lemma K.3'),
    ('Lemma K.4', 'Proposition K.5'), ('Theorem J.4', 'Proposition K.5'), ('Lemma K.4', 'Theorem K.6'),
    ('Proposition K.5', 'Theorem K.6'), ('Theorem J.4', 'Theorem K.6'), ('Lemma K.3', 'Theorem K.7'),
    ('Proposition E.1', 'Theorem K.7'), ('Proposition K.5', 'Theorem K.7'), ('Theorem K.6', 'Theorem K.7'),
    ('Theorem D.2', 'Theorem L.1'), ('Theorem E.11', 'Theorem L.1'), ('Theorem K.7', 'Theorem L.1'),
    ('Theorem D.2', 'Theorem L.2'), ('Theorem E.6', 'Theorem L.2'), ('Theorem K.7', 'Theorem L.2'),
    ('Theorem L.2', 'Corollary L.3'), ('Lemma K.3', 'Theorem M.3'), ('Lemma M.1', 'Theorem M.3'),
    ('Proposition E.10', 'Theorem M.3'), ('Proposition K.5', 'Theorem M.3'), ('Proposition M.2', 'Theorem M.3'),
    ('Theorem D.2', 'Theorem M.3'), ('Theorem E.11', 'Theorem M.3'), ('Theorem K.6', 'Theorem M.3'),
    ('Theorem K.7', 'Theorem M.3'), ('Theorem L.1', 'Theorem M.3'), ('Theorem M.3', 'Corollary M.4'),
    ('Definition A.1', 'Lemma N.3'), ('Lemma K.4', 'Proposition N.4'), ('Theorem J.4', 'Proposition N.4'),
    ('Theorem K.6', 'Proposition N.4'), ('Definition A.1', 'Theorem N.5'), ('Lemma A.3', 'Theorem N.5'),
    ('Lemma E.4', 'Theorem N.5'), ('Lemma K.2', 'Theorem N.5'), ('Lemma N.2', 'Theorem N.5'),
    ('Lemma N.3', 'Theorem N.5'), ('Proposition E.1', 'Theorem N.5'), ('Proposition E.9', 'Theorem N.5'),
    ('Proposition I.1', 'Theorem N.5'), ('Proposition M.2', 'Theorem N.5'), ('Proposition N.4', 'Theorem N.5'),
    ('Theorem D.2', 'Theorem N.5'), ('Theorem L.1', 'Theorem N.5'),
]
DIRECT = [
    ('Definition A.1', 'Lemma A.2'), ('Definition A.1', 'Theorem A.6'), ('Proposition A.5', 'Theorem A.6'),
    ('Definition A.1', 'Proposition A.7'), ('Proposition A.5', 'Proposition A.7'),
    ('Theorem C.1', 'Proposition C.3'), ('Corollary E.2', 'Lemma E.3'), ('Lemma E.3', 'Theorem E.6'),
    ('Proposition E.5', 'Theorem E.6'), ('Lemma E.8', 'Proposition E.9'), ('Lemma E.7', 'Proposition E.10'),
    ('Lemma E.3', 'Theorem E.11'), ('Proposition E.10', 'Theorem E.11'), ('Lemma F.3', 'Display (F.1)'),
    ('Display (F.1)', 'Lemma F.4'), ('Lemma C.4', 'Lemma F.4'), ('Lemma F.4', 'Lemma F.5'),
    ('Lemma C.4', 'Theorem F.6'), ('Proposition C.3', 'Theorem F.6'), ('Lemma I.2', 'Proposition J.2'),
    ('Theorem H.2', 'Proposition J.2'), ('Proposition I.1', 'Theorem J.3'), ('Proposition J.2', 'Theorem J.3'),
    ('Theorem J.3', 'Theorem J.4'), ('Theorem J.4', 'Proposition K.5'), ('Theorem J.4', 'Theorem K.6'),
    ('Theorem D.2', 'Theorem L.1'), ('Theorem E.11', 'Theorem L.1'), ('Theorem K.7', 'Theorem L.1'),
    ('Theorem D.2', 'Theorem L.2'), ('Theorem E.6', 'Theorem L.2'), ('Theorem K.7', 'Theorem L.2'),
    ('Theorem L.2', 'Corollary L.3'), ('Lemma M.1', 'Theorem M.3'), ('Theorem D.2', 'Theorem M.3'),
    ('Theorem E.11', 'Theorem M.3'), ('Theorem K.7', 'Theorem M.3'), ('Theorem M.3', 'Corollary M.4'),
    ('Theorem J.4', 'Proposition N.4'), ('Theorem K.6', 'Proposition N.4'), ('Lemma N.2', 'Theorem N.5'),
]


def abridge(s, limit):
    if s is None or len(s) <= limit:
        return s
    cut = s[:limit].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + " …"


def build():
    src = vp.load()
    st = src.statements
    reread = "Table 3 of paper.pdf (src/paper-facts.json) and the Paper/*.lean files at FM_COMMIT"
    compare("F1: the number of numbered statements in Table 3", N_STATEMENTS, len(st), reread)
    compare("F1: statements by kind", KINDS, dict(sorted(collections.Counter(r["kind"] for r in st.values()).items())),
            reread)
    compare("F1: the statements with no Lean theorem", NOT_FORMALIZED, [k for k, r in st.items() if not r["decls"]],
            reread)
    nolabel = [k for k, r in st.items() if not r["decls"] or r["doc_kind"] != r["kind"]
               or r["doc_label"] != vp.label_of(r["lean"][0])]
    compare("F1: the rows whose docstring does not open with the paper's kind and label", NO_DOC_LABEL, nolabel,
            "the docstring of each row's first Lean theorem")
    compare("F1: Lean names Table 3 gives two statements", SHARED,
            {n: k for n, k in sorted(src.lean_of.items()) if len(k) > 1}, reread)
    edges = [(u, k) for k in st for u in src.lean_uses[k]]
    direct = [(u, k) for k in st for u, v in src.lean_uses[k].items() if v == "direct"]
    compare("F1: the uses between numbered statements in the elaborated Lean", sorted(EXPECTED), sorted(edges),
            "src/lean-uses.json (tools/lean-uses/README.md)")
    compare("F1: the uses a row's own theorem names", sorted(DIRECT), sorted(direct),
            "src/lean-uses.json (tools/lean-uses/README.md)")
    used_by = collections.defaultdict(list)
    for u, k in edges:
        used_by[u].append(k)
    sections = {r["section"]: r for r in src.facts["table1"]}

    c = Canvas(ID, f"The paper against the Lean: the {len(st)} numbered statements of the appendix, each beside the "
               "Lean theorems Table 3 gives it",
               "Read from the paper's Table 3 and its statement headers (pinned in src/paper-facts.json) and from the "
               f"Lean source of vp-vnp at formal-math {src.commit}. A row is one numbered statement: its header in the "
               "paper, its Lean theorems with file and line, the label the first theorem's docstring opens with, the "
               "paper's words that docstring quotes, and the other statements its Lean proof names.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (Table 3, the statement headers, "
               "Table 1 for the section names), vp-vnp/Paper/*.lean.",
               state=f"Drawn from formal-math {src.commit}")
    x, y = c.x0, c.y
    nf = len([1 for r in st.values() if r["decls"]])
    ndirect = len(direct)
    c.para(x, y, c.x1 - x, f"**How to read it.** {nf} of the {len(st)} rows have a Lean theorem; the one without is "
           f"{', '.join(NOT_FORMALIZED)}, which the paper's own Section 3 names as its one unformalized statement. "
           f"**Uses** lists the rows whose theorems the row's elaborated Lean proof refers to: {ndirect} of the "
           f"{len(edges)} uses by the row's own theorem, the rest, marked via, through declarations of vp-vnp that "
           "belong to no row. A row number links to the row. " + vp.NOT_BUILT_LEAN, S + 1, "muted")
    y += 70

    cols = [("Statement", 200), ("Title in the paper, and page", 360), ("Lean theorems (prefix Paper.), file and line",
            560), ("Docstring label", 200), ("The paper's words, as the docstring quotes them", 860),
            ("Uses (in the elaborated Lean)", 520), ("Used by", 280)]
    scale = (c.x1 - x) / sum(w for _, w in cols)
    cols = [(t, round(w * scale)) for t, w in cols]
    rows = []
    sec = None
    for k in sorted(st, key=vp.order_key):
        r = st[k]
        if r["section"] != sec:
            sec = r["section"]
            t1 = sections[sec]
            rows.append({"group": f"Section {sec} · “{t1['what']}” (Table 1) · {vp.CASE_LABEL[t1['case']]}",
                         "accent": vp.CASE_ACCENT[t1["case"]]})
        h = r["header"]
        title = (h["title"] or "no title in its header") if h else "a display, inside the proof of Lemma F.3"
        page = f" · p. {h['page']}" if h else ""
        leans = []
        for n in r["decls"]:
            d = src.decls[n]
            url = vp.lean_url(src.full, d["file"], d["line"])
            shared = " (also " + ", ".join(o for o in src.lean_of[n] if o != k) + ")" if len(src.lean_of[n]) > 1 else ""
            leans.append(f"{linked(url, code(n[len('Paper.'):], 30))} {d['file'].split('/')[-1]}:{d['line']}{shared}")
        if not leans:
            leans = [f"“{r['printed']}” (Table 3)"]
        if r["decls"] and r["doc_label"]:
            label = f"`{r['doc_label']}` ✓" if k not in NO_DOC_LABEL else f"`{r['doc_label']}`"
        else:
            label = "no label"
        quote = abridge(r["quote"], 300)
        quote = f"“{quote}”" if quote else ("no quotation" if r["decls"] else "")
        uses = src.lean_uses[k]
        dl = [f"`{anchor_of(u)}`" for u, v in uses.items() if v == "direct"]
        tl = [f"`{anchor_of(u)}`" for u, v in uses.items() if v != "direct"]
        ucell = ", ".join(dl) + ("; " if dl and tl else "") + (("via " + ", ".join(tl)) if tl else "")
        ub = ", ".join(f"`{anchor_of(u)}`" for u in sorted(used_by[k], key=vp.order_key))
        rows.append({"cells": [f"`{anchor_of(k)}` {r['kind'].lower()}", f"{title}{page}", "\n".join(leans), label,
                               quote, ucell or "none named", ub or "none"],
                     "anchor": anchor_of(k), "accent": None if r["decls"] else "red"})
    y += c.table(x, y, cols, rows, size=S) + 40

    # a note on what is not checked
    note = ("**Not checked here.** Whether a Lean theorem says what its row says: the docstring's label and quotation "
            "are the Lean authors' claim that it does, and Appendix Q of the paper lists the differences they know of. "
            "A use is a constant of an elaborated term, its type included, so a use the proof makes only in a "
            "statement it states but does not need is still counted.")
    c.para(x, y, c.x1 - x, note, S + 1, "muted")
    return c
