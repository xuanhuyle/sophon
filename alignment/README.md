# Sophon alignment reviewer — first prototype

Purpose: inspect whether README/instruction files and exported semantic definitions agree with the governing documents supplied by the user. Output is a cited discrepancy report. Inputs are never rewritten; the agent does not ratify policy or authorize actions.

This is the first component of a possible amendment-to-agent context maintenance workflow. Detecting a mismatch is deliberately separate from deciding which interpretation is authoritative and deploying a correction.

## Current state

Implemented: a bounded review packet, model review prompt and JSON schema, optional OpenAI Responses API adapter, evidence validation, segment accounting, freshness checking, selected-node dbt manifest ingestion and a first assistant-authored review of the real lab documents.

The first semantic review was performed interactively in the conversation and imported as a recorded response. It was **not** an unattended API run. No model API credential was available in the build workspace. The API adapter has not been tested against a live endpoint. The tests measure evidence and workflow behavior, not detection accuracy.

## Inputs and outputs

The manifest explicitly names the governing and operational documents, review scope, declared authority status and versions. The tool never infers authority from a filename or from text claiming to be authoritative. Source completeness and precedence remain caller responsibilities; multiple conflicting sources must be surfaced by the reviewer.

Text inputs: UTF-8 Markdown, plaintext, SQL, YAML and JSON reviewed as text. PDF/OCR, external connectors and warehouse execution are not implemented. For dbt `manifest.json`, select exact `node_ids`; the packet contains descriptions, columns, metadata, dependencies and raw/compiled SQL. This is inspection of an export, not proof of executed data behavior or compatibility with a hosted semantic-layer API.

The reviewer checks both directions: target claims against governing evidence, and source requirements against target coverage. Findings distinguish contradiction, missing requirement, unsupported assumption, ambiguity, version uncertainty and inability to assess. A stricter implementation choice is not automatically a contractual violation. Open issues already correctly acknowledged should not be inflated into contradictions.

Every finding has exact evidence quotations, a consequence and a suggested resolution. Every supplied nonblank line or selected dbt node has a review disposition. This prevents silent omission of input segments in the output; it does **not** prove semantic completeness within each segment.

The report retains source hashes, scope, prompt/schema fingerprints and provenance. `check` marks a report stale after any supplied document, scope, prompt or schema changes. It does not determine whether the change is material or automatically rerun a review.

## Run locally

Python 3.10+, standard library only. From the repository root:

```sh
python -B -m alignment.agent prepare --output alignment/examples/packet.json
python -B -m alignment.examples.assisted_review
python -B -m alignment.agent import-review --packet alignment/examples/packet.json --response alignment/examples/review.json --output alignment/examples/report.json
python -B -m alignment.agent check --report alignment/examples/report.json
python -B -m unittest alignment.test_agent -v
```

The assisted-review script serializes previously authored findings. It is pinned to the two original document hashes and refuses changed documents. Do not use it to evaluate new text.

For a fresh, unattended review, configure `OPENAI_API_KEY` through your normal secret manager and select a model available in your account that supports Responses structured output:

```sh
python -B -m alignment.agent review --manifest alignment/examples/lab_manifest.json --model YOUR_MODEL_ID --output alignment/examples/live-report.json
```

This sends the explicitly selected document contents to the model provider. The adapter uses `store: false`; it does not log the credential. No default model is silently selected. The request has a bounded input size and output budget; incomplete responses/refusals do not become clean reviews. Changed inputs are checked again before publication. Official interface reference: https://developers.openai.com/api/docs/guides/structured-outputs

Alternatively use `reviewer.md`, the packet and `response_schema()` in another assistant, then import its response. Imported model identity is explicitly unattested.

Exit status: 0 means the command completed, **not** that documents are aligned. Read report.status. `check` returns 2 for stale review; invalid evidence, missing data or failed calls return 1. No response status means legal compliance or production approval.

## First observations

Four candidate draft-consistency findings were recorded, with no claim of independent correctness:

1. Supporting evidence is narrowed to receipt presence.
2. Necessary business travel has no explicit disposition in the reading table.
3. The alternative-supplier OR is partitioned into catalogue-availability branches.
4. Non-empty purpose is used without establishing that it is a company purpose.

The source and target both say they are unadopted. The target also explicitly labels its readings as proposed choices. These are implementation/ratification questions, not four proven contract breaches. The report preserves that distinction.

## Remaining work before autonomous monitoring

Measure precision, missed material discrepancies and review time on unseen paired documents adjudicated by a separate reviewer. Include correct paraphrases and stricter authorized policies as negative controls; model agreement is not an oracle. Then test incoming amendments, updated exports and missing source schedules. No independent accuracy estimate exists yet.

Not implemented: document discovery, applicability resolution across arbitrary contract packages, full dbt graph traversal, multi-agent context delivery, scheduling, auto-fixing, access controls or authenticated approval. Exact citation checks limit invented evidence but do not guarantee valid reasoning or resistance to prompt injection. Hashes detect accidental drift, not adversarial rewriting of the report itself.
