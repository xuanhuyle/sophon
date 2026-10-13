# Observed local run — 13 October 2026

**Source:** Five fictional LAB clauses (`clauses.json`).

**Actual operation:** Invoked `python prototype.py --mode demo --output results_demo.json` and `python -m unittest discover -s . -p 'test_*.py' -v` in the artifact directory (stdlib Python 3.13.5, Linux).

**Output:** 5/5 clauses processed, 3 provisional candidates for human review, 2 held as unresolved (C3: missed claim deadline; C4: missed exception and missing schedule). Every proposed transposition remains `NOT_AUTHORIZED`. 15/15 unit tests passed.

**Epistemic boundary:** In demo mode the Jev predictions and BOTH reviewer responses are all predetermined hand-authored fixtures. **Zero live Jev API requests and zero live LLM reviewer requests.** Do not report the output as classifier accuracy, actual LLM disagreement, adversarial model recall or contractual compliance.

**Next live check:** With real Jev and LLM credentials, execute one pass using the frozen clause file. Preserve model IDs and raw outputs with the source hash. An expert-independent review is still needed for any quality claim.
