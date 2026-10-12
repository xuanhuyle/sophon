# Sophon V0 — normative semantic layer walking skeleton (LAB ONLY)

**Status:** runnable exploratory prototype; not a compliance product and not an E0–E5 result. **Stdlib Python 3.10+; no API keys or external dependencies.** No legal conclusions, genuine legal authority, production enforcement, or generalized natural-language comprehension are claimed.

## What actually works

1. Submit *text* of a laboratory customer contract and internal policy over HTTP. The narrow extractor recognizes two explicit sentence patterns (service credit and credit-approval limit), **deriving their numeric parameters from the supplied words**. Every unmatched clause becomes `UNRESOLVED`, never a fabricated rule.
2. Review the proposed rules and simulate approval. Until lab approval, the previous version remains the active one. Keep exact source excerpts, document hashes, observation/approval and effective dates, previous versions and an append-only audit **within this SQLite file** (not tamper-proof).
3. Two **different Python client programs**, support and billing, call the same `/assess` JSON interface. Neither contains customer contract thresholds, credits or amendment values. Both obtain the same source-scoped normative answer, and no client can authorize an actual external action.
4. Ingest a contract amendment (credit rate 5% → 10%). Until simulated approval both clients get 5%; after approval both get 10%, without editing their code. The internal policy routes a newly >EUR30 credit to founder approval. A dated future amendment does not apply prematurely. Historical as-known queries may select the previous version.
5. Negative tests: unsupported natural-language clause yields `UNRESOLVED`; absent policy or operational facts produces `NOT_VERIFIED`/`NEEDS_FACTS`; broken operational facts reject; proposed or unapproved amendment has no operative effect.

**Parser coverage is intentionally extremely narrow.** It only accepts exactly the two grammar patterns in `sophon_v0.py` (one sentence per line), on already extracted text. It cannot read PDFs, prove that a contract is signed, distinguish all legal exceptions, reconcile legal conflicts, validate real maintenance windows, check operational source-system facts, or interpret arbitrary agreements. Its output is advisory, and even the `APPROVED` label is **LAB_SIMULATED** and not identity-verified. Its `/approve` endpoint is unauthenticated. The HTTP server only binds to loopback. Do NOT expose it to a network, feed it real confidential contracts, or authorize actions based on it.

## Run the complete demonstration

Windows PowerShell, from the repository root:

```powershell
python prototype\normative_layer\demo.py
python -m unittest discover -s prototype\normative_layer -p "test_*.py" -v
```

On macOS/Linux, substitute `/` for `\`.

To explore persistent state and use the HTTP API:

```powershell
python prototype\normative_layer\sophon_v0.py serve --db .sophon-v0.sqlite --port 8765
```

Routes: `GET /health`, `POST /documents`, `POST /approve`, `POST /assess`, `GET /audit`. The demo uses temporary SQLite and automatically closes the server; the `serve` command persists data in your chosen SQLite path. `demo.py` launches two different subprocess clients, so the example exercises the actual JSON HTTP interface, not just in-process calls.

**Minimal request examples** (see `demo.py` for full, runnable inputs):

`POST /documents`: `{"doc_key":"customers/acme","kind":"customer_contract","effective_from":"2026-01-01","text":"If monthly service availability falls below 99.5%, the customer is entitled to a service credit of 5% of the monthly subscription fee, excluding scheduled maintenance."}`.

`POST /approve`: `{"document_id":1,"reviewer":"LAB founder"}` — *simulation only*.

`POST /assess`: `{"contract_key":"customers/acme","policy_key":"policies/credits","on_date":"2026-10-12","facts":{"period_minutes":43200,"outage_minutes":300,"scheduled_maintenance_minutes":0,"monthly_fee_eur":"400"}}`.

The response includes `execution_authorized: false`, `facts_provenance: SUPPLIED_BY_CALLER_NOT_INDEPENDENTLY_VERIFIED`, the source clause excerpts + hashes, governing versions, an unresolved list, calculation, and an approval route. The clients cannot issue credits or transfers.

## Observed in the initial authoring environment

- `python -m unittest discover -s prototype/normative_layer -p 'test_*.py' -v`: **6 tests passed** on Python stdlib on Linux, October 12, 2026.
- `python prototype/normative_layer/demo.py`: **both independent clients** reported EUR20.00 with contract v1, stayed at EUR20.00 with **unapproved v2**, then reported EUR40.00 under **LAB-approved v2** and the founder-review threshold. No client source changes.
- **GitHub Actions passed on both Windows and Ubuntu (Python 3.11)**: six unit/integration tests and the full two-client demo. Results establish this tiny grammar-specific behavior only, not reliable real-world contractual interpretation.

## Next engineering step, driven by observed failure

Feed a second independently authored contract **without changing application code**. The extractor will likely abstain because the grammar is narrow. Preserve that failure and add an LLM extraction *proposal* adapter with source spans and independent review. Do not give the LLM authority to approve meaning or modify active records. Separately, replace caller-supplied operational facts with a typed, authenticated read-only adapter to a real system of record. Do not develop a DSL until actual representational failures demand it.

## Charter boundary

This prototype explores the owner's newer **normative semantic layer** hypothesis: a cross-agent source of governing context. It is a **proposed architectural expansion** beyond `SOPHON_CHARTER.md` v1.1's existing BI-semantic-layer-only integration boundary. The Charter on main is deliberately unchanged. The owner must explicitly ratify any permanent Charter change. E0–E5 research branches/PRs remain untouched.
