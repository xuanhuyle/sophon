# Jev Fact Sheet (TypeSafe AI) — as of 2026-09-21

**Evidence caveat.** typesafe.ai, docs.typesafe.ai, evals.typesafe.ai, HN, X, Reddit, TechCrunch, The Register and most press were egress-blocked for every research facet. Every [VENDOR] item below is reconstructed from (a) TypeSafe's own GitHub artifacts (SDK source, SKILL.md, adapter), (b) an unofficial Chinese mirror of docs.typesafe.ai (github.com/Bald0Wang/jev-docs-zh), or (c) third parties quoting the docs. Exact vendor wording may differ from the live pages. All independent measurements are on `jev-1.13.0` (or the gateway build `typesafe/jev-1.13-20260917`) between 2026-09-16 and 2026-09-21, i.e. six days of data on one model version.

---

## 1. What Jev is

Jev is a closed-weights, hosted-only, text-only model from TypeSafe AI (San Francisco; announced 2026-09-15 in early access, waitlist removed 2026-09-21) that does not generate text. A caller sends a "state" (string, JSON object, or array of text) plus a map of typed questions to `POST https://api.typesafe.ai/v1/systemone`, and receives, per question, one of three typed outputs: a **Choice** (selected option, a probability for every option, and a scalar "confidence"), a **Score** (probability-weighted mean over 2–10 ordered levels, per-level probabilities, confidence), or a **Noul** (a single 0–1 probability of "yes", no confidence field). TypeSafe says all questions in a request are evaluated independently against the state in a single non-autoregressive pass, that the model is trained with an undisclosed method it calls RLCD ("Reinforcement Learning for Calibrated Decisions"), and that outputs are "calibrated". The current version is `jev-1.13.0` (aliases `jev-latest` and `jev-preview` both resolve to it); pricing is $0.042 per million input tokens with output free; input is capped at ~32k tokens for state plus the longest question and 64k per request; no explanation, rationale, or evidence span is returned. No paper, model card, parameter count, or calibration curve has been published.

---

## 2. Product surface

**Question types**
- Choice: `{type:"choice", instructions?, criteria:{option: description}}`, up to 255 options → `{choice, probabilities, confidence}`. [VENDOR] Response shape confirmed live by third parties (https://github.com/typesafe-ai/typesafe-sdk-js/blob/main/src/types.ts; https://github.com/typesafe-ai/skills/issues/6); the 255 cap is only restated from docs — no independent 256-option rejection reproduced, though https://github.com/nibzard/decision-model-benchmark reports "400 Too many choices" at 256/384/512. [INDEPENDENT for the cap, per that one repo]
- Score: 2–10 ordered levels → `{score, legend, probabilities, confidence}`; score is a probability-weighted mean and can land between levels. [VENDOR] Live API enforces ≤10 levels (400 "Too many score levels") but **accepts a single level** (HTTP 200, confidence 1.0), contradicting the documented 2-level minimum (https://github.com/typesafe-ai/skills/issues/6). [INDEPENDENT]
- Noul: `{type:"noul", instructions?, criteria?:{true?, false?}}` → `{noul: 0..1}`; 0.5 = yes and no equally likely; no confidence field. [VENDOR, shape INDEPENDENT] A noul with neither instructions nor criteria is rejected 400 (https://github.com/typesafe-ai/skills/issues/1). [INDEPENDENT]

**Outputs**
- One answer per question keyed by caller id; response also carries `model` (versioned id) and `usage{input_tokens, output_tokens}`. [INDEPENDENT] (https://github.com/jujumilk3/jev-calibration-audit; https://github.com/typesafe-ai/skills/issues/6)
- Output tokens are non-zero (~23/call) although billed free. [INDEPENDENT] (https://github.com/SamuelSacco/jev-exploration)
- Probabilities are rounded to two decimals; exactly-0 and exactly-1 values are frequent (1,051 of 2,000 option probabilities exactly 0 on OpenBookQA). [INDEPENDENT] (https://github.com/scienthoon/jev-ood-calibration; https://github.com/jourdanlabs/assay-001)
- No explanation, rationale, citation, evidence span, or input location. [VENDOR, confirmed by SDK types and every independent run] (https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md)

**Confidence definition**
- "Choice/Score confidence summarizes distribution concentration, not overall workflow correctness or permission to act." [VENDOR] (SKILL.md, same URL)
- Docs: "a margin, not a probability that the answer is right"; the docs' interactive demo approximates it as (k·max_probability − 1)/(k − 1) and defers the exact definition to a future guide. [VENDOR] (mirror: https://raw.githubusercontent.com/Bald0Wang/jev-docs-zh/main/content/confidence.md)
- TypeSafe's written survey answer (second-hand): formula "Not published, and it drifts across model versions." [VENDOR, second-hand] (https://github.com/factorysemantics/factorysemantics-mes/pull/71)
- Empirically indistinguishable from normalized entropy of the returned distribution (AUROC 0.706 vs 0.705). [INDEPENDENT] (https://github.com/FirasSX914/Janus/blob/main/RESEARCH.md)

**Inputs**
- State: string, JSON object, or array of text; text only, no image/audio/video. [VENDOR] Empty `""`, `{}`, `[]` accepted; `null` rejected 422 despite SDK types allowing it. [INDEPENDENT] (https://github.com/typesafe-ai/typesafe-sdk-js/issues/6)
- Questions must be a map keyed by id using `type`/`instructions`; array form rejected 400. [INDEPENDENT] (https://github.com/kerpopule/hermes-jev-skills/issues/2)
- Backticked dot/index paths (e.g. `` `ticket.messages[0].text` ``) recommended for nested state. [VENDOR] (SKILL.md)

**Limits**
- 64k tokens per request (state + all questions); 32k for state + the single longest question; oversized state rejected, not truncated. [VENDOR] Rejection shape independently reproduced: HTTP 400 `{"error_type":"max_tokens_exceeded"}` on an 88k-token state after 572 ms, "but was still billed". [INDEPENDENT] (https://github.com/burin-labs/harn/issues/8540). Exact boundary (~32.2k accepted / ~33.6k rejected) is a single unverified report. [UNKNOWN]
- Gateways list a flat 32,000-token context (OpenRouter, Cloudflare, Portkey). [VENDOR-restated]
- Max questions per request: not documented (cookbooks show 13 and 54; 36 in one independent call). [UNKNOWN]
- Max output size, total context window: not published. [UNKNOWN]
- Rate limits: 250,000 tokens/s and 1,200 req/min, "dynamic during early access", 429/529 on exceed. [VENDOR] One independent ledger (2026-09-18) recorded "no numeric ceiling" published — sources conflict. [UNKNOWN whether currently documented]
- Language: English primary; "other languages, including CJK scripts, are handled but not equally well". [VENDOR]

**Pricing**
- $0.042 per 1M input tokens, output free ("$42 per billion tokens"). [VENDOR] Per-token rate independently reconciled from OpenRouter billing ($0.0000153 for 364 tokens). [INDEPENDENT] (https://github.com/WallerChen/jev-measured)
- Measured per-decision cost: $0.0000153–$0.0000268 on 350–640-token states; $0.0399 per 1,000 decisions at ~950 tokens/decision. [INDEPENDENT] (same; https://github.com/ghubnab99/jev-enterprise-decision-fabric; https://github.com/fstandhartinger/jevbench)
- Rejected over-budget requests are billed. [INDEPENDENT] (harn#8540)
- Vercel AI Gateway currently bills $0 for Jev on a free credit; classifier.dev resells at $20/month for 200k classifications/day. [INDEPENDENT] (https://github.com/shitianfang/jev-use/blob/main/bench/RESULTS.md; https://github.com/mrmps/classifier-dev)
- $5 free credit on new accounts. [VENDOR, via snippet]

**Latency**
- "70–500 ms end-to-end", "response time stays flat as questions are added". [VENDOR]
- Direct API p50: 313 ms (jev-measured), 280 ms/p95 397 ms (Seoul, jujumilk3), 376/545 ms (ghubnab99), 421/542 ms (themsquared), 129 ms from a laptop (jeff); server-reported service time 70–81 ms; network floor 160–200 ms. [INDEPENDENT] (https://github.com/WallerChen/jev-measured; https://github.com/jujumilk3/jev-calibration-audit; https://github.com/logan-markewich/jeff)
- Via gateways: Vercel 225–440 ms p50 with a ~0.43 s floor invariant to a 600× input-size change; OpenRouter 734 ms p50 / 1,739 ms p90; from China ~890 ms; Germany 0.65 s. [INDEPENDENT] (https://github.com/ickma2311/jev-baselines-eval; https://github.com/typesafe-ai/skills/issues/3; jevbench)
- Adding questions is nearly free: 36 questions in one call in 1.61 s; 16 vs 1 question adds 14 ms; 12 questions batched 224 ms vs 2,662 ms serially. [INDEPENDENT] (SamuelSacco; jujumilk3; jev-use)
- Throughput saturates near 11 req/s; p90 >1 s under 8-way concurrency; Vercel free tier ~1 req/min. [INDEPENDENT] (https://github.com/priorbench/jev; ickma2311)

**Availability**
- Hosted API only; no on-prem/VPC/edge "now or planned"; US-hosted, no EU region; closed weights; ZDR enterprise-only; no subprocessor list. [VENDOR, second-hand] (factorysemantics PR #71; https://github.com/fdsimms/todo/issues/2781)
- Direct API has no retention header/field; ZDR is requestable only via the Vercel gateway flag. [INDEPENDENT] (https://github.com/coldteadotai/abide/issues/1)
- No public SLA/uptime commitment; status page showed 99.854% over 90 days with a 5-min incident 2026-09-17; 529 "system_overloaded" hit 5 of 6 calls for one tester in launch week. [VENDOR status page via snippet / INDEPENDENT anecdote]
- Also served via Vercel AI Gateway (`typesafe-ai/jev`, no version exposed), OpenRouter alpha `/api/alpha/decisions` (`~typesafe/jev-latest`, `typesafe/jev-1.13-20260917`), Cloudflare Workers AI (`typesafe/jev`). [INDEPENDENT]
- SOC 2 / ISO 27001 / HIPAA status: not found. [UNKNOWN]

**Versioning**
- `jev-latest` = stable alias, `jev-preview` "should be better in most ways"; both resolved to `jev-1.13.0` on 2026-09-18; `GET /v1/models` lists only the two aliases with release_date 2026-09-10. [INDEPENDENT] (https://github.com/typesafe-ai/skills/issues/7; jujumilk3)
- Docs: pin a versioned id once thresholds are tuned because "an alias moves when a new release ships". [VENDOR]
- jev-1.12 existed (September cookbooks); OpenRouter says 1.13 released 2026-09-18; no model changelog page exists (only SDK changelogs). [UNKNOWN what changed]
- Deprecation policy: "pinnable, with no fixed forced-retirement window". [VENDOR, second-hand]
- No actual alias move has been observed yet; drift risk is structural, not demonstrated. [UNKNOWN]

**SDKs / errors**
- `@typesafe-ai/sdk` (npm, Node ≥20; v0.6.0 2026-09-15, no release since) and `typesafe-sdk` (PyPI; 0.0.1a0 2026-09-09 → 0.7.1 2026-09-21); default model `jev-latest`, 10 s per-request timeout. [INDEPENDENT via registries]
- Live error codes diverge from docs: semantic validation → 400 (docs say 422); schema failures → 422; missing key → 403 (docs say 401); JS SDK maps 402/409/413 to generic APIError; 11 JS SDK issues open with no maintainer reply as of 2026-09-21; Python SDK v0.7.0 leaked API key into exception text (fixed 0.7.1). [INDEPENDENT] (https://github.com/typesafe-ai/skills/issues/1, /issues/8; https://github.com/typesafe-ai/typesafe-sdk-js/issues/13; https://github.com/typesafe-ai/typesafe-sdk-python/issues/9)

---

## 3. Independently demonstrated capabilities

Only items with third-party measurement; sample sizes noted.

- **Schema is always satisfied.** Zero type/schema errors across 8,576 responses (https://github.com/jourdanlabs/assay-001), 4,621 calls (https://github.com/scienthoon/jev-ood-calibration), 19,772 requests (https://github.com/bitnovus/jev-spam-eval). The model cannot select an option it was not offered.
- **Questions in one request are independent and cheap.** 16 bundled questions (incl. 5 hostile) shift confidence 0.008 and flip 0.4% of answers on 250 items (jujumilk3); 36 questions returned in one 1.61 s call (SamuelSacco).
- **Sub-second decisions at ~$0.02–0.04 per 1,000.** See §2 latency/pricing. Against properly enum-constrained LLMs: 3.0–3.1× lower latency and 5–16× lower cost than Haiku 4.5 / Gemini 3 Flash (jev-use, n=40×2); 6.5× faster p50 and ~323× cheaper per decision than Claude Opus 5 (ghubnab99, 111 cases); 45×/274× cheaper than Gemini 3.8 Flash / Claude Fable 5.1 at medium reasoning (https://github.com/gemanor/jev-code-review-benchmark, 1,080 calls).
- **Accuracy at parity with small/mid LLMs on easy, well-specified classification.** Tool-call gate 90.1% vs Opus 5 91.9%, McNemar p≈0.75 (ghubnab99); code-rule review 98.0% vs 100%/100% (gemanor); reranking nDCG@10 0.692 vs Cohere Rerank 4 Pro 0.691, CI −0.009..+0.012 (https://github.com/anessbelbati/jev-rerank-bench, 1,617 queries); business email 96.4% vs Gemini 3.8 Flash 98.5% (X post, n=1,565, method unverifiable); spam 98.64% vs trained TF-IDF 98.87% on 5,733 emails, and 95.3% vs 75.3% recall on 853 recent phishing emails (bitnovus).
- **Beats clean zero-shot NLI encoders.** +0.05 to +0.13 accuracy over uncontaminated DeBERTa-v3-large-NLI on all 7 sets; zero-shot worth ~230 labelled examples on AG News/Banking77, >2,048 on SST-2/TweetEval/PAWS; contamination drop on post-release arXiv only −0.035 vs −0.113 for DeBERTa (https://github.com/zhuyansen/jev-zeroshot-vs-bert, 872–1,000 items/set).
- **Prompt-injection detection with deployment context**: 96.5% accuracy / 95.1% recall / AUROC 0.993 on 662 deepset messages (https://github.com/Gaurav-Gosain/jev-sec-bench); 100% attack catch in a 320-item held-out firewall test (https://github.com/AnshChoudhary/typesafe-ai-firewall).
- **Explicit abstain option works when offered**: 95% abstention on 300 unanswerable KoBBQ items, ECE 0.023 at a 0.024 noise floor (jujumilk3).
- **Option-order robustness on clear items**: reversing two options shifted probability 0.005 with 0/400 argmax flips (jujumilk3); reversing passage order changed top-1 on 24.7% of rerank queries vs 92.6% for Qwen2.5-1.5B (rerank-bench).
- **Numeric/date comparison better than vendor warns**: number comparison and date ordering 99.6% across 13 designs, negation 100% (https://github.com/priorbench/jev, 5,721 calls, pre-registered).
- **Near-calibrated on in-distribution/public sets**: OpenBookQA ECE 0.024, CommonsenseQA 0.032, HellaSwag 0.029 (scienthoon); CLINC150 0.0204 (ASSAY-001); 20 Newsgroups 0.045 (https://github.com/yodablocks/jev-orderby-bench); MMLU probe n=1,200 ECE 0.031 (Archer Hume, cited by jujumilk3, page blocked).
- **Ranks #1 on JevBench v1.2** (534 frozen decisions, composite of intelligence/calibration/speed/cost): 75.4 vs SemIf 74.7, djev 74.3; hard-tier 74.1% vs best open 69.5% (https://github.com/fstandhartinger/jevbench). Note the #1 rests on speed/cost axes; on intelligence alone Jev is #5.

---

## 4. Vendor-only claims (not independently reproduced)

- "Calibrated: higher confidence means higher accuracy"; probabilities "optimized against outcomes" via RLCD. No ECE, reliability diagram, dataset, or method published anywhere reachable (ASSAY-001 PROTOCOL.md transcription; SKILL.md; 44 mirrored docs pages swept).
- "70–500 ms end-to-end" (kenhuangus/jev-usecases quoting docs). Independent: fair as service time (~76 ms), misleading end-to-end.
- "40×–200× faster, 40×–400× cheaper"; "193.6× faster than Claude Sonnet 5, 444.6× cheaper than Claude Opus 5"; "two orders of magnitude"; also 10–125×/22–805× and 20–200× on other vendor surfaces (datacamp, spring.io, tomshardware snippets; SamuelSacco ledger). TypeSafe itself calls these "on the higher end of real world gains".
- Four-workflow eval: Jev 67.8% vs GPT-5.6 Sol 74.1%, Opus 5 73.1%, Terra 67.9%; 0.4 s and $0.0004 per case. Reference labels = average of GPT-6 Astra and Claude Fable 5.1 outputs; workflows written by TypeSafe's own team (evals.typesafe.ai, blocked; restated by SamuelSacco, jenaiho).
- "0% structured-output error / 0% tool-call error" vs 0.58% (OpenAI Luna/Terra), 5.73% (Opus 5), 45.5% (Haiku 4.5). TypeSafe's chart footnote reportedly reads "Our number is not empirical. Schema matching is guaranteed, thus we can confidently add 0% into the plots."
- "Mathematically cannot hallucinate or produce type errors" (blog via snippets).
- Non-autoregressive "parallel sampler", single-pass architecture; "new model architecture" (blog via snippets). No architecture disclosed; org forks of LLaDA and vLLM are commit-identical to upstream (https://github.com/ML-GSAI/LLaDA/compare/main...typesafe-ai:LLaDA:main).
- Trained "exclusively on synthetic data" (Almeida to TechCrunch, snippet only).
- Cookbook: batching 13 questions is "12.2× cheaper and 10.0× faster with no change in answers" (docs snippet).
- 64k/32k token limits and 255-option cap (only ever restated from docs).
- 250k tokens/s and 1,200 req/min rate limits.
- "Does not train or fine-tune on customer inputs"; ZDR enterprise-only; DPA retains data "for as long as necessary" (legal pages via snippets).
- ~140,000 waitlist signups in 36 hours (huggingnews snippet).
- Vercel: "~13% of AI Gateway teams in 24 hours" and "up to 18× faster at p95 than GPT Luna, and more accurate" (partner telemetry, unverifiable).
- $40M seed led by DCVC; Almeida "co-inventor of InstructGPT, RLHF, ChatGPT, and GPT-4" (TypeSafe landing page). Checkable fact: InstructGPT paper co-authorship; "co-inventor" is vendor framing.
- "Semantic linter" for question/answer-type mismatch being tested (runtimewire snippet; not in any SDK).

---

## 5. Contradicted or misleading claims

| Claim | What independent evidence shows |
|---|---|
| Two orders of magnitude faster than LLMs | 2.9× vs Haiku 4.5 wall-clock (~9× service time), 2× vs Cohere Rerank Pro, 6.5× vs Opus 5, ~1.2× vs Qwen-27B-on-Cerebras (176 vs 215 ms), **parity** with GPT-OSS-120B Nitro (283 vs 293 ms), and **slower** than local GLiNER (~44 ms) and Laya/Von (46–55 ms). 100×+ appears only vs unconstrained free-text or heavy-reasoning models. (anisselbd; anessbelbati; ghubnab99; iammrduncan; benjamin-brady gist; AbdelStark/jev-benchmarks; jabr/classifier-benchmark) |
| Two orders of magnitude cheaper | 12–323× vs frontier models at list price, but only 1.4× vs mistral-small-3.2-24b and 1.7× vs gemini-2.5-flash-lite per decision; on one single-question fixture Mistral was cheaper than Jev (jev-measured). |
| "Calibrated" as a model property | Corpus- and primitive-dependent. In-distribution ECE 0.02–0.03; Banking77 0.094–0.157; phishing 0.154 (worse than Haiku's 0.097); ESCI 0.242; Web of Science 0.322; unseen rule task 0.107 (4.4× floor), 44.7% accuracy at mean stated probability 0.74; 800-item gradient 2.1–2.5× noise floor at every tier. Sign flips by primitive on identical inputs (Choice/Score refit T 3.29–3.40 overconfident, Noul T 0.66 underconfident). (scienthoon; ASSAY-001; Janus; anisselbd; yodablocks; SamuelSacco) |
| "Never wrong at confidence 1.000" (themsquared, n=60) | Wrong at 1.00: 6 of 102 CLINC items (ickma2311); 129 WoS rows at 1.00 only 76.7% accurate (Janus); 11/191 and 14/187 wrong at p=1.00 (Running-Dolphins); one OpenBookQA item with 1.00 on a wrong answer (scienthoon). At n=60 a perfect model scores ECE ≈0.045, so that study cannot measure calibration. |
| "Cannot hallucinate" | Definitional (schema-level). Confident wrong valid answers are routine: cake recipe → technical issue at 0.94, random letters at 0.97 (priorbench); 37.4% wrong on phishing verdicts; 16% of DAIR Emotion items with probability 0 on the true label. Constrained decoding gives any LLM the same guarantee: with `response_format: json_schema, strict: true` all chat models were 5/5 valid on every fixture (jev-measured). |
| Vendor eval "accuracy" 67.8% | Measures agreement with two other models' averaged outputs, not correctness; and shows Jev *behind* the best comparators by ~6 points. |
| Docs: 422 on validation; 401 on auth | Live: 400 for semantic errors, 422 for schema errors; 403 for missing key. (skills#1, #8; sdk-js#6) |
| Score requires ≥2 levels | 1 level accepted with confidence 1.0 (skills#6). |
| "Near-deterministic" / "100% deterministic" (community) | 50 byte-identical requests → 15 distinct answer sets (jujumilk3); 2.2% label flips between identical passes (anisselbd); near-tie items flip 9/10 vs 1/10 (geekylax gist). Argmax stable on clear items only. |
| "Score is weak at numeric calibration; dates read as text" (vendor jaggedness) | priorbench: number comparison and date ordering 99.6% across 13 designs — 18 of 21 falsified pre-registered predictions were in the direction of predicting failure that did not occur. Vendor understates the model here (though RINNECODER found arithmetic degrades with answer position: 95/108 first vs 62/108 last). |
| "Rate limits 250k tok/s, 1,200 rpm" vs "no published rate limits" | Sources conflict (Anil-matcha, jenaiho vs SamuelSacco ledger). Unresolved. |
| Open-clone "beats Jev" numbers (Laya +3.9 pts; openJev-verdict 77.1% vs 72.7%; SemIf 0.845 vs 0.883) | Laya's win is a checkpoint fine-tuned on the benchmark's own training split; openJev-verdict's checkpoint is not downloadable and JevBench scores it Intelligence 58.1 vs Jev 90.4; SemIf's Jev figure is read from TypeSafe records, not a live run. None are independent zero-shot comparisons. |
| Directory claims "sub-100 ms" / "50–100 ms" (logicrw) | Below even the vendor's floor and every measurement. |
| "No reproducible independent benchmarks" (digest, 2026-09-20) | At least nine pre-registered or raw-data-committed benchmarks existed by that date. |
| Cookbook `uid` cache-busting "reveals" variance | It adds variance (25 distinct sets vs 15) (jujumilk3). |

---

## 6. Hard limitations for evaluating predicates over long legal / financial / policy documents

**Input size.** ~32k tokens for state + longest question, 64k per request [VENDOR]; oversized input is rejected with 400 and still billed [INDEPENDENT]. JSON tokenizes at ~3 chars/token vs ~3.6 for prose, so budgets estimated on prose overshoot (https://github.com/octalide/sift/issues/10). Spanish needs 17–38% more tokens (https://github.com/marcosmartinez/jev-acento). A 600-page document therefore requires caller-side windowing (4 overlapping windows in one PR, never tested against the limit: https://github.com/kdaisho/pdfwasm/pull/37). **No independent test of Jev on a 100-page contract exists.** Well below the cap, discrimination already degrades: 40 rows in a ~12,600-token state drifted probabilities by 0.42 for slots 24–39 and pushed 159/360 rows into the 0.3–0.7 band (yodablocks); conflicting records buried in the middle of 7,558–14,726-token states were found 1/6 and 0/6 times (https://github.com/RINNECODER/jev-behavior-study, 6 calls per cell). Vendor's own jaggedness page: "accuracy decreases when state contains fields the question does not need" — the fix is "on your side".

**No explanations or evidence spans.** The response carries only label/probability/confidence (SDK types). Docs' citation-check pattern is to have code locate the passage. For audit trails, a generative model is still required; a Home Assistant integration's own disclaimer: "A probability with no explanation should not hold a lock" (https://github.com/AboveColin/HA-Jev). Answers are also literal: "jev-1.13 answers the question you wrote, not the one you meant" [VENDOR]; paraphrasing a question moved answers by 0.164 mean / 0.52 at p95 on a hard task (yodablocks) and flipped 12.5% of answers in a pre-registered study (https://github.com/vcjdeboer/jev-reliability); a criteria label "touches credentials" made read-only inspection escalate at 0.88 (skills#5).

**Confidence semantics.** Confidence is a concentration statistic of the returned distribution, not epistemic uncertainty, not P(correct) [VENDOR + INDEPENDENT]. The formula is unpublished and reportedly drifts across versions; read as P(correct) it had ECE 0.035–0.18 and was "never better than the max probability" (scienthoon). It saturates: 47.6% of Banking77 answers at exactly 1.00 (Janus); 40/60 at 1.000 (themsquared). Thresholds do not transfer across datasets (optimal 0.67 → 0.37 between Banking77 and Web of Science; "DO NOT ROUTE" verdict on the latter, Janus), across primitives (Noul vs two-option Choice differ by 0.125 mean; complements sum 0.71–1.42; a Noul 0.22 ≠ Choice 0.99 on the vendor's own page), across languages (Spanish ECE doubles, 0.057→0.101), or across versions. Confidence on a high-consequence error can be high: "revoke production admin access" labelled reversible at 0.93 (ghubnab99). Fewer than ~100 labelled rows per question cannot fit a threshold (https://github.com/abhixhek/jevcal).

**No abstain primitive.** Jev always returns one of the supplied options. Without an explicit "none/unknown" option: 0/30 out-of-scope inputs flagged (priorbench); on unanswerable items accuracy 0.950 → 0.000, stereotype rate 0.79 at 0.79 confidence (jujumilk3); rule-dependent labels absent from the text answered at 0.74 mean probability (scienthoon). With an explicit option it abstains well on genuinely unanswerable items (95%) and lowers probability on CLINC out-of-scope (median 0.54 vs 1.00) — but 15% still ≥0.9 (https://github.com/Running-Dolphins/jev-bench), it chose "unknown" 0/6 times for missing-link inference chains at every length (RINNECODER), and an UNCERTAIN option went unused in 265 calls (https://github.com/Nyarlathoteppppp/pi-jev-context). The vendor's guidance is to add a no-match option and a separate "presence" question; a presence question "catches what confidence cannot" (vcjdeboer). It also answers from priors: with the question removed it scores 0.38–0.46 vs ~0.15 chance (jujumilk3) — a document-grounded predicate may be answered from world knowledge rather than the document.

**Determinism.** Not deterministic: 50 identical requests → 15 distinct answer sets (SD 0.001–0.015); 2.2% label flips on re-run; borderline Noul 0.38–0.52 across 20 calls flipping a 0.5 cutoff 6 times. Argmax is stable on clear items (0 flips in 400). Reproducible audits require pinning, logging the returned `model` field, and tolerance bands.

**Versioning.** Aliases move without notice; no model changelog; no deprecation policy beyond a second-hand "no fixed forced-retirement window"; gateways hide (Vercel) or rename (OpenRouter `jev-1.13-20260917`) the version; `jev-preview` is currently the same model, so no preview exists to test against. Thresholds tuned on 1.13.0 have no documented survival guarantee.

**Other relevant weaknesses.** Vendor-admitted susceptibility to adversarial text in state ("does not treat it as hostile by default"; a `// satisfies REQ-AUTH-02` comment can skew results — https://github.com/nozomi-koborinai/jev-spec/pull/13); counting unreliable (letter counting 117/216); multi-hop reasoning absent (missing-link chains 0/6; nested-identity phishing missed); non-English accuracy −6.4 to −11 points with ECE roughly doubling (Spanish, Russian); hosted-only, US-only, no SLA, ZDR enterprise-only; official SDK default timeout 10 s; a customer-agreement clause reportedly restricting publication of performance numbers (jevcal README, unverified).

---

## 7. Science / novelty and commoditization outlook

**What is public.** Four interface statements (single non-autoregressive pass; independent questions over shared state; option scoring for Choice ≤255 / Score 2–10 / Noul; O(K) float outputs), the name RLCD, "trained for calibrated decisions", and a synthetic-data quote. No paper, preprint, model card, parameter count, reward function, calibration curve, or weights. An arXiv search for the exact phrase "reinforcement learning for calibrated decisions" returned zero results (systemonemodels.org, blocked; corroborated by every field guide). Second-hand: the CEO on HN "confirms the zero-shot classifier reading and the encoder-with-heads shape" (https://github.com/OmniJev/awesome-jev; thread unreachable).

**Prior art for every component** (catalogued at https://github.com/OmniJev/awesome-jev; contents not re-read, arXiv blocked): entailment zero-shot classification (Yin et al. 2019, arXiv 1909.00161), monoBERT cross-encoders (1901.04085), GLiNER/GLiClass (2311.08526, 2508.07662), Llama Guard single-token verdicts (2312.06674), the InstructGPT reward model (2203.02155, co-authored by Almeida), non-autoregressive decoding (1711.02281, 1904.09324), constrained decoding (Outlines 2307.09702; OpenAI Structured Outputs), and proper-scoring-rule RL for calibration: RLCR (Damani et al., arXiv 2507.16806, ICLR 2026, Brier reward on RLVR), "Rewarding Doubt" (2503.02623), calibration-aware RL for decision tokens (2601.13284), temperature scaling (Guo et al. 2017). A toy reconstruction (https://github.com/Maverick-Ansh/jev-from-scratch, 6.6M params) shows plain cross-entropy already yields calibration within 0.003 of perfect, so RLCD's plausible role is preventing the confidence collapse that accuracy-reward RL causes (0.725 → 0.918 mean confidence at flat accuracy), not creating calibration; VladUZH/jev-calibration shows pretrained Qwen2.5 base option-logits already reach ECE 0.03–0.04 while instruct tuning raises it to ~0.27. Jev's 0.01-quantized outputs with hard zeros (log-loss undefined) are atypical of a strictly-proper-scoring-rule-trained model.

**What is plausibly novel** is productization and training investment: a frontier-quality zero-shot discriminative model with parallel heads, free output tokens, and (unverifiable) large-scale synthetic RL. Where it shows: beats clean NLI zero-shot on all 7 sets; 96.5% vs 58–70% for sub-500M open encoders on a 947-case suite with only −1.0 pt under distribution shift vs −25.7 for Von (https://github.com/jabr/classifier-benchmark, LLM-labelled); JevBench hard tier 74.1% vs 69.5% (djev), 65.5% (decider-35B), 59.5% (SemIf). Where it does not: frontier LLMs beat it on intelligence and calibration (GPT-5.6 Luna low 96.8/89.8, DeepSeek V4.1 Flash 96.1/96.7 vs 90.4/82.7; Luna 0.964 vs 0.730 on public hard items); a few hundred labels + logistic regression beat it on accuracy on every dataset tested (elcronos; ickma2311: bge-small+LR 0.933 vs 0.832); a 4B LoRA trained 18 min on 1,000 emails reached 97.4%/ECE 0.010 vs Jev 62.6%/0.154 (anisselbd issue #1).

**Who else can do this, now.** (a) Any frontier API with logprobs + JSON schema (OpenAI, Google) or structured outputs + verbalized confidence (Anthropic — no logprobs); TypeSafe's own MIT adapter runs the Jev interface over OpenAI/Anthropic (https://github.com/typesafe-ai/system-one-adapter-python). (b) Wire-compatible open servers within 48 hours to one week: SemIf (untrained Qwen3.5-4B logit readout, 3,045★), kev (Qwen3.5 LoRA, 9B within 3.5 pts on its dev set), NanoJev, decider, jev-local, Laya, Von, Luce, reflex, LitJev, Winnow — ~28 implementations per OmniJev, 5,108 "jev" repos created in six days. (c) Hosted rivals: Maisa djev (Apache-2.0 runtime over DiffusionGemma-26B, $0.035/M announced, free preview, 0.24 s, JevBench 74.3, "uncalibrated" per its docs) and milliseconds.ai decision-machine-1 ($0.04/M, 0.17 s, Intelligence 74.5). (d) Distribution: OpenRouter alpha Decisions API, Vercel AI SDK "evaluation model" type, Cloudflare Workers AI, classifier.dev resale, LangChain and Pydantic AI integrations — all within one week. No first-party OpenAI/Google/Anthropic "decision model" was found.

**Outlook.** The interface is commoditized today. The operating point (~200–300 ms, ~$0.02–0.04 per 1k decisions, near-Jev composite) is reproducible on a single GPU with 4–35B open models and is offered hosted at equal or lower announced prices. The remaining, real gap is zero-shot breadth and hard-tier accuracy (~5–15 points over open models on JevBench's hard tier), which reflects backbone scale and training data, not a disclosed mechanism. Given that, and that cheap chat models are within 1.4–1.7× on cost and ~3× on latency when properly constrained, the evidence supports: typed/calibrated decision endpoints become a standard SKU at gateways and at least one hyperscaler within roughly 3–9 months (Q1–Q2 2027); open models close the routine-classification gap in the same window; TypeSafe's durable edge, if any, is its private training recipe on hard/multi-hop items and whatever calibration it actually has — which independent tests show is narrower and less robust than the launch narrative. This timeline is an inference from the above evidence, not a sourced fact.

---

## 8. Open questions only a hands-on test can resolve

1. **Long-document behaviour near the cap.** No test exists on a 100+-page contract or filing. Does discrimination collapse toward 0.5 for predicates whose evidence sits deep in a 25–32k-token state (as it did at ~12.6k tokens in a 40-row batch), and does chunk-then-aggregate (max/any over windows) preserve precision on negative predicates?
2. **Predicates whose truth is unknowable from the document.** With an explicit "not determinable from text" option, what fraction of genuinely absent facts does Jev abstain on for legal/financial language (KoBBQ 95%, logic chains 0/6 — which regime applies)? Does it answer from priors (state-blind control) on well-known statutes or public filings?
3. **Per-predicate calibration and threshold fitting.** On ≥100–300 labelled documents per predicate: what is ECE at the noise floor, in which direction is it miscalibrated per primitive (Noul vs Choice), and what threshold achieves a target precision at what coverage? Do Noul and two-option Choice framings of the same predicate disagree by >0.1 on your text?
4. **Determinism for audit.** Across 20–50 identical runs on your documents, what is the argmax flip rate and probability SD? Is a tolerance band (e.g. 0.40–0.60 = review) sufficient?
5. **Question-wording sensitivity.** Do 3–5 paraphrases of each predicate move probabilities by >0.15 (yodablocks: 0.164 mean on hard tasks)? Does negation phrasing hold (complements sum ≈1)?
6. **Adversarial content in documents.** Does self-describing language in a clause ("this provision complies with §X") or injected instructions in a scanned document move the answer? The vendor says yes; no red-team numbers exist.
7. **Numeric, date and cross-reference predicates.** Vendor says unreliable; priorbench says 99.6%. Which holds for settlement windows, accrual periods, defined-term indirection, and quarter boundaries in real filings?
8. **Batching many predicates over one state.** Independence held for 16 questions on short states; does it hold for 50+ predicates over a 30k-token state, and does the position effect seen for batched *items* also appear for batched *questions*?
9. **Versioning in practice.** Does pinning `jev-1.13.0` actually hold answers fixed over weeks, and does a preview build ever diverge from latest? Are thresholds stable after a version bump?
10. **Rate limits, throughput and billing.** Real sustained req/s on a paid key (11 req/s saturation and 30 rpm on free tiers reported); whether rejected oversized requests are billed at full size; whether the dashboard reconciles with list price (one tester could not reconcile $0.68 vs $0.0016).
11. **Tokenization of your inputs.** Effective tokens/char for JSON-structured vs prose document state, and non-English (Spanish +17–38%).
12. **ZDR and data handling on the direct API.** Whether any retention control exists outside the enterprise tier or Vercel's gateway flag.
13. **Head-to-head at your operating point.** Same predicates on Haiku 4.5 / Gemini Flash-Lite with strict JSON schema and logprobs (or verbalized probability), with prompt caching and batch discounts: independent data suggests the cost gap may be 1.4–7× and the latency gap ~3×, not 100×, and accuracy/calibration may favour the LLM.
14. **Whether the 255-option cap, 64k limit, and question-count limit** bind for your predicate sets (only 256+ options has an independent rejection report).
15. **Confidence-field stability**: is (k·max_p − 1)/(k − 1) actually the implemented statistic on your questions, and does it remain so across versions?