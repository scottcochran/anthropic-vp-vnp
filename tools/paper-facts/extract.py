#!/usr/bin/env python3
"""Read the facts the posters need from the paper, vp-vnp/paper.pdf at FM_COMMIT, into diagrams/src/paper-facts.json.

    uv run --with pypdf==7.1.1 python tools/paper-facts/extract.py [VP_VNP_DIR]

VP_VNP_DIR is the vp-vnp folder of a formal-math checkout (default: $VP_VNP, else ../vp-np). The paper exists only as
a PDF, and the standard library cannot read one, so this script is run once per move of FM_COMMIT, outside the build;
the build reads the JSON it writes, which diagrams/src/vp.py pins by its hash (PAPER_FACTS_SHA256) and by the hash of
the PDF it was read from (PAPER_SHA256). It writes, from the text pypdf extracts:

- table1: Table 1 of the paper, "Map of the proof": for each section A to O, what it proves, the sections it uses,
  and the case it serves (flat, contracting or both), as printed.
- table3: Table 3, "The Lean theorems that belong to the numbered statements": for each numbered statement of
  Sections A to N, its kind, its number and the Lean theorems (prefix Paper.) the table names, as printed and
  with a range such as "lem_toolkit_a to _f" spelled out; Remark N.6 has none ("not formalized").
- headers: for each statement of table3, the paper's own header for it in the text: the page and the title in
  parentheses, where the header has one.
- intro: the numbered statements of Sections 1 and 2, whose headers name their Lean theorem in parentheses.

It stops with an error, writing nothing, when a table does not parse as these expect: a row it cannot read, a
section of table1 out of order, a statement of table3 with no header in the text. tools/paper-facts/meta.json
records the commit, the PDF's hash, the pypdf version and the output's hash.
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import unicodedata

import pypdf

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "diagrams" / "src" / "paper-facts.json"
META = ROOT / "tools" / "paper-facts" / "meta.json"
KINDS = ("Theorem", "Lemma", "Proposition", "Corollary", "Definition", "Remark", "Display")
SECTIONS = "ABCDEFGHIJKLMNO"


def plain(s):
    """A title or a cell as plain text: the paper's math italic letters, which pypdf returns as Mathematical
    Alphanumeric Symbols (U+1D400 to U+1D7FF), become plain ones by NFKC (𝑈𝑛 -> Un), every other character is kept
    (ℓ stays ℓ), and runs of white space become one space."""
    if s is None:
        return None
    s = "".join(unicodedata.normalize("NFKC", ch) if 0x1D400 <= ord(ch) <= 0x1D7FF else ch for ch in s)
    return re.sub(r"\s+", " ", s).strip()


def fail(msg):
    sys.exit(f"extract: {msg}")


def pages(pdf):
    r = pypdf.PdfReader(str(pdf))
    return [p.extract_text() or "" for p in r.pages]


def table1(text):
    """The rows between the header "Section what is proved uses case" and the caption "Table 1."."""
    m = re.search(r"^Section what is proved uses case\n(.*?)^Table 1\. ", text, re.M | re.S)
    if not m:
        fail("no Table 1 (the header 'Section what is proved uses case')")
    rows = []
    for ln in m.group(1).splitlines():
        r = re.fullmatch(r"([A-O]) (.+?) ((?:[A-O](?:, [A-O])*)|–) (both|flat|contracting)", ln.strip())
        if not r:
            fail(f"Table 1: a row that does not parse: {ln!r}")
        uses = [] if r.group(3) == "–" else r.group(3).split(", ")
        rows.append({"section": r.group(1), "what": plain(r.group(2)), "uses": uses, "case": r.group(4)})
    if [r["section"] for r in rows] != list(SECTIONS):
        fail(f"Table 1: sections {[r['section'] for r in rows]}, expected A to O in order")
    return rows


def expand(names):
    """'lem_toolkit_a to _f' -> lem_toolkit_a ... lem_toolkit_f."""
    out = []
    for n in names:
        r = re.fullmatch(r"(\w+_)([a-z]) to _([a-z])", n)
        if r:
            out += [r.group(1) + chr(c) for c in range(ord(r.group(2)), ord(r.group(3)) + 1)]
        else:
            out.append(n)
    return out


def table3(text):
    """The rows between the header "Statement Lean (prefix Paper.)" and the caption "Table 3.". The table is printed
    in two columns, each with the header; a row's Lean names may wrap onto the next lines."""
    m = re.search(r"^Statement Lean \(prefix Paper\.\)\n(.*?)^Table 3\. ", text, re.M | re.S)
    if not m:
        fail("no Table 3 (the header 'Statement Lean (prefix Paper.)')")
    body = m.group(1).replace("Statement Lean (prefix Paper.)\n", "")
    rows, section = [], None
    row_re = re.compile(r"(" + "|".join(KINDS) + r") ((?:[A-O]\.\d+)|\(([A-O])\.\d+\)) (.+)")
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        s = re.fullmatch(r"(?:Section|Appendix) ([A-O])", ln)
        if s:
            section = s.group(1)
            continue
        r = row_re.fullmatch(ln)
        if r:
            num = r.group(2)
            sec = num.strip("()")[0]
            if sec != section:
                fail(f"Table 3: {r.group(1)} {num} under Section {section}")
            rows.append({"kind": r.group(1), "number": num, "section": sec, "printed": r.group(4)})
            continue
        if not rows:
            fail(f"Table 3: a line before the first row: {ln!r}")
        rows[-1]["printed"] += " " + ln          # a wrapped Lean cell
    for r in rows:
        p = re.sub(r"\s+", " ", r["printed"]).replace(" _", "_") if "to _" not in r["printed"] else \
            re.sub(r"\s+", " ", r["printed"])
        r["printed"] = p
        if p == "not formalized":
            r["lean"] = []
            continue
        names = [n.strip() for n in p.split(",")]
        if not all(re.fullmatch(r"\w+( to _[a-z])?", n) for n in names):
            fail(f"Table 3: {r['kind']} {r['number']}: Lean cell {p!r} is not a list of names")
        r["lean"] = expand(names)
    return rows


def headers(page_texts, rows):
    """For each statement of table3, its header in the text: the first line that starts with its kind and number
    followed by a title in parentheses or a full stop."""
    out = {}
    for r in rows:
        if r["kind"] == "Display":
            continue
        key = f"{r['kind']} {r['number']}"
        pat = re.compile(r"^" + re.escape(key) + r"(?: \(([^\n]*?)\))?\.", re.M)
        for i, t in enumerate(page_texts):
            m = pat.search(t)
            if m:
                out[key] = {"page": i + 1, "title": plain(m.group(1))}
                break
        else:
            fail(f"no header in the text for {key}")
    return out


def intro(text):
    """The numbered statements of Sections 1 and 2: 'Theorem 1.1 (main theorem; thm_allfields).'"""
    out = []
    for m in re.finditer(r"^(" + "|".join(KINDS) + r") ([12]\.\d+) \((?:([^;)]*); )?(\w+)\)\.", text, re.M):
        out.append({"kind": m.group(1), "number": m.group(2), "title": plain(m.group(3)), "lean": m.group(4)})
    if not out:
        fail("no numbered statement in Sections 1 and 2")
    return out


def main(argv):
    src = pathlib.Path(argv[0] if argv else os.environ.get("VP_VNP") or ROOT.parent / "vp-np")
    pdf = src / "paper.pdf"
    if not pdf.is_file():
        fail(f"no paper.pdf in {src}")
    commit = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True,
                            check=True).stdout.strip()
    texts = pages(pdf)
    text = "\n".join(texts)
    t3 = table3(text)
    facts = {"table1": table1(text), "table3": t3, "headers": headers(texts, t3), "intro": intro(text),
             "pages": len(texts)}
    data = json.dumps(facts, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    OUT.write_text(data, encoding="utf-8")
    meta = {"commit": commit, "file": "vp-vnp/paper.pdf",
            "paper_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pypdf": pypdf.__version__,
            "output": OUT.relative_to(ROOT).as_posix(),
            "output_sha256": hashlib.sha256(data.encode("utf-8")).hexdigest()}
    META.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(facts['table1'])} sections, {len(t3)} statements, "
          f"{len(facts['intro'])} in Sections 1 and 2, read at {commit[:10]}")
    print(f"  PAPER_SHA256 = \"{meta['paper_sha256']}\"")
    print(f"  PAPER_FACTS_SHA256 = \"{meta['output_sha256']}\"")


if __name__ == "__main__":
    main(sys.argv[1:])
