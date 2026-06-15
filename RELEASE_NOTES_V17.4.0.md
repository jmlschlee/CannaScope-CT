# 🌿 CannaScope CT — V17.4

**Source-verified Connecticut cannabis transparency reporting.** V17.4 makes the program's **regulatory standards accurate** — it fixes the THC-potency standard, which previously read **“no cap” for every year**, and bakes in Connecticut's **real, dated, triple-verified Total-THC caps**. It also adds **product + producer identity** to the Multiple / Conflicting COA tables.

🔗 **Live web app:** https://cannascope-ct.streamlit.app &nbsp;·&nbsp; 💻 Desktop downloads below (Windows / macOS / Linux).

---

## 🆕 Headline changes

### 🧪 Accurate, dated CT THC potency caps (was “no cap”)
Connecticut **does** cap Total THC for **adult-use** sale, and the cap has **changed over time**. The program now bakes in the verified, dated, **cited** caps — and the standards tables (both “Applicable CT Standards by Test Date” and the year-by-year ledger) show them instead of a blanket “no cap”:

| Product type | 2023 → Sep 30 2025 | **Oct 1 2025 →** (PA 25-166) |
|---|---|---|
| Flower / plant material | 30% | **35%** |
| Concentrate / other non-vape | 60% | **70%** |
| Vape cartridges | **exempt** | exempt |
| Edibles | 5 mg/serving · 100 mg/package | same |
| Medical-only / Legacy | **no cap** | no cap |

- **Triple-verified** against CT primary + secondary sources: CGS Chapter 420h, **CT PA 21-1 (RERACA)**, **CT PA 25-166** (raised the caps, eff. 2025-10-01), and **CT PA 26-8** (HB 5350, signed 2026-05-04 — keeps 35% flower, removes the concentrate cap, **effective 2026-10-01** so noted, not yet applied).
- **Correctly qualified:** the caps apply to **adult-use retail sale**; **medical-only, “legacy,” and all vape cartridges are EXEMPT**; edibles use a mg dose limit, not a %.
- Shown as **VERIFIED reference standards** with citations and an as-of date. They are **not** auto-applied as violation flags — the registry's market flag is brand-level, so high-potency items registered for both markets may be lawfully sold medical-only; presenting them as violations would be inaccurate.
- New legal sources (PA 25-166 / PA 26-8 act PDFs) added to the live-consult list; legal-fetch cache version bumped so stale entries re-verify.

### 🧾 Conflicting-COA tables now carry product + producer
The **Multiple / Conflicting COA Records** comparison tables previously showed only lab names and dates. Each case now carries a tinted **Product** and **Producer** identity band (and the within-document cases carry the same line), so a reviewer sees *what* product and *which* producer each comparison is about — not just labs and dates.

> Every flag is a **lead to verify against the official COA — never a conclusion**, and **never an allegation of fraud or intent.** CannaScope is independent and **not** affiliated with the State of Connecticut, any lab, or any producer.

---

## 🔬 Unchanged (still accurate)
The microbial / total-aerobic / pathogen (Salmonella · STEC · Aspergillus) / heavy-metal standards were already VERIFIED, cited, and corroborated by the action limits printed on the COAs — those were correct and are unchanged. Detection logic is unchanged (`ANALYSIS_VERSION` stays 17.3.0); this release updates **regulatory reference accuracy + report identity detail**.

---

## 🚀 Run it

```bash
python CannaScope_CT_V17.py statewide --since 2024-01-01 --until 2026-06-15            # live-first
python CannaScope_CT_V17.py statewide --since 2024-01-01 --until 2026-06-15 --validate  # full-window, 100% live-verified
python CannaScope_CT_V17.py concern --example                                          # single-product
```

Each OS zip bundles the self-contained `CannaScope_CT_V17.py` (embeds the triple-verified COA dataset) + README + requirements + LICENSE + install/run scripts. Python 3.9+; `pip install -r requirements.txt`.

---

## ⚖️ Important
Independent, informational transparency tool — **not** medical/legal/professional advice and **not** affiliated with or endorsed by the State of Connecticut, any lab, or any producer. Regulatory citations are confirmed as of the report's “as-of” date; always confirm current text at eRegulations.ct.gov / DCP. Every flag is a lead to verify against the official COA, not a conclusion. Provided as-is, no warranty.

🌿 *All prior releases are preserved; this is an additive release.*
