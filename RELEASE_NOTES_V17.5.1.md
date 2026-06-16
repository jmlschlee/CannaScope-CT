# CannaScope CT V17.5.1

A correctness + evidentiary-provenance release. SOFTWARE 17.5.1 / ANALYSIS 17.3.1.
Verified by a full forensic statewide run (2023-01-01 → 2026-06-15, `--validate`): 18,309 COAs,
99.9% live-verified, reconciled to 100%, **all ship-blocker and producer-identity gates pass**,
status PASS WITH MINOR WARNINGS.

## Parser accuracy
- **B-1 — Total THC > Total Cannabinoids field-mapping fix.** Analytics Labs COAs print a formula legend
  after the data rows (`Total Active THC = D9-THC + (THCA·0.877) …`). On distillates (no THCA) the parser
  matched THCA inside that legend and read the **"9" out of "D9-THC"** as THCA = 9.0%, inflating derived
  Total THC above Total Cannabinoids on ~1,221 records (237 of them tripped the consistency flag). The
  cannabinoid parser now stops at the legend, so only real data rows are read. 237 impossible inversions →
  0; 1,210 fabricated THCA values scrubbed from the embedded cache. Real THCA data rows (incl. Analytics
  flower) are preserved. New gate: THC>TotalCannabinoids must stay < 1% of freshly-read COAs.

## Evidentiary provenance (cache hardening — "verified once, cached, reused" with proof)
- **Per-record provenance** — every live-verified cache write records when it was verified, under which
  analysis version, and the SHA-256 of the source COA bytes.
- **Honest reuse accounting** — cache-served records are split into version-current (trusted reuse),
  stale-version (re-verify), and no-provenance (the real coverage concern); reuse is never called
  "unverified," and never implied to be fresh-live.
- **Version-bump invalidation** — a value verified under a superseded analysis version is re-verified live.
- **Traceability ship-blocker (SB-6)** — every published finding must trace to a recorded live-verification
  event; a forensic `--validate` run aborts otherwise. Export: `cache_provenance_audit.csv`.
- **Online cache-audit gate** — an online, cache-backed run must actually live-audit its cached rows.

## Transparency / readiness
- **Per-year readiness evidence** — the four readiness criteria (sample size, lab-layout coverage, era
  confidence, core-panel parse) are now shown with the measured value vs threshold for every window year,
  with a guard that the evidence can never contradict the READY/PARTIAL/NOT-READY verdict.
- **Explicit 2015 isolation** — when a window starts after 2015, the report affirms (and a guard enforces)
  that zero 2015-or-earlier records contributed to the window.

## Report integrity
- **Producer identity** — a legal entity could leak as a producer label in two statewide tables
  ("DXR Finance 3, LLC (Theraplant …)"); both now show the clean trade name. New in-program G2
  ship-blocker aborts if any `LLC/Inc./Corp./Co. (` label appears in the report body.
- **Version label** — the cover/footer version is now derived from `SOFTWARE_VERSION` (no more drift).

Additive release — all prior releases preserved. The hosted app (cannascope-ct.streamlit.app) updates
automatically with the committed self-contained build.
