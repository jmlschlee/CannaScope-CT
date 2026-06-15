#!/usr/bin/env python3
"""T1 — contaminant-class taxonomy is the single source of truth: every analyte/category resolves to a
class with the CORRECT remediation_possible property and base flag. The core safety principle:
microbial = remediable; elemental heavy metals + mycotoxins = NOT remediable by ordinary cannabis methods.

Run: python3 _test_taxonomy.py
"""
import cannascope_ct_v17_src as M

_fails = []
def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond: _fails.append(msg)

# --- the core principle: heavy metals are NON-remediable; microbials ARE remediable ---
for metal in ("chromium", "lead", "arsenic", "cadmium", "mercury"):
    check(M.contaminant_class(metal) == M.CLASS_HEAVY_METAL, f"{metal} -> elemental heavy metals")
    check(M.remediation_possible(metal) == "no", f"{metal} is NOT remediable by ordinary methods")
    check(M.class_base_flag(metal) == "Critical", f"{metal} fail->pass base flag is Critical")
    check(M.is_non_remediable(metal), f"{metal} is non-remediable")

for micro in ("tymc", "aerobic", "aspergillus", "salmonella", "ecoli", "listeria"):
    check(M.contaminant_class(micro) == M.CLASS_BIOLOGIC, f"{micro} -> biologic/microbial")
    check(M.remediation_possible(micro) == "yes", f"{micro} IS remediable (validated kill steps)")
    check(not M.is_non_remediable(micro), f"{micro} is remediable (not in the non-remediable gate)")

# --- mycotoxins: NOT remediable (killing mold doesn't remove the toxin) ---
for myco in ("aflatoxin", "ochratoxin", "Mycotoxins"):
    check(M.contaminant_class(myco) == M.CLASS_MYCOTOXIN, f"{myco} -> mycotoxins")
    check(M.remediation_possible(myco) == "no", f"{myco} is NOT remediable")
    check(M.is_non_remediable(myco), f"{myco} is non-remediable")

# --- chemical residues: SOMETIMES remediable (must be proven by the later COA) ---
for chem in ("pesticides", "__pesticide_panel__", "solvent:benzene", "Residual Solvents"):
    check(M.contaminant_class(chem) == M.CLASS_CHEMICAL, f"{chem} -> chemical residues")
    check(M.remediation_possible(chem) == "sometimes", f"{chem} is sometimes remediable")
    check(not M.is_non_remediable(chem), f"{chem} not in the non-remediable gate")

# --- potency: informational, never a safety reversal ---
for pot in ("total_thc", "total_cannabinoids", "thca", "cbd"):
    check(M.contaminant_class(pot) == M.CLASS_POTENCY, f"{pot} -> potency/cannabinoids")
    check(M.remediation_possible(pot) == "n/a", f"{pot} is n/a (not a safety remediation)")

# --- conflict-CATEGORY labels (what _conflict_categories emits) resolve correctly ---
check(M.contaminant_class("Total Yeast & Mold") == M.CLASS_BIOLOGIC, "category 'Total Yeast & Mold' -> biologic")
check(M.contaminant_class("Heavy metals") == M.CLASS_HEAVY_METAL, "category 'Heavy metals' -> elemental")
check(M.contaminant_class("Chromium") == M.CLASS_HEAVY_METAL, "per-metal category 'Chromium' -> elemental")
check(M.contaminant_class("Aspergillus species") == M.CLASS_BIOLOGIC, "category 'Aspergillus species' -> biologic")

# --- the taxonomy table itself is complete + consistent ---
for cls, props in M.CONTAMINANT_CLASSES.items():
    check(props["remediation_possible"] in ("yes", "no", "sometimes", "n/a"), f"{cls} has a valid remediation_possible")
    check(props["base_flag"] in ("Critical", "High", "Moderate", "Informational"), f"{cls} has a valid base flag")
check(M.CONTAMINANT_CLASSES[M.CLASS_HEAVY_METAL]["remediation_possible"] == "no", "taxonomy: heavy metals NOT remediable")
check(M.CONTAMINANT_CLASSES[M.CLASS_BIOLOGIC]["remediation_possible"] == "yes", "taxonomy: biologic remediable")

print()
if _fails:
    print(f"FAILED ({len(_fails)}):")
    for f in _fails: print("  -", f)
    raise SystemExit(1)
print("ALL PASSED")
