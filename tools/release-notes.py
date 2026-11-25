#!/usr/bin/env python3
"""Write the notes of a release from the tag, the pins and the manifest.

    python3 tools/release-notes.py TAG pins.json diagrams/manifest.json > notes.md

The notes carry what a reader needs to check a citation of a poster (PLAN.md, "Releases"): the tag message, which
opens with the kind of move; the pin and the four pinned hashes, with a link to the commit the pin resolves to; one
row per poster with its card and arrow counts, so that what moved between releases can be read without opening the
SVGs; and the workflow run that regenerated and checked the posters at the tag. Adapted from riemann-diagrams'
tools/release-notes.py. Standard library only.
"""
import json
import subprocess
import sys


def main(tag, pins_path, manifest_path):
    pins = json.load(open(pins_path, encoding="utf-8"))
    message = subprocess.run(["git", "tag", "-l", "--format=%(contents)", tag], capture_output=True,
                             text=True, check=True).stdout.strip()
    out = [message, "", "## The sources", "", "| Pin | Value |", "|---|---|"]
    fm = pins["formal_math"]
    out.append(f"| The vp-vnp folder of anthropics/formal-math (`FM_COMMIT`) | `{fm['pin']}`, "
               f"[{fm['commit'][:10]}]({fm['url']}) |")
    for k, v in pins["hashes"].items():
        out.append(f"| `{k}` | `{v[:16]}…` |")
    out.append(f"| vp-vnp-posters | `{tag}`, [{pins['generator']['commit'][:10]}]({pins['generator']['url']}) |")
    out += ["", "`PAPER_SHA256` is the paper's PDF; `PAPER_FACTS_SHA256` the facts read from it; `LEAN_USES_SHA256` "
            "and `LEAN_MODULES_SHA256` the uses read from the built Lean, from its export and from its compiled "
            "modules. Each derived file's `meta` in the tree records what it was read from.", "",
            f"Regenerated with Python {pins['python']}; the generator uses the standard library only.", "",
            "## The posters", "", "| Id | Poster | Cards | Arrows | File |", "|---|---|---:|---:|---|"]
    for k, v in json.load(open(manifest_path, encoding="utf-8")).items():
        title = v["title"].replace("|", "\\|")
        out.append(f"| {k} | {title} | {v['cards']} | {v['arrows']} | `{v['file']}` |")
    out += ["", "## Checking a citation", "",
            "`SHA256SUMS` covers every asset. A poster's state line, at its foot, names the same formal-math commit as "
            "the table above. The posters are SVG only; every browser renders them.", "",
            f"The posters were regenerated from the pinned sources and compared byte for byte with the tagged commit in "
            f"workflow run [{pins['run']['id']}]({pins['run']['url']}), which passed before this release was created.",
            "", "The posters quote vp-vnp's Lean source, README and paper under that folder's Apache-2.0 licence; the "
            "posters' own prose is CC BY 4.0 (see `NOTICE`). Nothing here builds the Lean for the posters; the "
            "derived Lean files were read once from a build at the pin (tools/lean-uses/README.md)."]
    print("\n".join(out))


if __name__ == "__main__":
    main(*sys.argv[1:])
