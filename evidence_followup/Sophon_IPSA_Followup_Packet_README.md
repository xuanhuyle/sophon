# Public IPSA follow-up evidence

This supplement accompanies the Sophon packet already sent to Claude Code. Start with `Sophon_IPSA_Followup_Test_Final_2026-09-21.md`. The `sophon_cases/corpus_inventory.json` file freezes 46 PDF source URLs and hashes; the `sophon_ipsa_followup/` folder contains a local reproduction script, machine navigation inventory and 13 source-grounded case observations. No raw PDF is redistributed here.

Requirements: Python 3, `pdftotext`, `pdftoppm` and `tesseract` on PATH, plus access to the official PDF URLs listed in the inventory. From the extracted packet root:

```bash
python sophon_ipsa_followup/prepare_corpus.py
python sophon_ipsa_followup/audit.py
python sophon_ipsa_followup/verify_checks.py
```

The first command downloads and verifies all 46 frozen PDFs and OCRs the 13-page tribunal decision. If a hosted PDF has changed, the hash check stops and requires inspection. The next commands reproduce document-level phrase counts and confirm 22 source-text anchors in 13 hand-selected cases. The analyst's interpretation remains a qualitative, post hoc assessment. The 2023–24 claims replay and five-case authority probe are in the earlier packet and are not reproduced in this supplement.
