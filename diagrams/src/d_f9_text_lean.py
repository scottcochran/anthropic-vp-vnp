"""F9 — The text against the Lean: every use between numbered statements, as the source text shows it (Phase 1) and as
the elaborated Lean shows it (Phase 2), side by side.

Phase 1 read the uses from the Lean source as text (vp.py). Phase 2 built vp-vnp once at
FM_COMMIT, exported Solution's theorems and every Lean theorem of Table 3 with their dependency closure (lean4export),
and read the uses from the elaborated terms (tools/lean-uses/read_export.py, pinned in src/lean-uses.json), which every
other poster that draws uses now reads. This poster sets the two readings against each other, use by use, and says why they differ. The build fails if a use of
either reading is missing from the other other than those recorded here, if the two give a use different kinds, if
the uses only the export shows or the helper behind each change, or if the counts of the export change."""
import collections

import vp
from vp import anchor_of, code, compare, linked
from lib import Canvas

ID, SLUG = "F9", "text-lean"

W = 3080
S = 13.5
G = 30

EXPORT_ONLY = [('Definition A.1', 'Proposition A.8', 'through'), ('Definition A.1', 'Proposition B.3', 'through'),
 ('Definition A.1', 'Theorem C.1', 'through'), ('Lemma A.2', 'Theorem C.1', 'through'),
 ('Definition A.1', 'Lemma C.2', 'through'), ('Lemma A.2', 'Lemma C.2', 'through'),
 ('Definition A.1', 'Proposition C.3', 'through'), ('Lemma A.2', 'Proposition C.3', 'through'),
 ('Definition A.1', 'Theorem D.2', 'through'), ('Lemma A.2', 'Theorem D.2', 'through'),
 ('Definition A.1', 'Proposition E.5', 'through'), ('Definition A.1', 'Lemma E.7', 'through'),
 ('Definition A.1', 'Lemma E.8', 'through'), ('Lemma A.2', 'Lemma E.8', 'through'),
 ('Definition A.1', 'Proposition E.9', 'through'), ('Definition A.1', 'Proposition E.10', 'through'),
 ('Lemma F.2', 'Theorem F.6', 'through'), ('Definition A.1', 'Theorem G.2', 'through'),
 ('Lemma A.2', 'Theorem G.2', 'through'), ('Lemma F.2', 'Theorem G.2', 'through'),
 ('Lemma F.2', 'Proposition H.1', 'through'), ('Lemma K.4', 'Proposition K.5', 'through'),
 ('Definition A.1', 'Lemma N.3', 'through'), ('Definition A.1', 'Theorem N.5', 'through')]
# For each, the first declaration outside the Paper library on its shortest chain: why the text reading, which walks
# only through Paper's helpers, does not see it.
OUTSIDE = {('Definition A.1', 'Lemma C.2'): 'Nc.Price.IsPrice.self',
 ('Definition A.1', 'Lemma E.7'): 'Nc.Price.few',
 ('Definition A.1', 'Lemma E.8'): 'Ov.Spec.e_self',
 ('Definition A.1', 'Lemma N.3'): 'Nc.Price.few',
 ('Definition A.1', 'Proposition A.8'): 'Nc.Price.IsPrice.nonneg',
 ('Definition A.1', 'Proposition B.3'): 'Ov.Spec.e_nonneg',
 ('Definition A.1', 'Proposition C.3'): 'Nc.Price.IsPrice.self',
 ('Definition A.1', 'Proposition E.10'): 'Ov.Spec.wire_eq',
 ('Definition A.1', 'Proposition E.5'): 'Ov.Spec.wire_eq',
 ('Definition A.1', 'Proposition E.9'): 'Nc.Price.hexp_le_of_two',
 ('Definition A.1', 'Theorem C.1'): 'Nc.Price.IsPrice.nonneg',
 ('Definition A.1', 'Theorem D.2'): 'Nc.Price.IsPrice.self',
 ('Definition A.1', 'Theorem G.2'): 'Nc.Price.IsPrice.symm',
 ('Definition A.1', 'Theorem N.5'): 'Ov.Spec.wire_eq',
 ('Lemma A.2', 'Lemma C.2'): 'Nc.Price.IsPrice.self',
 ('Lemma A.2', 'Lemma E.8'): 'Nc.Price.IsPrice.nonneg',
 ('Lemma A.2', 'Proposition C.3'): 'Nc.Price.IsPrice.self',
 ('Lemma A.2', 'Theorem C.1'): 'Nc.Price.IsPrice.nonneg',
 ('Lemma A.2', 'Theorem D.2'): 'Nc.Price.IsPrice.self',
 ('Lemma A.2', 'Theorem G.2'): 'Nc.Price.IsPrice.symm',
 ('Lemma F.2', 'Proposition H.1'): 'Nc.Flag.mem_of_x',
 ('Lemma F.2', 'Theorem F.6'): 'Nc.Flag.mem_of_x',
 ('Lemma F.2', 'Theorem G.2'): 'Nc.Flag.const_of_x',
 ('Lemma K.4', 'Proposition K.5'): 'NS1.round'}
TEXT_ONLY = []
KIND_DIFFERS = []
LEAN_COUNTS = {"declarations": 63346, "direct": 41, "library": 53351, "uses": 124, "vp_vnp": 9995}
# Uses between sections that only the export adds (to R2's matrix, which reads the text).
SECTIONS_ADDED = [("A", "D"), ("F", "H")]
# The second Lean reading, the compiled modules read by Lean itself (src/lean-modules.json).
MODULES_COUNTS = {"direct": 41, "modules": 321, "uses": 124, "vp_vnp": 13561}
# Uses the two Lean readings give differently, or that only one gives: none.
READINGS_DIFFER = []
# The export's rule for vp-vnp's own constants, by name, against the modules': names it takes for vp-vnp's that a
# library defines (none), and how many of vp-vnp's constants it does not take (compiler-made: derived instances,
# equation lemmas).
RULE_FALSE = []
RULE_MISSED = 480
# Statements under whose Lean theorems the modules find more declarations than the export: (declarations, their lines,
# declarations the export finds and the modules do not). Reached through the constants the rule misses.
UNDER_DIFFERS = {"Corollary L.3": (2, 16, 0), "Corollary M.4": (2, 16, 0), "Proposition A.5": (7, 35, 0),
                 "Proposition A.7": (3, 11, 0), "Theorem A.6": (3, 11, 0), "Theorem G.2": (4, 15, 0)}


def sec(k):
    return k.split(" ", 1)[1].strip("()")[0]


def build():
    src = vp.load()
    st = src.statements
    lean = src.lean
    T = {(u, k): h for k in st for u, h in src.uses[k].items()}
    E = {(u, k): h for k, v in lean["uses"].items() for u, h in v.items()}
    reread = "src/lean-uses.json (tools/lean-uses/) and the Lean source at FM_COMMIT"
    compare("F9: the counts of the export", LEAN_COUNTS, lean["counts"], reread)
    compare("F9: the uses only the text shows", TEXT_ONLY, sorted(e for e in T if e not in E), reread)
    compare("F9: the uses the two readings give different kinds", KIND_DIFFERS,
            sorted((u, k, T[(u, k)], E[(u, k)]) for (u, k) in T if (u, k) in E and T[(u, k)] != E[(u, k)]), reread)
    eonly = sorted(((u, k, E[(u, k)]) for (u, k) in E if (u, k) not in T),
                   key=lambda t: (vp.order_key(t[1]), vp.order_key(t[0])))
    compare("F9: the uses only the export shows", EXPORT_ONLY, eonly, reread)
    outside = {(u, k): next(n for n in lean["chains"][k][u][1:-1] if n.split(".")[0] != "Paper")
               for u, k, _ in eonly}
    compare("F9: the declaration outside Paper behind each", OUTSIDE, outside, reread)
    if lean["absent"]:
        raise ValueError(f"F9: Table 3 names not in the export: {lean['absent']}")
    secT = {(sec(u), sec(k)) for u, k in T if sec(u) != sec(k)}
    secE = {(sec(u), sec(k)) for u, k in E if sec(u) != sec(k)}
    compare("F9: the uses between sections only the export adds", SECTIONS_ADDED, sorted(secE - secT), reread)
    t1 = {(u, r["section"]) for r in src.facts["table1"] for u in r["uses"]}
    m = src.lean_meta
    mods = src.lean_modules
    compare("F9: the counts of the module reading", MODULES_COUNTS, mods["counts"], "src/lean-modules.json")
    Mu = {(u, k): h for k, v in mods["uses"].items() for u, h in v.items()}
    compare("F9: the uses the two Lean readings give differently", READINGS_DIFFER,
            sorted({(u, k, E.get((u, k)), Mu.get((u, k))) for (u, k) in set(E) | set(Mu) if E.get((u, k)) != Mu.get((u, k))}),
            "src/lean-uses.json and src/lean-modules.json")
    compare("F9: constants the export's rule takes for vp-vnp's that a library defines", RULE_FALSE,
            mods["rule"]["by_name_not_by_module"], "src/lean-modules.json")
    compare("F9: vp-vnp's constants the export's rule does not take", RULE_MISSED,
            len(mods["rule"]["by_module_not_by_name"]), "src/lean-modules.json")
    under = {}
    for k in lean["under"]:
        extra = set(mods["under"][k]) - set(lean["under"][k])
        fewer = set(lean["under"][k]) - set(mods["under"][k])
        if extra or fewer:
            under[k] = (len(extra), sum(src.decls[n]["lines"] for n in extra), len(fewer))
    compare("F9: where the two Lean readings find different declarations under a statement", UNDER_DIFFERS, under,
            "src/lean-uses.json and src/lean-modules.json")

    def lean_link(n):
        d = src.decls.get(n)
        return linked(vp.lean_url(src.full, d["file"], d["line"]), code(n, 40)) if d else code(n, 40)

    c = Canvas(ID, "The text against the Lean: every use between the numbered statements, as the source text shows it "
               "and as the elaborated Lean shows it",
               f"The text reading is Phase 1's, from the Lean source of vp-vnp at formal-math {src.commit}. The Lean "
               f"reading is Phase 2's: vp-vnp built at that commit with Lean {m['lean']['version']}, Solution's theorems and "
               f"every Lean theorem of Table 3 exported with their dependency closure by lean4export "
               f"{m['exporter']['version']}, and the uses read from the elaborated terms (src/lean-uses.json).", W,
               sources=f"anthropics/formal-math {src.commit}; its export, {m['export_lines']} lines, sha256 "
               f"{m['export_sha256'][:16]}… (tools/lean-uses/meta.json); paper.pdf (Table 1, Table 3).",
               state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    same = len([e for e in T if e in E])
    c.para(x0, y, c.x1 - x0, "**How to read it.** Both readings walk from a statement's Lean theorems through the "
           "declarations that belong to no statement, and stop at another statement's theorem: a use, direct when one "
           "of the statement's own theorems refers to it. The text reading matches names in the source and walks "
           "only through the Paper library's helpers; the Lean reading follows the constants of the elaborated terms "
           "through every declaration of vp-vnp. The Lean reading is the build's own and is not a check that the "
           "proofs are correct: that is the claim of the formal-math repository's CI.", S + 0.5, "muted")
    y += 70

    cw = (c.x1 - x0 - 3 * G) / 4
    cards = [
        ("The text reading, confirmed", "teal",
         [f"All {len(T)} uses the text shows are in the Lean reading, {same} of {len(T)}, and each of the same kind: "
          f"{sum(1 for h in T.values() if h == 'direct')} direct, {sum(1 for h in T.values() if h != 'direct')} "
          "through helpers.", f"No use is only in the text (`TEXT_ONLY` is empty)."]),
        (f"{len(EXPORT_ONLY)} uses only the Lean shows", "violet",
         [f"All {len(EXPORT_ONLY)} are through helpers, and on the shortest chain of each lies a declaration outside the "
          f"Paper library ({', '.join(sorted({n.split('.')[0] for n in OUTSIDE.values()}))}), which the text reading "
          "does not walk: so where the text reading walks explains each (`OUTSIDE`).",
          "They reach mostly Definition A.1 and Lemma A.2, through the price lemmas of Nc.Price and Ov.Spec."]),
        ("Table 1, read again", "amber",
         [f"Of Table 1's {len(t1)} uses between sections the Lean reading bears out {len(t1 & secE)}, the same as the "
          f"text reading ({len(t1 & secT)}): the other {len(t1 - secE)} are uses the elaborated Lean does not make "
          "either.", "It adds " + ", ".join(f"{a}→{b}" for a, b in SECTIONS_ADDED) + " to the uses Table 1 does not "
          "list (R2 draws the Lean reading's)."]),
        ("A second Lean reading: the compiled modules", "blue",
         [f"Read by Lean itself from the built modules ({mods['counts']['vp_vnp']} constants of vp-vnp, "
          "tools/lean-uses/ReadModules.lean): the same "
          f"{mods['counts']['uses']} uses, each of the same kind ({mods['counts']['direct']} direct). "
          "No use differs (`READINGS_DIFFER`).",
          f"The export's rule for what is vp-vnp's, by name, takes nothing a library defines, and misses "
          f"{RULE_MISSED} compiler-made constants (derived instances, equation lemmas). Through them the modules find "
          f"a few more declarations under {len(UNDER_DIFFERS)} statements, at most "
          f"{max(v[0] for v in UNDER_DIFFERS.values())} ({', '.join(f'`{anchor_of(k)}`' for k in UNDER_DIFFERS)}); "
          "F3 and F5 draw the export's."]),
    ]
    hs = [c.card(0, 0, cw, t, b, accent=a, size=S + 0.5, draw=False) for t, a, b in cards]
    for i, (t, a, b) in enumerate(cards):
        c.card(x0 + i * (cw + G), y, cw, t, b, accent=a, size=S + 0.5, h=max(hs))
    y += max(hs) + 40

    y += c.heading(x0, y, f"The {len(EXPORT_ONLY)} uses only the Lean shows, each with a shortest chain")
    cols = [("Use", 330), ("The chain of declarations, from the user's theorem to the used one",
                           c.x1 - x0 - 330 - 420), ("Outside Paper", 420)]
    rows = []
    for u, k, h in EXPORT_ONLY:
        chain = lean["chains"][k][u]
        rows.append({"cells": [f"`{anchor_of(k)}` uses `{anchor_of(u)}`", " → ".join(lean_link(n) for n in chain),
                               code(OUTSIDE[(u, k)], 40)], "accent": "violet"})
    y += c.table(x0, y, cols, rows, size=S - 0.5) + 40

    y += c.heading(x0, y, "Every statement's uses, in both readings")
    cols = [("Statement", 260), ("Uses in both readings (text ✓ Lean ✓)", 1700), ("Only in the Lean", c.x1 - x0 - 1960)]
    rows = []
    for k in sorted(st, key=vp.order_key):
        bothl = [u for u in src.uses[k] if (u, k) in E]
        lonly = [u for u, kk, _ in EXPORT_ONLY if kk == k]
        if not bothl and not lonly:
            continue
        rows.append([f"`{anchor_of(k)}`", ", ".join(f"`{anchor_of(u)}`" + ("" if T[(u, k)] == "direct" else " via")
                                                    for u in bothl) or "none",
                     ", ".join(f"`{anchor_of(u)}`" for u in lonly) or ""])
    y += c.table(x0, y, cols, rows, size=S - 0.5) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** That a use is one the proof needs: the walk follows every constant of "
           "a term, including those in its type. That the rule which says a constant is vp-vnp's own (a name the source "
           "declares, one extending it, or a private name of one of its modules) is complete: a declaration vp-vnp makes "
           f"under a library's name would be read as the library's. The export ({m['export_lines']} lines) is not in "
           "this repository; tools/lean-uses/README.md says how to make it again.", S + 0.5, "muted")
    return c
