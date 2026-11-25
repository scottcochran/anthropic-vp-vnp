"""F10 — The proof file by file: every Lean file of vp-vnp, by library and directory, its declarations and imports.

F2 counts the files, lines and declarations of each library, and F5 those of each directory of Nc, NS1 and Ov; this
poster lists what they count. A row is one file at FM_COMMIT: its lines, the declarations at the head of its lines
(each linked to its line), the files of vp-vnp it imports and the files that import it (each linked to its row). A
header row stands before each library and each directory, with its counts; F2's library cards and F5's directory cards
link to it. The build fails if the files, lines and declarations of a library or a directory differ from GROUPS, in
either direction."""
import collections

import vp
from vp import code, compare, linked
from lib import Canvas

ID, SLUG = "F10", "files"

W = 3080
S = 12.5

ORDER = ["Statement", "Challenge", "Solution", "Paper", "Nc", "NS1", "Ov"]
ACCENT = {"Statement": "violet", "Challenge": "grey", "Solution": "blue", "Paper": "teal", "Nc": "brown",
          "NS1": "amber", "Ov": "pink"}
# library, or directory (vp.dir_of; Nc-top for the files at the top of Nc) -> (files, lines, declarations at the head
# of a line, Challenge's counted from the file, since vp.load keeps them apart from Solution's)
GROUPS = {
    "Challenge": (1, 33, 5), "NS1": (29, 7308, 523), "Nc": (236, 46094, 3240), "Nc-top": (15, 2443, 172),
    "Nc.Acc": (8, 1652, 119), "Nc.CaseI": (6, 765, 65), "Nc.Cat": (7, 1088, 96), "Nc.Cross": (9, 855, 76),
    "Nc.Cut": (12, 1635, 89), "Nc.Dl": (22, 5297, 294), "Nc.End": (4, 324, 17), "Nc.Final": (1, 234, 24),
    "Nc.Flag": (16, 2452, 218), "Nc.G": (7, 2019, 125), "Nc.Grp": (28, 6382, 416), "Nc.Hc": (3, 977, 71),
    "Nc.Plus": (2, 41, 2), "Nc.Price": (10, 1218, 86), "Nc.Rate": (4, 450, 24), "Nc.Sort": (4, 771, 57),
    "Nc.Tape": (8, 1212, 93), "Nc.Tow": (37, 8860, 538), "Nc.Tower": (11, 2348, 251), "Nc.Uni": (20, 4878, 396),
    "Nc.Vp": (2, 193, 11), "Ov": (11, 1855, 170), "Ov.Core": (7, 1429, 132), "Ov.Duality": (4, 426, 38),
    "Paper": (44, 17477, 665), "Solution": (1, 55, 7), "Statement": (1, 98, 13),
}


def plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def build():
    src = vp.load()
    mods = src.modules
    reread = "the Lean files of vp-vnp at FM_COMMIT"
    decls = collections.defaultdict(list)          # module -> its declarations, in the order of their lines
    for d in list(src.decls.values()) + list(src.challenge.values()):
        decls[d["module"]].append(d)
    for v in decls.values():
        v.sort(key=lambda d: d["line"])
    def group_of(m):
        dd = vp.dir_of(m)
        return f"{dd}-top" if dd in ("Nc", "Ov") else dd
    groups = collections.defaultdict(lambda: [0, 0, 0])
    for m, d in mods.items():
        for k in {d["library"], group_of(m)}:
            t = groups[k]
            t[0] += 1; t[1] += d["lines"]; t[2] += len(decls[m])
    compare("F10: files, lines and declarations per library and directory", GROUPS,
            {k: tuple(v) for k, v in sorted(groups.items())}, reread)
    imported_by = collections.defaultdict(list)
    for m, d in mods.items():
        for i in d["imports"]:
            imported_by[i].append(m)

    nfiles, nlines = len(mods), sum(d["lines"] for d in mods.values())
    ndecls = sum(len(v) for v in decls.values())
    c = Canvas(ID, f"The proof file by file: the {nfiles} Lean files of vp-vnp, by library and directory, each with "
               "its declarations and its imports",
               f"Read from every Lean file of vp-vnp at formal-math {src.commit}: its lines, the declarations at the "
               "head of its lines, and its imports. A row is one file; a header row stands before each library and "
               "each directory, with the counts that " + vp.poster("F2") + "'s library cards and " + vp.poster("F5") +
               "'s directory cards give, and link to.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/*.lean, vp-vnp/{{Paper,Nc,NS1,Ov}}/**/*.lean.",
               state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    c.para(x0, y, c.x1 - x0, f"**How to read it.** {nfiles} files, {nlines} lines and {ndecls} declarations in all. A "
           "declaration is counted where a `theorem`, `lemma`, `def`, `structure` or the like begins a line, as on "
           + vp.poster("F2") + "; nothing is elaborated, so declarations made by commands or by `where` clauses are "
           "not counted. Each declaration links to its line in formal-math at the pin, named without its library's "
           "prefix (`Nc.`, `Paper.`, …) where it has one. Each file of vp-vnp in **Imports** and **Imported by** "
           "links to its row here; `Mathlib` is named, not linked. Nc's files are grouped by the directories " +
           vp.poster("F5") + " counts, with the files at the top of Nc first. " + vp.NOT_BUILT, S + 1.5, "muted")
    y += 92

    cols = [("File", 420), ("Lines", 76), ("Decl.", 70), ("Its declarations, each at its line", 1352),
            ("Imports", 540), ("Imported by", c.x1 - x0 - 2458)]
    def file_link(m):
        return vp.to(f"mod-{m}", code(m, 40)) if m in mods else code(m, 40)
    rows = []
    for L in ORDER:
        ms = sorted((m for m in mods if mods[m]["library"] == L),
                    key=lambda m: (group_of(m) != f"{L}-top", group_of(m), m))   # the files at the top first
        f, ln, dc = GROUPS[L]
        dirs = sorted({group_of(m) for m in ms} - {L})
        sub = [g for g in dirs if not g.endswith("-top")]
        if dirs:
            top = [vp.to(vp.files_id(L), "the files at the top")] if f"{L}-top" in dirs else []
            inside = (" · " + (top[0] + ", and " if top else "") + f"{len(sub)} directories: "
                      + ", ".join(vp.to(vp.files_id(g), code(g)) for g in sub))
        elif L in ("Nc", "NS1", "Ov"):   # a library F5 counts as one directory
            inside = f" · its card on {vp.poster('F5')}: {vp.to('dir-' + L, code(L))}"
        else:
            inside = ""
        head = f"{vp.library(L)} · {plural(f, 'file')}, {ln} lines, {plural(dc, 'declaration')}"
        rows.append({"group": head + inside, "accent": ACCENT[L], "anchor": f"files-{L}"})
        grp = None
        for m in ms:
            g = group_of(m)
            if dirs and g != grp:
                grp = g
                gf, gl, gd = GROUPS[g]
                name = f"{L}, the files at the top" if g.endswith("-top") else code(g)
                dd = g.removesuffix("-top")
                rows.append({"group": f"{name} · {plural(gf, 'file')}, {gl} lines, {plural(gd, 'declaration')} · its "
                                      f"card on {vp.poster('F5')}: {vp.to('dir-' + dd.replace('.', '-'), code(dd))}",
                             "accent": ACCENT[L], "anchor": vp.files_id(dd)})
            d = mods[m]
            names = ", ".join(linked(vp.lean_url(src.full, x["file"], x["line"]),
                                     code(x["name"].removeprefix(f"{L}."), 44)) for x in decls[m])
            rows.append({"cells": [linked(vp.lean_url(src.full, d["file"]), code(m, 40)), str(d["lines"]),
                                   str(len(decls[m])), names or "none",
                                   ", ".join(file_link(i) for i in d["imports"]) or "nothing",
                                   ", ".join(file_link(i) for i in sorted(imported_by[m])) or "nothing"],
                         "anchor": f"mod-{m}"})
    y += c.table(x0, y, cols, rows, size=S) + 40

    c.para(x0, y, c.x1 - x0, "**Not checked here.** The build checks each library's and each directory's counts "
           "(`GROUPS`), not each file's: a declaration renamed, moved within a directory, or replaced by another "
           "leaves them as they were. That a name is a declaration is read from the text at the head of a line, as "
           "on " + vp.poster("F2") + ".", S + 1.5, "muted")
    return c
