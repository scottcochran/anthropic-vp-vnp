/-
The second reading of the uses: the compiled modules of vp-vnp, read by Lean itself.

    lake env lean --run tools/lean-uses/ReadModules.lean <module>… > modules.ndjson

Run from the vp-vnp folder of a built checkout, with the project's own toolchain (its lean-toolchain). It imports the
named modules at the private level, the level that holds the proofs (importModules' default), and prints one JSON line
for every constant whose module belongs to vp-vnp: its name, its module, and the constants its type and its value use
(Expr.getUsedConstants). Which constants are vp-vnp's is decided here by the module that defines each one, not by its
name, so the export's rule (tools/lean-uses/read_export.py) is checked, not shared. read_modules.py reads the output.
-/
import Lean
open Lean

/-- The libraries of vp-vnp (its lakefile.toml). -/
def libraries : List String := ["Statement", "Challenge", "Solution", "Paper", "Nc", "NS1", "Ov"]

def main (args : List String) : IO Unit := do
  initSearchPath (← findSysroot)
  let imports := args.toArray.map fun m => ({ module := m.toName } : Import)
  let env ← importModules imports {} (trustLevel := 1024)
  let out ← IO.getStdout
  let mut n := 0
  for (name, ci) in env.constants.map₁.toList do
    let some idx := env.getModuleIdxFor? name | continue
    let mod := env.header.moduleNames[idx.toNat]!
    if !(libraries.contains (mod.getRoot.toString (escape := false))) then continue
    let mut used := ci.type.getUsedConstants
    if let some v := ci.value? (allowOpaque := true) then
      used := used ++ v.getUsedConstants
    let j := Json.mkObj [("n", Json.str (name.toString (escape := false))),
                         ("m", Json.str (mod.toString (escape := false))),
                         ("v", Json.bool (ci.value? (allowOpaque := true)).isSome),
                         ("u", Json.arr (used.map fun u => Json.str (u.toString (escape := false))))]
    out.putStrLn j.compress
    n := n + 1
  IO.eprintln s!"{n} constants of vp-vnp, from {env.header.moduleNames.size} modules"
