# IPSA published-review authority-boundary probe

This is an independently reproducible **small case-study and scope-guard** constructed from five primary IPSA Compliance Officer review reports. It is a manually curated test of case-specific authority, timing and source provenance. It is **not** a representative sample or evidence of lower governance effort.

`corpus_inventory.json` additionally indexes all 46 PDF links on the official completed-reviews page with source URLs and hashes. All 46 were downloaded and extracted locally during this run; the large PDFs and extracted text are not bundled. To regenerate them, run `python sophon_cases/corpus_index.py --download` (requires `pdftotext`). One tribunal decision extracted only 13 characters and will need OCR before analysis. The inventory's keyword flags are navigation aids only.

`cases.json` records what was known at an initial claim and what the public review later established. The reports may contain information gathered only during review, so the case narrative is not assumed to have been available when the original claim was submitted. `authority_events.json` contains a *minimal, explicitly typed* subset of the reported decisions. The original grant correspondence is not public; even for an in-period match, the probe returns `AUTHORITY_EVIDENCE_ONLY`, never permission to reimburse.

Run from the repository root:

```bash
python sophon_cases/authority_probe.py COM-1613 personal_effects_storage 2024-02-01
python sophon_cases/authority_probe.py COM-1613 personal_effects_storage 2024-04-01
python -m unittest discover -s sophon_cases -p 'test_*.py'
```

The five original report URLs and the relevant paragraph ranges are in `cases.json`. This test is deliberately adversarial: grants stay within their named beneficiary, purpose and documented service period; announced guidance is non-executable; individual review outcomes cannot silently become general policy. The Davies review expressly disclaims future precedent for its 50% remedy. An in-window result still lacks the invoice and payment-specific proof needed for clearance.
