#!/usr/bin/env python3
"""Regression suite for Group E — cache provenance & traceability (E-2/E-3/E-4/SB-6).

Covers, with NO network:
  - provenance round-trips through the COA cache's _extra column (E-2);
  - _provenance_current / _provenance_state classify live / prior / stale / none (E-2);
  - the E-4 read-path version-gate condition (stale+online => re-verify; stale+offline / version-current
    / no-provenance => trusted-or-not as designed);
  - the E-3 cache-served split identity (backed + stale + none == cache-served total);
  - the SB-6 traceability predicate (published finding traces iff state in {live, prior}).

Run: python3 _test_provenance.py   (exit 0 = all pass)
"""
import os
import sys
import tempfile

import coa_csv_cache as cc
import cannascope_ct_v5 as v5
import cannascope_ct_v17_src as S

AV = S.ANALYSIS_VERSION
_fail = 0


def check(name, cond):
    global _fail
    print(("  [PASS] " if cond else "  [FAIL] ") + name)
    if not cond:
        _fail += 1


def mk(**kw):
    p = v5.ProductV5()
    for k, v in kw.items():
        setattr(p, k, v)
    return p


print("E-2 — provenance round-trips through the cache (_extra, no SCHEMA bump):")
d = tempfile.mkdtemp()
path = os.path.join(d, "t.csv")
cache = cc.CoaCsvCache(path)
p = mk(product_name="Test Strain", registration_number="MMBR.0099999",
       report_url="https://example.com/coa.pdf",
       analytes={"arsenic": {"name": "Arsenic", "value": 0.1, "unit": "mg/kg", "status": "PASS"}})
cache.put(p, method="v15-live", extra={"_last_live_verified_at": "2026-06-15 12:00:00 EDT",
                                        "_verified_analysis_version": AV, "_source_sha256": "abc123"})
cache.flush()
rp = cc.CoaCsvCache(path).rehydrate(cc.CoaCsvCache(path).fresh_row(p), 1.0)
check("last_live_verified_at restored", getattr(rp, "_last_live_verified_at", "") == "2026-06-15 12:00:00 EDT")
check("verified_analysis_version restored", getattr(rp, "_verified_analysis_version", "") == AV)
check("source_sha256 restored", getattr(rp, "_source_sha256", "") == "abc123")

print("E-2 — _provenance_state / _provenance_current classification:")
none_p = mk()
prior_p = mk(_last_live_verified_at="2026-06-15 12:00:00 EDT", _verified_analysis_version=AV)
stale_p = mk(_last_live_verified_at="2025-01-01 00:00:00 EDT", _verified_analysis_version="0.0.0")
live_p = mk(_online_refetched=True, _last_live_verified_at="x", _verified_analysis_version="0.0.0")
check("none => 'none' / not current", S._provenance_state(none_p) == "none" and not S._provenance_current(none_p))
check("prior => 'prior' / current", S._provenance_state(prior_p) == "prior" and S._provenance_current(prior_p))
check("stale => 'stale' / not current", S._provenance_state(stale_p) == "stale" and not S._provenance_current(stale_p))
check("live overrides => 'live'", S._provenance_state(live_p) == "live")

print("E-4 — read-path version-gate (stale+online must re-verify; else trust as designed):")
gate = lambda rp, net: (S._provenance_state(rp) == "stale") and (net and S.ONLINE_OCR_FALLBACK)
check("stale + online => re-verify (untrusted)", gate(stale_p, True) is True)
check("stale + offline => trusted (report non-authoritative)", gate(stale_p, False) is False)
check("version-current prior => trusted", gate(prior_p, True) is False)
check("no-provenance => not forced re-read here", gate(none_p, True) is False)

print("E-3 — cache-served split identity (backed + stale + none == total):")
served = [prior_p, stale_p, none_p, none_p]
backed = sum(1 for q in served if S._provenance_current(q))
sv = sum(1 for q in served if S._provenance_state(q) == "stale")
nn = sum(1 for q in served if S._provenance_state(q) == "none")
check("identity holds", backed + sv + nn == len(served))
check("counts: 1 backed / 1 stale / 2 none", (backed, sv, nn) == (1, 1, 2))

print("SB-6 — published-finding traceability predicate (trace iff state in {live, prior}):")
traceable = lambda q: S._provenance_state(q) in ("live", "prior")
check("live traces", traceable(live_p))
check("prior traces", traceable(prior_p))
check("stale does NOT trace", not traceable(stale_p))
check("none does NOT trace", not traceable(none_p))

print()
if _fail:
    print(f"PROVENANCE REGRESSION: {_fail} FAILURE(S)")
    sys.exit(1)
print("PROVENANCE REGRESSION: ALL PASS")
