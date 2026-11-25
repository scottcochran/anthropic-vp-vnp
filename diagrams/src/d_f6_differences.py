"""F6 — Where the Lean and the text differ: every Lean name the paper prints, the universes, and Appendix Q.3's
list of differences between the statements of the text and those of the Lean, each checked as far as it can be.

The paper prints Lean names in typewriter type throughout. This poster finds every one in the text (a word with an
underscore; src/paper-facts.json, paper_names) and checks that the Lean source declares it. It sets Appendix Q.3's
sentence on universes against the Lean signatures (vp.polymorphic), and quotes Q.3's differences bullet by bullet
with the statements and Lean names each one mentions, every name checked to exist. The build fails if a printed
name is not declared (other than those recorded), if the names beyond Table 3 change, if the universes of the text
and of the Lean part, or if a bullet's statements or names differ from what is recorded here."""
import vp
from vp import anchor_of, code, compare, linked
from lib import Canvas

ID, SLUG = "F6", "differences"

W = 3080
S = 13.5
G = 30

N_PAPER_NAMES = 96
NOT_DECLARED = ['native_decide']
BEYOND_TABLE3 = {'contracting_approx_complete': 'Paper.contracting_approx_complete',
 'exists_generates': 'Paper.exists_generates',
 'exists_laws': 'Paper.exists_laws',
 'lem_circuit_approx': 'Paper.lem_circuit_approx',
 'lem_circuit_phi': 'Paper.lem_circuit_phi',
 'permanent_over_real': 'Solution.permanent_over_real',
 'prop_flat_lower_sum': 'Paper.prop_flat_lower_sum',
 'thm_allfields_exceeds': 'Paper.thm_allfields_exceeds',
 'thm_onecut_evaluator': 'Paper.thm_onecut_evaluator',
 'thm_onecut_program': 'Paper.thm_onecut_program',
 'universal_symbols_ne': 'Paper.universal_symbols_ne'}
UNIVERSES = ['Lemma M.1', 'Theorem M.3', 'Corollary M.4', 'Definition N.1', 'Lemma N.2', 'Theorem N.5']
STRONGER = ['Lemma A.3', 'Lemma E.4', 'Lemma E.7', 'Lemma F.1', 'Lemma F.2', 'Lemma I.2', 'Lemma K.3', 'Lemma M.1',
 'Lemma N.2', 'Lemma N.3', 'Proposition B.2']
DIFFERENCES = [([], []), ([], []), (['Theorem F.6', 'Lemma F.3', 'Lemma F.4', 'Lemma F.5'], ['projection_nearest']),
 (['Theorem A.6', 'Proposition A.7'], []), (['Lemma E.3', 'Proposition E.10', 'Proposition E.5'], []),
 (['Lemma A.3', 'Lemma E.4', 'Lemma E.7', 'Lemma F.1', 'Lemma F.2', 'Lemma I.2', 'Lemma K.3', 'Lemma M.1',
   'Lemma N.2', 'Lemma N.3', 'Proposition B.2', 'Proposition E.10'],
  ['lem_hubs', 'lem_hubs_further']),
 (['Theorem G.2', 'Theorem F.6'], ['def_law']), (['Proposition H.1'], ['prop_tower_representatives']),
 (['Theorem H.2', 'Proposition J.2'], ['thm_tree_good']), (['Proposition J.2', 'Lemma I.2'], []),
 (['Theorem H.2', 'Proposition J.2', 'Theorem J.3', 'Theorem J.4', 'Theorem G.2'],
  ['exists_laws', 'exists_generates', 'exists_setting', 'thm_onecut_evaluator', 'thm_onecut_program']),
 (['Proposition K.5', 'Theorem K.6', 'Proposition N.4', 'Theorem J.4'],
  ['scales_setting', 'prop_approx_acc_setting']),
 (['Lemma C.2', 'Proposition M.2', 'Definition N.1'], ['def_approx']), ([], []),
 (['Proposition I.1', 'Lemma K.2', 'Lemma K.3'], ['universal_symbols_ne', 'lem_circuit_phi'])]


def build():
    src = vp.load()
    f = src.facts
    q3 = f["q3"]
    by_short = {}
    for n in src.decls:
        by_short.setdefault(n.rsplit(".", 1)[-1], []).append(n)
    names = [p["name"] for p in f["paper_names"]]
    pages = {p["name"]: p["pages"] for p in f["paper_names"]}
    reread = "paper.pdf (src/paper-facts.json) and the Lean files of vp-vnp at FM_COMMIT"
    compare("F6: the number of Lean names the paper prints", N_PAPER_NAMES, len(names), reread)
    compare("F6: the names the paper prints that no file declares", NOT_DECLARED,
            [n for n in names if n not in by_short], reread)
    for n in NOT_DECLARED:
        hits = [p.name for p in sorted(vp.VP.rglob("*.lean")) if ".lake" not in p.parts and n in p.read_text()]
        if hits:
            raise ValueError(f"F6: the paper says {n} is not used, and {hits} name it")
    t3 = {n for r in f["table3"] for n in r["lean"]}
    compare("F6: the names the paper prints beyond Table 3", BEYOND_TABLE3,
            {n: sorted(by_short[n])[0] for n in names if n not in t3 and n in by_short}, reread)
    st = src.statements
    lean_poly = sorted((k for k, r in st.items() if r["decls"] and vp.polymorphic(src.decls[r["decls"][0]])),
                       key=vp.order_key)
    compare("F6: the statements Appendix Q.3 says may take a field in any universe", UNIVERSES,
            sorted(q3["universes"]["names"], key=vp.order_key), reread)
    compare("F6: the statements whose Lean takes a type in any universe", UNIVERSES, lean_poly,
            "the signatures and `variable` lines of the Lean theorems (vp.polymorphic)")
    compare("F6: the statements Q.3 says are proved in stronger forms", STRONGER, q3["stronger"]["names"], reread)
    compare("F6: Appendix Q.3's differences, the statements and Lean names of each",
            DIFFERENCES, [(b["names"], b["lean"]) for b in q3["differences"]], reread)
    for b in q3["differences"]:
        for n in b["lean"]:
            if n not in by_short:
                raise ValueError(f"F6: Appendix Q.3 names {n}, which no file declares")
        for k in b["names"]:
            if k not in st:
                raise ValueError(f"F6: Appendix Q.3 names {k}, which Table 3 does not list")

    def lean_link(n):
        d = src.decls[sorted(by_short[n])[0]]
        return linked(vp.lean_url(src.full, d["file"], d["line"]), code(n, 32))

    c = Canvas(ID, "Where the Lean and the text differ: every Lean name the paper prints, the universes, and "
               "Appendix Q.3's list of differences, each checked against the source",
               "The paper prints Lean names in typewriter type throughout, and its Appendix Q.3 lists how the Lean "
               "statements differ from the printed ones. Read from paper.pdf (pinned in src/paper-facts.json) and the "
               f"Lean source of vp-vnp at formal-math {src.commit}. The words in quotation marks are the paper's.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (the whole text, Appendix Q.3), "
               "vp-vnp/**/*.lean.", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    nin = len([n for n in names if n in t3])
    c.para(x0, y, c.x1 - x0, f"**How to read it.** A Lean name in the paper is a word with an underscore, the only "
           f"words the text sets so. Of the {len(names)} it prints, {nin} are in Table 3, {len(BEYOND_TABLE3)} name "
           f"steps that Table 3 does not list, and {len(NOT_DECLARED)} is not a declaration. A statement number links "
           "to its row on F1; a Lean name, to its line at the pin. " + vp.NOT_BUILT, S + 0.5, "muted")
    y += 64

    # ---- the names beyond Table 3
    y += c.heading(x0, y, f"1 · The {len(names)} Lean names the paper prints, and the {len(BEYOND_TABLE3)} beyond "
                   "Table 3")
    cols = [("Name", 520), ("Declared as", 760), ("File and line", 700), ("Printed on pages", c.x1 - x0 - 1980)]
    rows = []
    for n, full in BEYOND_TABLE3.items():
        d = src.decls[full]
        rows.append([lean_link(n), code(full, 60), f"{d['file']}:{d['line']}", ", ".join(map(str, pages[n]))])
    for n in NOT_DECLARED:
        rows.append({"cells": [f"`{n}`", "not a declaration: a Lean tactic", "no file of vp-vnp names it",
                               ", ".join(map(str, pages[n]))], "accent": "grey"})
    y += c.table(x0, y, cols, rows, size=S) + 40

    # ---- universes
    y += c.heading(x0, y, "2 · Universes: Appendix Q.3 against the signatures")
    cw = (c.x1 - x0 - G) / 2
    h1 = c.card(x0, y, cw, "The paper (Appendix Q.3)",
                ["“The theorems with prefix Paper. are stated for fields in the lowest universe … The exception is "
                 f"the given field in {q3['universes']['text']}, which may lie in any universe.”",
                 "Its list: " + ", ".join(f"`{anchor_of(k)}`" for k in UNIVERSES) + "."], accent="grey", size=S)
    lines = []
    for k in UNIVERSES:
        d = src.decls[st[k]["decls"][0]]
        how = ("its signature" if vp.POLY.search(d["signature"]) else
               "a `variable` of " + d["file"].split("/")[-1])
        lines.append(f"`{anchor_of(k)}` {linked(vp.lean_url(src.full, d['file'], d['line']), code(st[k]['lean'][0]))}: "
                     f"a type in any universe, from {how}")
    h2 = c.card(x0 + cw + G, y, cw, f"The Lean: the same {len(UNIVERSES)}, and no other", lines +
                [f"Every other of the {len([r for r in st.values() if r['decls']])} statements' first Lean theorem "
                 "binds its types in `Type`, the lowest universe, where a binder in the signature overrides a "
                 "`variable` of the file."], accent="teal", size=S)
    y += max(h1, h2) + 40

    # ---- the differences, bullet by bullet
    y += c.heading(x0, y, f"3 · Appendix Q.3, “Statements”: the {len(DIFFERENCES)} differences it lists, quoted")
    ncol = 3
    cw = (c.x1 - x0 - (ncol - 1) * G) / ncol
    specs = []
    for i, b in enumerate(q3["differences"]):
        bullets = ["**Statements** " + (", ".join(f"`{anchor_of(k)}`" for k in b["names"]) or "none named"),
                   "**Lean names** " + (", ".join(lean_link(n) for n in b["lean"]) or "none printed")]
        specs.append(dict(name=f"Difference {i + 1}", accent="grey", say=f"“{vp.abridge(b['text'], 700)}”",
                          bullets=bullets, anchor=f"diff-{i + 1}"))
    for row in range(0, len(specs), ncol):
        chunk = specs[row:row + ncol]
        hh = max(vp.node(c, 0, 0, cw, draw=False, size=S - 0.5, tsize=15, **sp) for sp in chunk)
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (cw + G), y, cw, h=hh, size=S - 0.5, tsize=15, **sp)
        y += hh + G
    y += 10
    y += c.card(x0, y, c.x1 - x0, "Proved in stronger or more general forms (Appendix Q.3)",
                [f"“{q3['stronger']['text']} are proved in stronger or more general forms.”",
                 f"{len(STRONGER)} statements: " + ", ".join(f"`{anchor_of(k)}`" for k in STRONGER) + ". That a form is "
                 "stronger is the paper's statement; this poster checks only that each has a Lean theorem."],
                accent="grey", size=S) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** Whether each difference is as Q.3 says: the build checks that the "
           "statements and names a bullet mentions exist, not what it says of them. A Lean name the text prints without "
           "an underscore (`CutHyp`, `hyperfilter`, `Paper.VPBar`) is not in section 1.", S + 0.5, "muted")
    return c
