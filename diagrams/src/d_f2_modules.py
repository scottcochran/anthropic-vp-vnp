"""F2 — The proof as code: the libraries of the formalization, who imports whom, and the Paper library file by file.

The vp-vnp folder builds seven Lean libraries (lakefile.toml): Statement, Challenge and Solution, one file each; Paper,
whose files state the paper's numbered statements; and Nc, NS1 and Ov, which hold the rest of the proof. This poster
reads every file's imports and declarations at FM_COMMIT and draws the libraries, the imports between them, counted
and then file by file, the Paper library file by file with the section of the paper each file's own docstring names,
and the largest files. A library's counts link to its files on F10, and an import count to its lines in band 3. The
build fails if the files, lines and declarations of a library, the imports between libraries, counted or file by file,
the files of other libraries that import a Paper file, the statements each Paper file declares, or the largest files
differ from what is recorded here, in either direction."""
import collections

import vp
from vp import anchor_of, code, compare, linked
from lib import Canvas

ID, SLUG = "F2", "modules"

W = 3080
S = 13.5
G = 36

ORDER = ["Statement", "Challenge", "Solution", "Paper", "Nc", "NS1", "Ov"]
ACCENT = {"Statement": "violet", "Challenge": "grey", "Solution": "blue", "Paper": "teal", "Nc": "brown",
          "NS1": "amber", "Ov": "pink", "Mathlib": "grey"}
# library -> (files, lines, declarations at the head of a line)
LIBRARY = {"Challenge": (1, 33, 5), "NS1": (29, 7308, 523), "Nc": (236, 46094, 3240), "Ov": (11, 1855, 170),
           "Paper": (44, 17477, 665), "Solution": (1, 55, 7), "Statement": (1, 98, 13)}
# (importing library, imported library, import lines)
IMPORTS = [
    ("Challenge", "Statement", 1), ("NS1", "Mathlib", 2), ("NS1", "NS1", 28), ("NS1", "Nc", 3), ("NS1", "Paper", 2),
    ("Nc", "Mathlib", 23), ("Nc", "NS1", 16), ("Nc", "Nc", 324), ("Nc", "Ov", 6), ("Nc", "Paper", 7),
    ("Ov", "Mathlib", 2), ("Ov", "Ov", 11), ("Ov", "Paper", 1), ("Paper", "NS1", 9), ("Paper", "Nc", 50),
    ("Paper", "Ov", 1), ("Paper", "Paper", 72), ("Solution", "Paper", 1), ("Solution", "Statement", 1),
    ("Statement", "Mathlib", 1),
]
# Every import line between two libraries, as (importing file, imported file); IMPORTS counts them by library.
ACROSS = [
    ('Challenge', 'Statement'), ('NS1.ApproxBack', 'Nc.Acc.Main'), ('NS1.ApproxExtract', 'Nc.Acc.Trie'),
    ('NS1.ApproxRound', 'Nc.Acc.CompK'), ('NS1.ApproxRound', 'Paper.Postpone'), ('NS1.Finite', 'Mathlib'),
    ('NS1.Machine', 'Mathlib'), ('NS1.Scale', 'Paper.Postpone'), ('Nc.Acc.ApproxMain', 'NS1.ApproxMain'),
    ('Nc.Acc.CompK', 'NS1.Util'), ('Nc.Acc.LowDeg', 'Paper.LowDegChains'), ('Nc.Acc.Main', 'NS1.Main'),
    ('Nc.Acc.Trie', 'NS1.Util'), ('Nc.CaseI.Geo', 'Mathlib'), ('Nc.Cat.Core', 'Mathlib'), ('Nc.Cat.Len', 'Mathlib'),
    ('Nc.Cross.Meix', 'Mathlib'), ('Nc.Cross.Split', 'Mathlib'), ('Nc.Cut.Defs', 'Mathlib'), ('Nc.Cut.Play',
    'Mathlib'), ('Nc.Cut.Slp', 'Mathlib'), ('Nc.Cut.Units', 'Mathlib'), ('Nc.Dl.DealThm', 'NS1.Compose'),
    ('Nc.Dl.DealThm', 'NS1.Parts'), ('Nc.Dl.Last', 'NS1.Interp'), ('Nc.Dl.Last', 'NS1.Main'), ('Nc.Dl.Last',
    'Paper.UniversalSteps'), ('Nc.Dl.Names', 'NS1.Picks'), ('Nc.Dl.SizeDeal', 'NS1.Guess'), ('Nc.End.Thm',
    'NS1.Main'), ('Nc.Flag.Act', 'Paper.Toolkit'), ('Nc.Flag.Len', 'Mathlib'), ('Nc.Grp.Lang', 'NS1.Lists'),
    ('Nc.Grp.PutDef', 'NS1.Lists'), ('Nc.Grp.Script', 'NS1.Lists'), ('Nc.LowDegree', 'Mathlib'), ('Nc.PermCoeff',
    'Mathlib'), ('Nc.PermPad', 'Mathlib'), ('Nc.Plus.Interface', 'Mathlib'), ('Nc.Price.Basic', 'Ov.Core.Wire'),
    ('Nc.Price.BorderSum', 'Ov.Core.Wire'), ('Nc.Price.Cover', 'Ov.Core.Spec'), ('Nc.Price.Cover',
    'Ov.Duality.Cert'), ('Nc.Price.Cover', 'Ov.Duality.Minimal'), ('Nc.Price.Cross', 'Paper.Prices'),
    ('Nc.Price.Hyper', 'Paper.Curvature'), ('Nc.Price.Network', 'Paper.Prices'), ('Nc.Rate.Defs', 'Ov.Core.Tensor'),
    ('Nc.Sort.Radix', 'Mathlib'), ('Nc.Tape.Refine', 'Mathlib'), ('Nc.Tape.Rep', 'Mathlib'), ('Nc.Tow.Cst',
    'NS1.Accel'), ('Nc.Tow.Defs', 'Mathlib'), ('Nc.Tow.Rank', 'Mathlib'), ('Nc.Tower.Ring', 'Mathlib'),
    ('Nc.Tower.UT', 'Mathlib'), ('Nc.Uni.Bin', 'Mathlib'), ('Nc.Uni.PM', 'Mathlib'), ('Nc.Uni.Rules', 'NS1.Accel'),
    ('Nc.Vp.Gen', 'Paper.Lengths'), ('Ov.Core.Tensor', 'Mathlib'), ('Ov.Core.Wire', 'Paper.Tensors'),
    ('Ov.Duality.Abstract', 'Mathlib'), ('Paper.Alternative', 'Nc.Flag.Cases'), ('Paper.Alternative',
    'Nc.Flag.Exchange'), ('Paper.ApproxRound', 'NS1.ApproxBack'), ('Paper.ApproxRound', 'NS1.ApproxScale'),
    ('Paper.ApproxScales', 'NS1.ApproxMain'), ('Paper.ApproxScales', 'Nc.Acc.ApproxMain'), ('Paper.ApproxScales',
    'Nc.End.ApproxThm'), ('Paper.Approximate', 'Nc.Rate.Circuit'), ('Paper.Circuit', 'Nc.End.PermThm'),
    ('Paper.CircuitPhi', 'Nc.RunMn'), ('Paper.Convex', 'Nc.CaseI.Cube'), ('Paper.Convex', 'Nc.Price.BorderFew'),
    ('Paper.Crossing', 'Nc.Cross.Data'), ('Paper.Crossing', 'Nc.Price.Cross'), ('Paper.Curvature', 'Nc.Cat.Space'),
    ('Paper.Cuts', 'NS1.OneCut'), ('Paper.Cuts', 'Nc.Dl.GrpCost'), ('Paper.Cuts', 'Nc.Dl.Last'), ('Paper.Fan',
    'Nc.Cat.Window'), ('Paper.Fields', 'Nc.Hc.Vnp'), ('Paper.Flat', 'Nc.CaseI.Lower'), ('Paper.Flat', 'Nc.Vp.Main'),
    ('Paper.Gauges', 'Nc.Price.Cover'), ('Paper.Grids', 'Nc.Hc.Grid'), ('Paper.Groups', 'Nc.Flag.Main'),
    ('Paper.Groups', 'Nc.Vp.Gen'), ('Paper.Heavy', 'Nc.Tow.Slp0'), ('Paper.Identity', 'Nc.Cross.Ident'),
    ('Paper.Laws', 'Nc.Tow.FromPriceK'), ('Paper.Laws', 'Nc.Vp.Main'), ('Paper.Lengths', 'Nc.Flag.Main'),
    ('Paper.Lengths', 'Nc.Flag.Words'), ('Paper.LowDeg', 'Nc.Acc.Main'), ('Paper.LowDeg', 'Nc.Final.CClasses'),
    ('Paper.LowDegChains', 'Nc.Acc.Line'), ('Paper.Means', 'Nc.Cat.Length'), ('Paper.Next', 'NS1.Main'),
    ('Paper.NoAcc', 'NS1.Diag'), ('Paper.NoAcc', 'NS1.Finite'), ('Paper.Pieces', 'Nc.Dl.Cost'), ('Paper.Pieces',
    'Nc.G.Exact'), ('Paper.Postpone', 'NS1.Accel'), ('Paper.Prices', 'Nc.Price.Basic'), ('Paper.Rate',
    'Nc.CaseI.Hub'), ('Paper.Runnet', 'Nc.Dl.Facts'), ('Paper.Runnet', 'Nc.G.Start'), ('Paper.Ryser',
    'Nc.Final.CClasses'), ('Paper.Ryser', 'Nc.Hc.Vnp'), ('Paper.Ryser', 'Nc.PermValiant'), ('Paper.States',
    'Nc.Cross.Count'), ('Paper.Tensors', 'Nc.Rate.Defs'), ('Paper.Tensors', 'Ov.Core.Unit'), ('Paper.Toolkit',
    'Nc.Cat.Core'), ('Paper.Toolkit', 'Nc.Cat.Prod'), ('Paper.Tower', 'Nc.Tow.Cst'), ('Paper.Tower',
    'Nc.Tower.Tower'), ('Paper.Transfer', 'Nc.Rate.Transfer'), ('Paper.Universal', 'NS1.Main'), ('Paper.Universal',
    'Nc.Dl.Cut'), ('Paper.UniversalSteps', 'Nc.Uni.Bounds'), ('Solution', 'Paper.Approximate'), ('Solution',
    'Statement'), ('Statement', 'Mathlib'),
]
# The files outside Paper that import a file of Paper, as (importer, imported).
UPWARD = [
    ("NS1.ApproxRound", "Paper.Postpone"), ("NS1.Scale", "Paper.Postpone"), ("Nc.Acc.LowDeg", "Paper.LowDegChains"),
    ("Nc.Dl.Last", "Paper.UniversalSteps"), ("Nc.Flag.Act", "Paper.Toolkit"), ("Nc.Price.Cross", "Paper.Prices"),
    ("Nc.Price.Hyper", "Paper.Curvature"), ("Nc.Price.Network", "Paper.Prices"), ("Nc.Vp.Gen", "Paper.Lengths"),
    ("Ov.Core.Wire", "Paper.Tensors"), ("Solution", "Paper.Approximate"),
]
# Paper file -> the numbered statements whose first Lean theorem it declares.
STATEMENTS_IN = {
    "Paper.Alternative": 2, "Paper.ApproxScales": 1, "Paper.Approximate": 3, "Paper.Circuit": 1, "Paper.Convex": 3,
    "Paper.Crossing": 1, "Paper.Curvature": 1, "Paper.Cuts": 3, "Paper.Extension": 1, "Paper.Fan": 1,
    "Paper.Fields": 2, "Paper.Flat": 4, "Paper.Gauges": 2, "Paper.Grids": 2, "Paper.Groups": 5, "Paper.HcGrid": 1,
    "Paper.Identity": 1, "Paper.Laws": 2, "Paper.Lengths": 2, "Paper.LowDeg": 1, "Paper.Means": 1, "Paper.Next": 1,
    "Paper.NoAcc": 1, "Paper.Pieces": 1, "Paper.Postpone": 1, "Paper.Prices": 3, "Paper.Rate": 5, "Paper.Runnet": 1,
    "Paper.Scales": 2, "Paper.States": 1, "Paper.Tensors": 2, "Paper.Toolkit": 1, "Paper.Tower": 1,
    "Paper.Transfer": 2, "Paper.Tree": 1, "Paper.Universal": 1,
}
TOP = [("Paper.Tree", 1658), ("Paper.Groups", 1122), ("Paper.Fan", 1016), ("Paper.Alternative", 926),
       ("Paper.Pieces", 884), ("Nc.Dl.SizeDeal", 790), ("Paper.Identity", 741), ("Paper.Flat", 647),
       ("Paper.Gauges", 615), ("Paper.ApproxRound", 586), ("Paper.Cuts", 578), ("NS1.Lists", 573)]


def library_of(src, imp):
    if imp in src.modules:
        return src.modules[imp]["library"]
    if imp.split(".")[0] == "Mathlib":
        return "Mathlib"
    raise ValueError(f"F2: an import of neither a file of vp-vnp nor Mathlib: {imp}")


def build():
    src = vp.load()
    mods = src.modules
    reread = "the Lean files of vp-vnp at FM_COMMIT"
    lib = collections.defaultdict(lambda: [0, 0, 0])
    for d in mods.values():
        t = lib[d["library"]]
        t[0] += 1; t[1] += d["lines"]; t[2] += len(d["decls"])
    compare("F2: files, lines and declarations per library", LIBRARY, {k: tuple(v) for k, v in sorted(lib.items())},
            reread)
    imp = collections.Counter((d["library"], library_of(src, i)) for d in mods.values() for i in d["imports"])
    compare("F2: the imports between libraries", sorted(IMPORTS), sorted((a, b, n) for (a, b), n in imp.items()), reread)
    up = sorted((m, i) for m, d in mods.items() for i in d["imports"]
                if d["library"] != "Paper" and i in mods and mods[i]["library"] == "Paper")
    compare("F2: the files outside Paper that import a Paper file", sorted(UPWARD), up, reread)
    across = sorted((m, i) for m, d in mods.items() for i in d["imports"] if library_of(src, i) != d["library"])
    compare("F2: the import lines between libraries, file by file", ACROSS, across, reread)
    home = collections.defaultdict(list)
    for k, st in src.statements.items():
        if st["decls"]:
            home[src.decls[st["decls"][0]]["module"]].append(k)
    compare("F2: the numbered statements each Paper file declares", STATEMENTS_IN,
            {m: len(v) for m, v in sorted(home.items())}, reread + " and Table 3 of paper.pdf")
    top = sorted(((m, d["lines"]) for m, d in mods.items()), key=lambda t: (-t[1], t[0]))[:len(TOP)]
    compare("F2: the largest files", TOP, top, reread)

    c = Canvas(ID, "The proof as code: the seven Lean libraries of vp-vnp, the imports between them, and the Paper "
               "library file by file",
               f"Read from every Lean file of vp-vnp at formal-math {src.commit}: its imports, its lines, and the "
               "declarations at the head of its lines; the numbered statements are joined to their files through the "
               "paper's Table 3 (src/paper-facts.json). The words in quotation marks are the files' own docstrings.",
               W, sources=f"anthropics/formal-math {src.commit}, vp-vnp/*.lean, vp-vnp/{{Paper,Nc,NS1,Ov}}/**/*.lean, "
               "paper.pdf (Table 3).", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    total = sum(v[1] for v in LIBRARY.values())
    nfiles = sum(v[0] for v in LIBRARY.values())
    c.para(x0, y, c.x1 - x0, f"**How to read it.** {nfiles} files and {total} lines in all. A declaration is counted "
           "where a `theorem`, `lemma`, `def`, `structure` or the like begins a line; nothing is elaborated, so "
           "declarations made by commands or by `where` clauses are not counted. A statement number links to its row "
           "on " + vp.poster("F1") + ". " + vp.NOT_BUILT, S + 0.5, "muted")
    y += 64

    # ---- band 1: the libraries
    y += c.heading(x0, y, "1 · The libraries")
    cw = (c.x1 - x0 - (len(ORDER) - 1) * G) / len(ORDER)
    imported_by = collections.defaultdict(list)
    for (a, b), n in imp.items():
        if a != b:
            imported_by[b].append((a, n))
    role = {"Statement": "the definitions and statements, from Mathlib alone",
            "Challenge": "Solution's theorems with sorry, for Comparator; nothing imports it",
            "Solution": "the five theorems, proved from Paper",
            "Paper": "a file per part of the paper, stating its numbered statements",
            "Nc": "the rest of the proof", "NS1": "the rest of the proof", "Ov": "the rest of the proof"}
    specs = []
    for k in ORDER:
        f, ln, dc = LIBRARY[k]
        out = sorted(((b, n) for (a, b), n in imp.items() if a == k and b != k), key=lambda t: (-t[1], t[0]))
        inn = sorted(imported_by[k], key=lambda t: (-t[1], t[0]))
        # each count opens what it counts: the files on F10, the import lines in band 3
        specs.append(dict(name=k, accent=ACCENT[k], pill=vp.to(f"files-{k}", f"{f} file{'s' if f > 1 else ''}"),
                          bullets=[vp.to(f"files-{k}", f"**{ln} lines**, {dc} declarations"),
                                   f"**Holds** {role[k]} (this poster's words)",
                                   "**Imports** " + (", ".join(f"{vp.library(b)} ({vp.to(f'imp-{k}-{b}', str(n))})"
                                                               for b, n in out) or "nothing outside itself"),
                                   "**Imported by** " + (", ".join(f"{vp.library(a)} ({vp.to(f'imp-{a}-{k}', str(n))})"
                                                                   for a, n in inn) or "nothing")],
                          anchor=f"lib-{k}"))
    hs = [vp.node(c, 0, 0, cw, draw=False, size=S, **sp) for sp in specs]
    for i, sp in enumerate(specs):
        vp.node(c, x0 + i * (cw + G), y, cw, h=max(hs), size=S, **sp)
    y += max(hs) + 30
    n_up = len([u for u in UPWARD if not u[0].startswith("Solution")])
    targets = sorted({b for a, b in UPWARD if not a.startswith("Solution")})
    y += c.card(x0, y, c.x1 - x0, "An interpretation: Paper is not only the top of the proof",
                [f"{n_up} files of Nc, NS1 and Ov import a file of Paper: " + ", ".join(
                    f"`{a}` imports `{b}`" for a, b in UPWARD if not a.startswith("Solution")) + ".",
                 f"So {len(targets)} files of Paper ({', '.join(targets)}) sit below parts of the rest of the proof, and "
                 "the libraries import each other both ways; the files do not. Computed from the imports, and checked "
                 "by `UPWARD`."], accent="amber", size=S) + 50

    # ---- band 2: the import matrix
    y += c.heading(x0, y, "2 · Who imports whom: import lines, by library (a row imports the columns)")
    cols = [("Imports →", 200)] + [(vp.library(b), 150) for b in ORDER + ["Mathlib"]]
    rows = []
    for a in ORDER:
        rows.append([vp.library(a, f"**{a}**")]       # a count opens its lines: band 3, or within a library F10
                    + [vp.to(f"imp-{a}-{b}" if a != b else f"files-{a}", str(imp[(a, b)])) if imp[(a, b)] else ""
                       for b in ORDER + ["Mathlib"]])
    y += c.table(x0, y, cols, rows, size=S) + 50

    # ---- band 3: the import lines between libraries, file by file
    pairs = collections.defaultdict(list)
    for m, i in ACROSS:
        pairs[(mods[m]["library"], library_of(src, i))].append((m, i))
    y += c.heading(x0, y, f"3 · The {len(ACROSS)} import lines between libraries, file by file")
    cols = [("Imports", 300), ("Lines", 80), ("Each importing file, and the file it imports", c.x1 - x0 - 380)]
    def mod(m):
        return vp.to(f"mod-{m}", code(m, 40)) if m in mods else code(m, 40)   # a file's row on F10; Mathlib is not
    rows = [{"cells": [f"{vp.library(a, f'**{a}**')} → {vp.library(b, f'**{b}**')}", str(len(v)),
                       ", ".join(f"{mod(m)} → {mod(i)}" for m, i in v)], "anchor": f"imp-{a}-{b}"}
            for (a, b), v in sorted(pairs.items(),
                                    key=lambda t: (ORDER.index(t[0][0]), (ORDER + ["Mathlib"]).index(t[0][1])))]
    y += c.table(x0, y, cols, rows, size=S - 0.5) + 50

    # ---- band 3: the Paper library, file by file
    y += c.heading(x0, y, "4 · The Paper library, file by file")
    cols = [("File", 300), ("Lines", 90), ("Decl.", 80),
            ("The part of the paper, as the file's docstring names it", 1100),
            ("Numbered statements it declares", 700), ("Imported from outside Paper by", c.x1 - x0 - 2270)]
    rows = []
    for m in sorted(x for x in mods if mods[x]["library"] == "Paper"):
        d = mods[m]
        doc = (d["doc"] or "").split("\n")[0].lstrip("# ").strip()
        stmts = sorted(home.get(m, []), key=vp.order_key)
        by = [a for a, b in UPWARD if b == m]
        rows.append([linked(vp.lean_url(src.full, d["file"]), code(d["file"], 30)), str(d["lines"]), str(len(d["decls"])),
                     f"“{doc}”" if doc else "no docstring",
                     ", ".join(f"`{anchor_of(k)}`" for k in stmts) or "none",
                     ", ".join(f"`{a}`" for a in by)])
    y += c.table(x0, y, cols, rows, size=S - 0.5) + 50

    # ---- band 4: the largest files
    y += c.heading(x0, y, f"5 · The {len(TOP)} largest files, by lines")
    maxl = TOP[0][1]
    bw = c.x1 - x0 - 560
    for m, n in TOP:
        acc = ACCENT[mods[m]["library"]]
        c.text(x0, y + 17, f"`{mods[m]['file']}`", S)
        c.rect(x0 + 400, y + 3, bw * n / maxl, 20, acc, rx=3)
        c.text(x0 + 410 + bw * n / maxl, y + 18, f"{n} lines", S, "muted")
        y += 30
    return c
