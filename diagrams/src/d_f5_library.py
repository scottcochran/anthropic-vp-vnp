"""F5 — Where the formal work is: the 25 directories of the libraries under Paper (Nc, NS1, Ov), each set against
the sections of the paper whose statements reach it.

Three quarters of the Lean is outside the Paper library. This poster reads every declaration of Nc, NS1 and Ov at
FM_COMMIT, groups them by directory, and for each section of the paper takes the declarations its numbered
statements reach in the elaborated Lean (src/lean-uses.json: every constant of their terms, stopping at the theorems
of other statements), so that a cell is the formal work a section's own statements stand on in a directory. It also
measures how much of each directory no statement's proof uses at all. The build fails if any directory's files, lines or
declaration lines, any cell, or any directory's reached lines differ from what is recorded here, in either
direction."""
import collections

import vp
from vp import compare
from lib import Canvas, light

ID, SLUG = "F5", "library"

W = 3080
S = 13.5
G = 30
LIB_ACCENT = {"Nc": "brown", "NS1": "amber", "Ov": "pink"}

# directory -> (files, lines, lines of the declarations at the head of a line)
DIRS = {
    'Nc.Tow': (37, 8860, 7427),
    'NS1': (29, 7308, 6405),
    'Nc.Grp': (28, 6382, 5501),
    'Nc.Dl': (22, 5297, 4500),
    'Nc.Uni': (20, 4878, 4337),
    'Nc.Flag': (16, 2452, 2072),
    'Nc': (15, 2443, 1889),
    'Nc.Tower': (11, 2348, 2082),
    'Nc.G': (7, 2019, 1698),
    'Nc.Acc': (8, 1652, 1440),
    'Nc.Cut': (12, 1635, 1235),
    'Ov.Core': (7, 1429, 1132),
    'Nc.Price': (10, 1218, 913),
    'Nc.Tape': (8, 1212, 984),
    'Nc.Cat': (7, 1088, 907),
    'Nc.Hc': (3, 977, 821),
    'Nc.Cross': (9, 855, 606),
    'Nc.Sort': (4, 771, 661),
    'Nc.CaseI': (6, 765, 610),
    'Nc.Rate': (4, 450, 296),
    'Ov.Duality': (4, 426, 300),
    'Nc.End': (4, 324, 236),
    'Nc.Final': (1, 234, 186),
    'Nc.Vp': (2, 193, 147),
    'Nc.Plus': (2, 41, 7),
}
# directory -> the declaration lines under some numbered statement's Lean theorems in the elaborated Lean
REACHED = {'Nc.Tow': 7427,
 'NS1': 6399,
 'Nc.Grp': 5501,
 'Nc.Dl': 4500,
 'Nc.Uni': 4337,
 'Nc.Flag': 2072,
 'Nc': 1875,
 'Nc.Tower': 2078,
 'Nc.G': 1698,
 'Nc.Acc': 1440,
 'Nc.Cut': 1235,
 'Ov.Core': 1124,
 'Nc.Price': 913,
 'Nc.Tape': 984,
 'Nc.Cat': 907,
 'Nc.Hc': 821,
 'Nc.Cross': 606,
 'Nc.Sort': 661,
 'Nc.CaseI': 610,
 'Nc.Rate': 279,
 'Ov.Duality': 300,
 'Nc.End': 236,
 'Nc.Final': 181,
 'Nc.Vp': 147,
 'Nc.Plus': 7}
# section -> directory -> the declaration lines its numbered statements reach there (each declaration once a section)
MATRIX = {'A': {'Ov.Core': 1008, 'Nc.Price': 174, 'Nc.Rate': 5, 'Ov.Duality': 300},
 'B': {'Ov.Core': 517, 'Nc.Price': 136, 'Nc.Cross': 606, 'Nc.Rate': 5},
 'C': {'Ov.Core': 258, 'Nc.Price': 32, 'Nc.Cat': 875},
 'D': {'Nc.Flag': 623, 'Ov.Core': 258, 'Nc.Price': 32, 'Nc.Cat': 4},
 'E': {'Nc.Flag': 4, 'Nc': 544, 'Ov.Core': 954, 'Nc.Price': 449, 'Nc.CaseI': 610, 'Nc.Rate': 18, 'Nc.Final': 11},
 'F': {'Nc.Flag': 1538, 'Nc.Tower': 122, 'Ov.Core': 30, 'Nc.Price': 9, 'Nc.Cat': 66, 'Nc.Vp': 125},
 'G': {'Nc.Tow': 70,
       'Nc.Flag': 34,
       'Nc.Tower': 167,
       'Nc.G': 43,
       'Ov.Core': 617,
       'Nc.Price': 315,
       'Nc.Rate': 5,
       'Ov.Duality': 33,
       'Nc.Vp': 142},
 'H': {'Nc.Tow': 7344,
       'NS1': 4,
       'Nc.Flag': 32,
       'Nc': 278,
       'Nc.Tower': 2045,
       'Nc.G': 1306,
       'Nc.Cut': 388,
       'Nc.Vp': 136,
       'Nc.Plus': 4},
 'I': {'NS1': 159, 'Nc.Dl': 84, 'Nc.Uni': 4337, 'Nc.G': 285, 'Nc.Cut': 870, 'Nc.Tape': 982, 'Nc.Sort': 661},
 'J': {'Nc.Tow': 271,
       'NS1': 2961,
       'Nc.Grp': 5501,
       'Nc.Dl': 4425,
       'Nc.Flag': 4,
       'Nc': 240,
       'Nc.Tower': 167,
       'Nc.G': 459,
       'Nc.Cut': 379,
       'Ov.Core': 30,
       'Nc.Price': 9,
       'Nc.Tape': 49,
       'Nc.Vp': 6,
       'Nc.Plus': 7},
 'K': {'NS1': 3426,
       'Nc.Dl': 4,
       'Nc.Flag': 4,
       'Nc': 1149,
       'Nc.Acc': 1326,
       'Ov.Core': 30,
       'Nc.Price': 9,
       'Nc.Tape': 31,
       'Nc.Rate': 8,
       'Nc.End': 183,
       'Nc.Final': 21},
 'L': {'Nc.Flag': 8, 'Nc': 11, 'Ov.Core': 30, 'Nc.Price': 9, 'Nc.Hc': 10, 'Nc.Final': 159},
 'M': {'NS1': 122,
       'Nc.Flag': 8,
       'Nc': 101,
       'Ov.Core': 30,
       'Nc.Price': 9,
       'Nc.Hc': 821,
       'Nc.CaseI': 11,
       'Nc.Rate': 66,
       'Nc.End': 32,
       'Nc.Final': 170},
 'N': {'NS1': 3479,
       'Nc.Dl': 4,
       'Nc.Flag': 8,
       'Nc': 1149,
       'Nc.Acc': 371,
       'Ov.Core': 620,
       'Nc.Price': 324,
       'Nc.Tape': 31,
       'Nc.Hc': 237,
       'Nc.CaseI': 237,
       'Nc.Rate': 279,
       'Nc.End': 236,
       'Nc.Final': 170}}


dir_of = vp.dir_of   # as F10 groups the files


def build():
    src = vp.load()
    reread = "src/lean-uses.json (under) and the Lean files of Nc, NS1 and Ov at FM_COMMIT"
    dirs = collections.defaultdict(lambda: [0, 0, 0])
    for m, d in src.modules.items():
        if d["library"] in LIB_ACCENT:
            t = dirs[dir_of(m)]
            t[0] += 1; t[1] += d["lines"]
    for n, d in src.decls.items():
        if d["module"].split(".")[0] in LIB_ACCENT:
            dirs[dir_of(d["module"])][2] += d["lines"]
    compare("F5: files, lines and declaration lines per directory", DIRS,
            {k: tuple(v) for k, v in sorted(dirs.items(), key=lambda t: (-t[1][1], t[0]))}, reread)
    by_sec = collections.defaultdict(set)
    reached = set()
    for k, st in src.statements.items():
        if st["decls"]:
            cl = src.lean_under[k]
            by_sec[st["section"]] |= cl
            reached |= cl
    matrix = {}
    for sec in sorted(by_sec):
        row = collections.Counter()
        for n in by_sec[sec]:
            dd = dir_of(src.decls[n]["module"])
            if dd in DIRS:
                row[dd] += src.decls[n]["lines"]
        if row:
            matrix[sec] = {dd: row[dd] for dd in DIRS if row[dd]}
    compare("F5: the lines each section's statements reach in each directory", MATRIX, matrix, reread)
    got = collections.Counter()
    for n in reached:
        dd = dir_of(src.decls[n]["module"])
        if dd in DIRS:
            got[dd] += src.decls[n]["lines"]
    compare("F5: the declaration lines of each directory that some statement reaches", REACHED,
            {dd: got[dd] for dd in DIRS}, reread)
    t1 = {r["section"]: r for r in src.facts["table1"]}
    home = {}
    for dd in DIRS:
        col = {sec: MATRIX[sec].get(dd, 0) for sec in MATRIX}
        tot = sum(col.values())
        best = max(sorted(col), key=lambda sec: col[sec])
        home[dd] = (best, col[best], tot)
    heads = collections.defaultdict(list)
    for m, d in sorted(src.modules.items(), key=lambda t: (-t[1]["lines"], t[0])):
        if d["library"] in LIB_ACCENT and d["doc"]:
            h = d["doc"].split("\n")[0].lstrip("# ").strip()
            if h:
                heads[dir_of(m)].append(h)

    c = Canvas(ID, f"Where the formal work is: the {len(DIRS)} directories of Nc, NS1 and Ov, set against the "
               "sections of the paper whose statements reach them",
               f"Read from the Lean source of vp-vnp at formal-math {src.commit}. A cell is the lines of the "
               "declarations in a directory that a section's numbered statements reach in the elaborated Lean, before "
               "another statement's theorem: the formal work that section's own statements stand on there. The words "
               "in quotation marks are the files' docstrings.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/{{Nc,NS1,Ov}}/**/*.lean, vp-vnp/Paper/*.lean, "
               "paper.pdf (Table 1, Table 3).", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    total = sum(v[2] for v in DIRS.values())
    nreach = sum(REACHED.values())
    c.para(x0, y, c.x1 - x0, f"**How to read it.** The {sum(v[1] for v in DIRS.values())} lines of {vp.library('Nc')}, "
           f"{vp.library('NS1')} and {vp.library('Ov')} "
           f"hold {total} lines of declarations; {nreach} of them ({100 * nreach / total:.1f}%) lie under some "
           "numbered statement's Lean theorems in the elaborated Lean. The rest no statement's proof uses at all. "
           "Each directory card names its home, the section whose statements reach most of it. " + vp.NOT_BUILT_LEAN, S + 0.5, "muted")
    y += 70

    # ---- the matrix
    y += c.heading(x0, y, "Section against directory: the lines each section's own statements reach")
    order = list(DIRS)
    head = 330
    cw = (c.x1 - x0 - head) / len(order)
    for j, dd in enumerate(order):
        lib = dd.split(".")[0]
        lab = dd.split(".")[1] if "." in dd else ("(top)" if dd == "Nc" else dd)
        c.text(x0 + head + j * cw + cw / 2, y + 14, lib if dd != "NS1" else "", 11.5, "faint", anchor="middle")
        c.text(x0 + head + j * cw + cw / 2, y + 32, lab, 13, LIB_ACCENT[lib], anchor="middle", bold=True)
    y += 44
    rh = 34
    vmax = max(v for row in MATRIX.values() for v in row.values())
    for i, sec in enumerate(sorted(MATRIX)):
        ry = y + i * rh
        c.rect(x0, ry, c.x1 - x0, rh, "line", tint=False, rx=0, sw=0.6, fill_token="bg" if i % 2 == 0 else "zebra")
        acc = vp.CASE_ACCENT[t1[sec]["case"]]
        c.text(x0 + 10, ry + 22, f"**{sec}** {vp.abridge(t1[sec]['what'], 34)}", 12.5, acc)
        for j, dd in enumerate(order):
            v = MATRIX[sec].get(dd)
            if not v:
                continue
            cx = x0 + head + j * cw
            op = 0.18 + 0.82 * (v / vmax) ** 0.5
            lib = dd.split(".")[0]
            c.add(f'<rect x="{cx + 3:.1f}" y="{ry + 3:.1f}" width="{cw - 6:.1f}" height="{rh - 6}" rx="4" '
                  f'fill="{light(LIB_ACCENT[lib])}" class="f-{LIB_ACCENT[lib]}" fill-opacity="{op:.2f}"/>', ry + rh)
            c.text(cx + cw / 2, ry + 22, str(v), 12, "ink", anchor="middle", bold=home[dd][0] == sec)
    nrows = len(MATRIX)
    c.blocks.append((x0, y, c.x1, y + nrows * rh, "table matrix"))
    y += nrows * rh + 16
    c.para(x0, y, c.x1 - x0, "A cell's shade grows with its lines (by their square root); the number in bold is the "
           "directory's home. A declaration reached by two sections counts in both rows.", S, "muted")
    y += 50

    # ---- the directories
    y += c.heading(x0, y, f"The {len(DIRS)} directories, largest first")
    ncol = 5
    wcard = (c.x1 - x0 - (ncol - 1) * G) / ncol
    specs = []
    for dd in order:
        f, ln, dl = DIRS[dd]
        best, bl, tot = home[dd]
        share = f"{100 * bl / tot:.0f}%" if tot else "—"
        hs = heads.get(dd, [])[:3]
        specs.append(dict(
            name=dd if dd != "Nc" else "Nc, files at the top", accent=LIB_ACCENT[dd.split(".")[0]], pill=f"home {best} · {share}",
            bullets=[vp.to(vp.files_id(dd), f"**{f} files**, {ln} lines, {dl} in declarations"),   # the files on F10
                     f"**Under a statement** {REACHED[dd]} of {dl} declaration lines ({100 * REACHED[dd] / dl:.1f}%)",
                     f"**Home** Section {best}, “{vp.abridge(t1[best]['what'], 60)}”: {bl} of the {tot} lines "
                     "the sections reach here"]
            + [f"“{h}”" for h in hs], anchor=f"dir-{dd.replace('.', '-')}"))
    for row in range(0, len(specs), ncol):
        chunk = specs[row:row + ncol]
        hh = max(vp.node(c, 0, 0, wcard, draw=False, size=S - 0.5, tsize=16, **sp) for sp in chunk)
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (wcard + G), y, wcard, h=hh, size=S - 0.5, tsize=16, **sp)
        y += hh + G
    y += 10

    # ---- the interpretation, computed
    strong = [dd for dd in order if home[dd][2] and home[dd][1] / home[dd][2] >= 0.8]
    shared = [dd for dd in order if home[dd][2] and home[dd][1] / home[dd][2] < 0.5]
    unused = sorted(((DIRS[dd][2] - REACHED[dd], dd) for dd in order if DIRS[dd][2] > REACHED[dd]), key=lambda t: (-t[0], t[1]))
    y += c.card(x0, y, c.x1 - x0, "An interpretation: most directories belong to one section",
                [f"In {len(strong)} of the {len(DIRS)} directories one section's statements reach at least 80% of the "
                 "lines the sections reach there: " + ", ".join(f"{dd} ({home[dd][0]})" for dd in strong) + ". "
                 f"In {len(shared)} no section reaches half: " + ", ".join(f"{dd}" for dd in shared) + ", shared work.",
                 f"Under no statement: {sum(n for n, _ in unused)} declaration lines in all, in {len(unused)} directories, "
                 "most in " + ", ".join(f"{dd} ({n})" for n, dd in unused[:3]) + ".",
                 "Computed from `MATRIX`, `REACHED` and `DIRS`, which the build checks."], accent="amber",
                size=S + 0.5) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** Whether a declaration under a statement is needed: a constant counts "
           "wherever it stands in a term, its type included. A "
           "directory's home is where the most lines are reached, which says where its code is used from, not what "
           "it is about; its docstrings say that.", S + 0.5, "muted")
    return c
