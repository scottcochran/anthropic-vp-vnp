#!/usr/bin/env python3
"""The second reading: the uses between statements from the compiled modules, into src/lean-modules.json.

    python3 tools/lean-uses/read_modules.py MODULES.ndjson [--meta tools/lean-uses/meta-modules.json]

MODULES.ndjson is what ReadModules.lean prints: every constant of a vp-vnp module, with its module and the constants
its type and value use, read by Lean itself from the built modules. This script runs on it the walk that
read_export.py runs on the export (vp._statement_uses' rule, over elaborated terms), with one difference: a constant is
vp-vnp's own when a vp-vnp module defines it, as Lean records, not by its name. It writes the uses, and how the
export's rule for vp-vnp's own constants compares with the modules' (src/lean-uses.json is read for that), so that F9
can check the two Lean readings against each other. Standard library only.
"""
import collections
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "diagrams" / "src"))
import vp  # noqa: E402

OUT = ROOT / "diagrams" / "src" / "lean-modules.json"


def main(argv):
    path = pathlib.Path(argv[0])
    meta_path = pathlib.Path(argv[argv.index("--meta") + 1]) if "--meta" in argv else \
        ROOT / "tools" / "lean-uses" / "meta-modules.json"
    src = vp.load(lean=False)
    used, module = {}, {}
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        for raw in fh:
            sha.update(raw)
            o = json.loads(raw)
            used[o["n"]] = set(o["u"])
            module[o["n"]] = o["m"]
    own = set(used)                                    # every constant here is defined by a module of vp-vnp

    owner = {}
    absent = []
    for key, st in src.statements.items():
        for full in st["decls"]:
            if full in own:
                owner.setdefault(full, []).append(key)
            else:
                absent.append(full)
    source = set(src.decls)

    def source_of(n):
        if n.startswith("_private."):
            n = n[len("_private."):].split(".0.", 1)[-1]
        parts = n.split(".")
        for k in range(len(parts), 0, -1):
            if ".".join(parts[:k]) in source:
                return ".".join(parts[:k])
        return None

    uses, under = {}, {}
    for key, st in sorted(src.statements.items(), key=lambda t: vp.order_key(t[0])):
        start = [f for f in st["decls"] if f in own]
        found, seen = {}, set(start)
        frontier = collections.deque((n, True, frozenset(owner[n]) - {key}) for n in start)
        while frontier:
            n, mine, skip = frontier.popleft()
            for c in sorted(used.get(n, ())):
                if c == n:
                    continue
                others = [k for k in owner.get(c, ()) if k != key]
                if others:
                    for k in others:
                        if k not in skip:
                            found[k] = "direct" if (mine or found.get(k) == "direct") else found.get(k, "through")
                    continue
                if c in owner or c in seen or c not in own:
                    continue
                seen.add(c)
                frontier.append((c, False, skip))
        uses[key] = {k: found[k] for k in sorted(found, key=vp.order_key)}
        under[key] = sorted({m for m in (source_of(n) for n in seen) if m})

    # the export's rule for vp-vnp's own constants (read_export.py), against the modules'
    modules = set(src.modules)

    def by_name(n):
        if n.startswith("_private."):
            return n[len("_private."):].split(".0.", 1)[0] in modules
        parts = n.split(".")
        return any(".".join(parts[:k]) in source for k in range(1, len(parts) + 1))

    mentioned = set().union(*used.values()) | own
    named_not_module = sorted(n for n in mentioned if by_name(n) and n not in own)
    module_not_named = sorted(n for n in own if not by_name(n))
    data = {"uses": uses, "under": under, "absent": sorted(absent),
            "rule": {"by_name_not_by_module": named_not_module, "by_module_not_by_name": module_not_named},
            "counts": {"vp_vnp": len(own), "modules": len(set(module.values())),
                       "uses": sum(len(v) for v in uses.values()),
                       "direct": sum(1 for v in uses.values() for h in v.values() if h == "direct")}}
    text = json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    meta = {"fm_commit": src.full, "input": path.name, "input_sha256": sha.hexdigest(), "constants": len(own),
            "reader": "tools/lean-uses/ReadModules.lean, lean --run with the project's toolchain (lean-toolchain)",
            "rule": "vp-vnp's own: defined by a module of Statement, Challenge, Solution, Paper, Nc, NS1 or Ov",
            "output": OUT.relative_to(ROOT).as_posix(),
            "output_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
    meta_path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {data['counts']}; rule: {len(named_not_module)} named vp-vnp's but a library's, "
          f"{len(module_not_named)} vp-vnp's but not by name")
    print(f"  LEAN_MODULES_SHA256 = \"{meta['output_sha256']}\"")


if __name__ == "__main__":
    main(sys.argv[1:])
