#!/usr/bin/env python3
"""Regression test for the coverage-gap diagnosis (open item #2): every COA held out of findings is
classified by its EXACT per-COA failure reason (OCR / broken link / multi-product routing / source
mismatch / parser error / extraction), aggregated, and a published COA is never counted as a gap.

Run: python3 _test_coverage_gap.py
"""
import cannascope_ct_v17_src as M
import cannascope_ct_v5 as v5

_fails = []
def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond: _fails.append(msg)

def _p(status, note="", reg="R", safety_incomplete=False):
    p = v5.ProductV5()
    p.product_name = "Test Product"; p.producer = "Test Producer"; p.dosage_form = "Flower"
    p.registration_number = reg; p.report_url = "http://x/" + reg + ".pdf"
    p._coa_status = status; p.parse_note = note
    if safety_incomplete:
        p._safety_panel_incomplete = True
    return p

# --- per-reason classification ---
check(M.classify_coverage_gap(_p(M.MATCH_LINK_BROKEN, "could not download COA"))[0] == "broken_link",
      "broken link -> broken_link")
check(M.classify_coverage_gap(_p(M.MATCH_LINK_BROKEN, "no extractable text (scanned image?)"))[0] == "ocr_extraction",
      "no-extractable-text -> ocr_extraction (even with a broken status)")
check(M.classify_coverage_gap(_p(M.MATCH_MANUAL, "multi-product COA (5 products): could not isolate"))[0] == "multiproduct_routing",
      "multi-product routing -> multiproduct_routing")
check(M.classify_coverage_gap(_p(M.MATCH_PRODUCT_MISMATCH))[0] == "source_mismatch",
      "product mismatch -> source_mismatch")
check(M.classify_coverage_gap(_p(M.MATCH_VALUE_MISMATCH))[0] == "source_mismatch",
      "value mismatch -> source_mismatch")
check(M.classify_coverage_gap(_p(M.MATCH_MANUAL, "processing error: ValueError: bad"))[0] == "parser_error",
      "processing error -> parser_error")
check(M.classify_coverage_gap(_p(M.MATCH_MANUAL, "microbial safety panel did not parse", safety_incomplete=True))[0] == "safety_incomplete",
      "incomplete safety panel -> safety_incomplete")
check(M.classify_coverage_gap(_p(M.MATCH_LINK_MISSING, "offline: COA not in CSV cache"))[0] == "offline_uncached",
      "offline+cache -> offline_uncached")
check(M.classify_coverage_gap(_p(M.MATCH_MANUAL, "some unusual reason"))[0] == "manual_review",
      "unclassified -> manual_review")

# every reason code has a human label
for code, label, detail in [M.classify_coverage_gap(_p(M.MATCH_LINK_BROKEN, "x"))]:
    check(code in M.GAP_REASON_LABELS, "reason code is in GAP_REASON_LABELS")

# --- aggregation: published COAs are NOT gaps; gaps are counted + reconcile ---
pub1 = _p(M.MATCH_EXACT, reg="P1")
pub2 = _p(M.MATCH_PARTIAL, reg="P2")
g1 = _p(M.MATCH_LINK_BROKEN, "could not download COA", reg="G1")
g2 = _p(M.MATCH_LINK_BROKEN, "no extractable text", reg="G2")
g3 = _p(M.MATCH_MANUAL, "multi-product COA: could not isolate", reg="G3")
reasons, rows = M.coverage_gap_diagnosis([pub1, pub2, g1, g2, g3])
check(len(rows) == 3, f"only the 3 held-out COAs are rows (got {len(rows)})")
check(all(r["reg"] in ("G1", "G2", "G3") for r in rows), "published COAs are never gap rows")
check(sum(r["count"] for r in reasons) == 3, "reason counts reconcile to the number of gaps")
codes = {r["code"] for r in reasons}
check({"broken_link", "ocr_extraction", "multiproduct_routing"} <= codes, "all three distinct reasons surfaced")
check(M.coverage_gap_diagnosis([pub1, pub2]) == ([], []), "no gaps -> empty diagnosis")

print()
if _fails:
    print(f"FAILED ({len(_fails)}):")
    for f in _fails: print("  -", f)
    raise SystemExit(1)
print("ALL PASSED")
