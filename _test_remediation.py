#!/usr/bin/env python3
"""Remediation intelligence layer (TASKS 2/3/4/5/6/8): a microbial fail->pass is a 'potential
remediation/retest event' (NOT fraud) while a heavy-metal fail->pass is Critical and routed to the
Non-Remediable Elemental Contamination section, with full forensics, transparency-failure detection,
Severe-Chromium logic, and a mold-without-mycotoxin-clearance check.

Run: python3 _test_remediation.py
"""
import cannascope_ct_v17_src as M
import cannascope_ct_v5 as v5

_fails = []
def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond: _fails.append(msg)

# ---------- TASK 2: class-aware labels ----------
check("Non-remediable elemental" in M.remediation_event_label("chromium"), "metal -> non-remediable label")
check("remediation or retest" in M.remediation_event_label("tymc"), "microbial -> potential remediation/retest label")
check("does not remove the toxin" in M.remediation_event_label("aflatoxin"), "mycotoxin -> toxin-not-removed label")
check("documented remediation/retest" in M.remediation_event_label("pesticides"), "chemical -> documented-explanation label")

# ---------- TASK 8: severity matrix (heavy metal fail->pass NEVER below Critical) ----------
check(M.remediation_severity("chromium", fail_then_pass=True, itemized_later=True) == "Critical",
      "heavy-metal fail->pass is Critical even WITH itemized later values")
check(M.remediation_severity("chromium", fail_then_pass=True, itemized_later=False) == "Critical",
      "heavy-metal fail->pass without itemized values is Critical")
check(M.remediation_severity("lead", over_limit=True) == "Critical", "standalone heavy-metal over-limit is Critical")
check(M.remediation_severity("tymc", fail_then_pass=True) == "High", "microbial fail->pass is High (not Critical)")
check(M.remediation_severity("aspergillus", fail_then_pass=True, detected_pathogen=True) == "Critical",
      "Aspergillus detected then absent is Critical")
check(M.remediation_severity("tymc", near_limit=True) == "Medium", "microbial near-limit clustering is Medium")
check(M.remediation_severity("aflatoxin", over_limit=True) == "Critical", "mycotoxin over limit is Critical")
check(M.remediation_severity("pesticides", fail_then_pass=True) == "High", "chemical fail->pass is High")

# ---------- TASK 4: generic 'below action limits' transparency detection ----------
check(M.metals_generic_pass("Heavy Metals: below action limits. PASS") is True,
      "generic 'heavy metals below action limits' (no numbers) -> transparency failure")
check(M.metals_generic_pass("As, Cd, Pb, Hg, Cr below action limits") is True,
      "generic 'As,Cd,Pb,Hg,Cr below action limits' -> transparency failure")
check(M.metals_generic_pass("Arsenic <0.1 ug/kg, Lead 12 ug/kg below action limits") is False,
      "itemized metal values present -> NOT a transparency failure")
check(M.metals_generic_pass("Total THC 24%") is False, "no metals statement at all -> not flagged")

# ---------- TASK 3/5: SERIOUS CONCERN builder + Severe Chromium ----------
# a chromium fail (1205.613 > 600) then a later numeric pass (518) — both sides present
CONF = [M._make_finding("Heavy metals",
        [dict(p=None, cfp={"product": "Two To Mgo Pr Minis", "producer": "Theraplant", "strain": "",
                           "product_type": "Vape Cartridge", "shared_id": "Lot 383", "report_url": "http://x"},
              lab="Analytics Labs", date=(2024, 1, 29), date_str="2024-01-29", status="FAIL",
              value=1205.613, limit=600.0, unit="ug/kg", raw="1205.613", analyte_key="chromium",
              analyte="Chromium", coa_url="http://x", reg="MMBR.0025389", pages=""),
         dict(p=None, cfp={"product": "Two To Mgo Pr Minis", "producer": "Theraplant", "strain": "",
                           "product_type": "Vape Cartridge", "shared_id": "Lot 383", "report_url": "http://y"},
              lab="Analytics Labs", date=(2024, 11, 19), date_str="2024-11-19", status="PASS",
              value=518.024, limit=600.0, unit="ug/kg", raw="518.024", analyte_key="chromium",
              analyte="Chromium", coa_url="http://y", reg="MMBR.0025073", pages="")],
        "Critical", fail_then_pass=True)]
# tag the finding with derived class fields the way detect_coa_conflicts would (via _make_finding)
check(CONF[0]["contaminant_class"] == M.CLASS_HEAVY_METAL, "_make_finding derives heavy-metal class from the metal")
check(CONF[0]["analyte"] == "Chromium", "_make_finding names the specific metal (Chromium)")

rows = M.non_remediable_findings(CONF, [])
check(len(rows) == 1, f"one SERIOUS-CONCERN row built (got {len(rows)})")
r = rows[0]
check(r["analyte"] == "Chromium" and r["severity"] == "Critical", "row is Chromium / Critical")
check(abs(r["fail_value"] - 1205.613) < 1e-3 and r["fail_limit"] == 600.0, "failing value + limit on the COA carried")
check(abs(r["fail_fold"] - 2.009) < 0.01 and abs(r["fail_pct"] - 200.94) < 0.1, "fold/% of limit computed")
check(r["severe_chromium"] is True, "chromium >= 2x -> Severe Chromium Exceedance")
check(r["fail_then_pass"] and abs(r["later_value"] - 518.024) < 1e-3, "later passing value carried (both sides)")
check(r["itemized_later"] is True and r["transparency_failure"] is False, "later COA itemized -> NOT a transparency failure")
check(r["fail_date"] == "2024-01-29" and r["later_date"] == "2024-11-19", "both test dates carried")
check(r["fail_coa"] == "http://x" and r["later_coa"] == "http://y", "both COA links carried")
check("hardware/process-contamination" in r["product_type_note"], "vape product-type elevation note")
check("Non-remediable elemental" in r["label"], "row label is the non-remediable label")

# generic later pass (no number) -> transparency failure on a chromium fail
CONF2 = [M._make_finding("Heavy metals",
         [dict(p=None, cfp={"product": "P2", "producer": "Prod", "strain": "", "product_type": "Flower",
                            "shared_id": "Lot 9", "report_url": "http://a"}, lab="L1", date=(2024,1,1),
               date_str="2024-01-01", status="FAIL", value=900.0, limit=600.0, unit="ug/kg", raw="900",
               analyte_key="chromium", analyte="Chromium", coa_url="http://a", reg="R1", pages=""),
          dict(p=None, cfp={"product": "P2", "producer": "Prod", "strain": "", "product_type": "Flower",
                            "shared_id": "Lot 9", "report_url": "http://b"}, lab="L2", date=(2024,6,1),
               date_str="2024-06-01", status="PASS", value=None, limit=None, unit="", raw="below action limits",
               analyte_key="chromium", analyte="Chromium", coa_url="http://b", reg="R2", pages="")],
         "Critical", fail_then_pass=True)]
r2 = M.non_remediable_findings(CONF2, [])[0]
check(r2["itemized_later"] is False and r2["transparency_failure"] is True,
      "generic later pass (no itemized value) -> Transparency Failure")
check("flower" in r2["product_type_note"], "flower product-type elevation note (plant uptake)")

# microbial fail->pass must NOT appear in the non-remediable section
MICRO = [M._make_finding("Total Yeast & Mold",
         [dict(p=None, cfp={"product": "M1", "producer": "Pr", "strain": "", "product_type": "Flower",
                            "shared_id": "L", "report_url": "u"}, lab="L1", date=(2024,1,1), date_str="2024-01-01",
               status="FAIL", value=300000.0, limit=100000.0, unit="CFU/g", raw="300000", analyte_key="tymc",
               analyte="Total Yeast & Mold", coa_url="u", reg="R", pages=""),
          dict(p=None, cfp={"product": "M1", "producer": "Pr", "strain": "", "product_type": "Flower",
                            "shared_id": "L", "report_url": "u2"}, lab="L1", date=(2024,6,1), date_str="2024-06-01",
               status="PASS", value=50.0, limit=100000.0, unit="CFU/g", raw="50", analyte_key="tymc",
               analyte="Total Yeast & Mold", coa_url="u2", reg="R2", pages="")],
         "Critical", fail_then_pass=True)]
check(M.non_remediable_findings(MICRO, []) == [], "microbial fail->pass is NOT in the non-remediable section")

# ---------- TASK 6: mold fail->pass without mycotoxin clearance ----------
gaps = M.mycotoxin_clearance_gaps(MICRO)
check(len(gaps) == 1 and "mycotoxin clearance" in gaps[0]["note"],
      "mold fail->pass with no same-lot mycotoxin test -> clearance gap flagged")
# if a mycotoxin record exists for the same lot, no gap
MYCO_SAME = MICRO + [M._make_finding("Mycotoxins",
            [dict(p=None, cfp={"product": "M1", "producer": "Pr", "strain": "", "product_type": "Flower",
                               "shared_id": "L", "report_url": "u3"}, lab="L1", date=(2024,6,2), date_str="2024-06-02",
                  status="ND", value=None, limit=None, unit="", raw="ND", analyte_key="aflatoxin",
                  analyte="Aflatoxins", coa_url="u3", reg="R3", pages="")] * 2, "Low")]
check(M.mycotoxin_clearance_gaps(MYCO_SAME) == [], "mycotoxins tested on same lot -> no clearance gap")

# ---------- TASK 3: standalone over-limit metal on a published product (no conflict) ----------
p = v5.ProductV5(); p.product_name = "Solo Metal"; p.producer = "Pr"; p.dosage_form = "Vape Cartridge"
p.registration_number = "R9"; p.report_url = "http://solo"; p._coa_status = M.MATCH_EXACT
p.test_lab = "Analytics Labs"
p.analytes = {"lead": {"value": 780.0, "limit": 500.0, "unit": "ug/kg", "raw": "780.0"}}
solo = M.non_remediable_findings([], [p])
check(len(solo) == 1 and solo[0]["analyte"].lower() == "lead" and solo[0]["severity"] == "Critical",
      "standalone over-limit Lead on a published product surfaces as Critical")
check(solo[0]["fail_value"] == 780.0 and solo[0]["fail_lab"] == "Analytics Labs",
      "standalone row carries value + lab")
# a below-detection metal bound is NOT an exceedance
p2 = v5.ProductV5(); p2.product_name = "Clean"; p2._coa_status = M.MATCH_EXACT
p2.analytes = {"lead": {"value": 0.5, "limit": 500.0, "unit": "ug/kg", "raw": "<0.5", "_below_detect": True}}
check(M.non_remediable_findings([], [p2]) == [], "below-detect metal bound is never a SERIOUS-CONCERN row")

print()
if _fails:
    print(f"FAILED ({len(_fails)}):")
    for f in _fails: print("  -", f)
    raise SystemExit(1)
print("ALL PASSED")
