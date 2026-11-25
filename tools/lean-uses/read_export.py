#!/usr/bin/env python3
"""Read the uses between the numbered statements from a lean4export export of vp-vnp, into src/lean-uses.json.

    python3 tools/lean-uses/read_export.py EXPORT.ndjson [--meta tools/lean-uses/meta.json]

The export (lean4export NDJSON, format 3.1.0) holds the declarations named on its command line and every declaration
they depend on, with their elaborated types and values. This script reads it in one pass, keeping for every
expression only its children and, for a constant, the name it refers to; then, for every numbered statement of the
paper (Table 3, through diagrams/src/vp.py), it walks, breadth first, from the statement's Lean theorems through every
declaration of vp-vnp that belongs to no statement, and records each other statement's theorem it meets: "direct" when
one of the statement's own theorems refers to it, "through" when a helper does, with a shortest chain of declarations
from the one to the other, and the declarations of the Paper library the walk passed. It is the walk of vp._statement_uses, over the
terms Lean elaborated instead of the names in the source, with the same rule for a name Table 3 gives two statements.

A constant is vp-vnp's own when (rule; it is recorded in the meta file):
  - its name is one the source declares (vp.load's declarations, Challenge.lean aside), or
  - it extends such a name (a compiler-made `._proof_1`, `.match_1`, `.eq_1`, a structure's `.mk` and fields), or
  - it is private to a module of vp-vnp (`_private.<module>.0.…`).
Every other constant is the library's (Lean, Batteries, Mathlib) and is not walked.

Standard library only. It reads the source through diagrams/src/vp.py, so VP_VNP must point at the checkout the export
was built from, and that checkout must be at FM_COMMIT.
"""
import array
import collections
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "diagrams" / "src"))
import vp  # noqa: E402

OUT = ROOT / "diagrams" / "src" / "lean-uses.json"


def main(argv):
    path = pathlib.Path(argv[0])
    meta_path = pathlib.Path(argv[argv.index("--meta") + 1]) if "--meta" in argv else ROOT / "tools" / "lean-uses" / "meta.json"
    src = vp.load(lean=False)

    # ---- one pass over the export
    names = {0: None}                       # name id -> (prefix id, component)
    kids = {}                               # expr id -> tuple of child expr ids (only for compound exprs)
    const = array.array("q")                # const_of[expr id] = name id, or -1
    decls = {}                              # name id -> list of root expr ids (type, value)
    kinds = {}
    head = None
    sha = hashlib.sha256()
    lines = 0
    with open(path, "rb") as fh:
        for raw in fh:
            sha.update(raw)
            lines += 1
            o = json.loads(raw)
            if "meta" in o:
                head = o["meta"]
                continue
            if "in" in o:
                if "str" in o:
                    names[o["in"]] = (o["str"]["pre"], o["str"]["str"])
                else:
                    names[o["in"]] = (o["num"]["pre"], str(o["num"]["i"]))
                continue
            if "il" in o:
                continue
            if "ie" in o:
                ie = o["ie"]
                while len(const) <= ie:
                    const.append(-1)
                if "const" in o:
                    const[ie] = o["const"]["name"]
                elif "app" in o:
                    kids[ie] = (o["app"]["fn"], o["app"]["arg"])
                elif "lam" in o or "forallE" in o:
                    b = o.get("lam") or o["forallE"]
                    kids[ie] = (b["type"], b["body"])
                elif "letE" in o:
                    b = o["letE"]
                    kids[ie] = (b["type"], b["value"], b["body"])
                elif "proj" in o:
                    kids[ie] = (o["proj"]["struct"],)
                    const[ie] = o["proj"]["typeName"]
                elif "mdata" in o:
                    kids[ie] = (o["mdata"]["expr"],)
                continue
            for kind in ("axiom", "def", "thm", "opaque", "quot"):
                if kind in o:
                    d = o[kind]
                    decls[d["name"]] = [d["type"]] + ([d["value"]] if "value" in d else [])
                    kinds[d["name"]] = kind
            if "inductive" in o:
                ind = o["inductive"]
                for part in ("types", "ctors", "recs"):
                    for d in ind[part]:
                        decls[d["name"]] = [d["type"]]
                        kinds[d["name"]] = part[:-1]

    memo = {}

    def name_of(i):
        if i in memo:
            return memo[i]
        parts = []
        j = i
        while j:
            pre, comp = names[j]
            parts.append(comp)
            j = pre
        s = ".".join(reversed(parts))
        memo[i] = s
        return s

    by_name = {name_of(i): i for i in decls}

    # ---- which constants are vp-vnp's own
    source = set(src.decls)
    modules = set(src.modules)

    def own(n):
        if n.startswith("_private."):
            rest = n[len("_private."):]
            mod = rest.split(".0.", 1)[0]
            return mod in modules
        parts = n.split(".")
        return any(".".join(parts[:k]) in source for k in range(1, len(parts) + 1))

    def refs(name_id):
        """The constants a declaration's type and value refer to."""
        out, seen, stack = set(), set(), list(decls.get(name_id, ()))
        while stack:
            e = stack.pop()
            if e in seen:
                continue
            seen.add(e)
            c = const[e] if e < len(const) else -1
            if c >= 0:
                out.add(c)
            stack.extend(kids.get(e, ()))
        return out

    # ---- the statements and their own theorems in the export
    owner = {}
    absent = []
    for key, st in src.statements.items():
        for full in st["decls"]:
            if full in by_name:
                owner.setdefault(by_name[full], []).append(key)
            else:
                absent.append(full)
    ref_cache = {}

    def refs_c(i):
        if i not in ref_cache:
            ref_cache[i] = refs(i)
        return ref_cache[i]

    uses, chains, reach, met = {}, {}, {}, {}
    for key, st in sorted(src.statements.items(), key=lambda t: vp.order_key(t[0])):
        start = [by_name[f] for f in st["decls"] if f in by_name]
        found, seen, via, hit = {}, set(start), {}, {}
        prev = {i: None for i in start}
        frontier = collections.deque((i, True, frozenset(owner[i]) - {key}) for i in start)
        while frontier:                                 # breadth first, so that each chain recorded is a shortest
            i, mine, skip = frontier.popleft()
            for c in sorted(refs_c(i)):
                if c == i:
                    continue
                others = [k for k in owner.get(c, ()) if k != key]
                if others:
                    for k in others:
                        if k in skip:
                            continue
                        found[k] = "direct" if (mine or found.get(k) == "direct") else found.get(k, "through")
                        hit.setdefault(k, set()).add(name_of(c))
                        if k not in via or (mine and len(via[k]) > 2):
                            chain, j = [name_of(c)], i
                            while j is not None:
                                chain.append(name_of(j))
                                j = prev[j]
                            via[k] = chain[::-1]
                    continue
                if c in owner or c in seen or c not in decls or not own(name_of(c)):
                    continue
                seen.add(c)
                prev[c] = i
                frontier.append((c, False, skip))
        uses[key] = {k: found[k] for k in sorted(found, key=vp.order_key)}
        chains[key] = {k: via[k] for k in sorted(via, key=vp.order_key)}
        # the declarations of the Paper library the walk passed, the statement's own among them: R3's route claims
        met[key] = {k: sorted(hit[k]) for k in sorted(hit, key=vp.order_key)}   # the used one's names arrived at
        reach[key] = sorted(n for n in (name_of(i) for i in seen) if n.startswith("Paper.") and n in source)

    own_count = sum(1 for i in decls if own(name_of(i)))
    data = {"uses": uses, "chains": chains, "reach": reach, "met": met, "absent": sorted(absent),
            "counts": {"declarations": len(decls), "vp_vnp": own_count, "library": len(decls) - own_count,
                       "uses": sum(len(v) for v in uses.values()),
                       "direct": sum(1 for v in uses.values() for h in v.values() if h == "direct")}}
    text = json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    meta = {"fm_commit": src.full, "export": path.name, "export_sha256": sha.hexdigest(), "export_lines": lines,
            "exporter": head and head.get("exporter"), "lean": head and head.get("lean"),
            "format": head and head.get("format"),
            "rule": "vp-vnp's own: a name the source declares, a name extending one, or _private.<vp-vnp module>.0.*",
            "output": OUT.relative_to(ROOT).as_posix(),
            "output_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
    meta_path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {data['counts']}; {len(absent)} Table 3 names not in the export")
    print(f"  LEAN_USES_SHA256 = \"{meta['output_sha256']}\"")


if __name__ == "__main__":
    main(sys.argv[1:])
