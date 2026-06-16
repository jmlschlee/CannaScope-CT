#!/usr/bin/env python3
"""B-1 regression — the cannabinoid FORMULA-LEGEND footnote (Analytics Labs) must NOT be scanned for
values. Before the fix, the THCA label matched inside the legend ("Total Active THC = D9-THC + (THCA*
0.877)...") and _bare_pct read the "9" out of "D9-THC" as THCA=9.0%, inflating DERIVED Total THC above
Total Cannabinoids on ~1,221 distillate COAs. This locks in: legend ignored, real THCA rows preserved.

Run: python3 _test_b1_cannabinoid_legend.py   (exit 0 = pass)
"""
import sys
import cannascope_ct_v5 as v5
import cannascope_ct_v17_src as S

_fail = 0
def check(name, cond, extra=""):
    global _fail
    print(("  [PASS] " if cond else "  [FAIL] ") + name + (f"  ({extra})" if extra and not cond else ""))
    if not cond:
        _fail += 1

# Real Analytics distillate layout: THCA is NOT a data row (only Δ9-THC + CBG); a formula legend follows.
ANALYTICS_DISTILLATE = """Cannabinoids Complete
80.248%
Total Active THC
ND
Total Active CBD
81.304%
Total Active Cannabinoids
Analyte LOD LOQ Result Result Qualifiers
% % % mg/g
Δ9-THC 0.00003 0.00010 80.248 802.483
CBG 0.00004 0.00010 1.056 10.559
Total Available THC 80.248 802.483
Total Active THC 80.248 802.483
Total Available CBD ND ND
Total Active CBD ND ND
Total Available Cannabinoids 81.304 813.042
Total Active Cannabinoids 81.304 813.042
Cannabinoids analyzed by SOP-009. LOD= Limit of Detection, LOQ = Limit of Quantitation, ND = Not Detected. Total Available THC = D9-THC + THCA. Total Active THC = D9-THC + (THCA0.877). Total Active Cannabinoids = THCA0.877+ d9 THC+ d8 THC+ THCVA0.867+ THCV+ CBDA 0.877 + CBD+ CBDV+ CBDVA 0.867+ CBNA0.876+ CBN + CBGA0.0.878+ CBG + CBCA*0.877+CBC+ CBL+ CBT.
"""

# Real flower layout (Analytics columnar): THCA IS a data row with a real value — must be preserved.
ANALYTICS_FLOWER = """Cannabinoids Complete
Analyte LOD LOQ Result Result Qualifiers
% % % mg/g
THCa 0.00003 0.00010 21.500 215.00
Δ9-THC 0.00003 0.00010 1.200 12.00
CBG 0.00004 0.00010 0.900 9.00
Total Active THC 19.930 199.30
Total Active Cannabinoids 22.100 221.00
Cannabinoids analyzed by SOP-009. LOD= Limit of Detection, LOQ = Limit of Quantitation. Total Active THC = D9-THC + (THCA0.877).
"""

print("B-1 — Analytics DISTILLATE (THCA not detected; legend must be ignored):")
p = v5.ProductV5()
v5.parse_cannabinoids(ANALYTICS_DISTILLATE, p)
thca = S.thc_value(p, "thca")
tt = S.thc_value(p, "total_thc")
totact = S.thc_value(p, "total_active")
check("THCA is NOT misread as 9.0", thca != 9.0, f"thca={thca}")
check("THCA absent / not from legend", thca is None or thca < 1.0, f"thca={thca}")
check("Total THC ~= Δ9 (80.2), not inflated to ~88", tt is not None and 79.0 <= tt <= 81.5, f"total_thc={tt}")
check("Total Active Cannabinoids preserved (81.304)", totact is not None and abs(totact - 81.304) < 0.1, f"={totact}")
check("no THC>TotalCannabinoids conflict", S.thc_conflict(p) is None, str(S.thc_conflict(p)))

print("B-1 — Analytics FLOWER (real THCA data row must be preserved):")
p2 = v5.ProductV5()
v5.parse_cannabinoids(ANALYTICS_FLOWER, p2)
thca2 = S.thc_value(p2, "thca")
check("real THCA 21.5 preserved", thca2 is not None and abs(thca2 - 21.5) < 0.2, f"thca={thca2}")
check("flower: no spurious conflict", S.thc_conflict(p2) is None, str(S.thc_conflict(p2)))

print()
if _fail:
    print(f"B-1 LEGEND REGRESSION: {_fail} FAILURE(S)")
    sys.exit(1)
print("B-1 LEGEND REGRESSION: ALL PASS")
