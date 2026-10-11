# sophon store: how to use it (arm B only)

A tiny provenance store for links between governing article versions and executable rules.
It records only what it can verify, refuses evidence it cannot find, and revalidates every link
against a new law snapshot or a new rule snapshot without any model call. It does **not**
interpret law or propose links: you do, it checks and records.

All commands: `python3 src/sophon.py --store work/sophon/store <command> ...`. Every command
prints one JSON line (the `asof` command prints a JSON document). Exit status 0 means the command
ran, not that anything is aligned.

## 1. Register snapshots (once per snapshot, idempotent)

```sh
python3 src/sophon.py --store work/sophon/store snapshot-law   --id S0 --articles inputs/law/S0_legi-data-2.360.0/articles.json
python3 src/sophon.py --store work/sophon/store snapshot-rules --id G0 --rules-dir "inputs/rules/G0_d9242882f96b/modele-social/règles" --meta inputs/rules/G0_d9242882f96b/meta.json
```

`snapshot-law` stores every bounded article with its LEGIARTI version id, legal dates, text and
text hash. `snapshot-rules` hashes every rule file, indexes top-level rules with their
`références`, and runs the real engine build (parsed rule count) as the native syntax check.

## 2. Record a link

```sh
python3 src/sophon.py --store work/sophon/store link add \
  --rule "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux service BNC" --rules-snapshot G0 \
  --article D613-4 --law-snapshot S0 \
  --quote "10 000 euros 34 % 6 600 euros 21,1 %" \
  --claim "category e) BNC: global rate 21,1 %" \
  --check-rule "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux service BNC" \
  --check-situation '{"date":"01/05/2024","salarié":"non","entreprise . catégorie juridique":"'"'"'EI'"'"'","entreprise . catégorie juridique . EI . auto-entrepreneur":"oui","dirigeant . auto-entrepreneur":"oui","entreprise . activité . nature":"'"'"'libérale'"'"'","dirigeant . auto-entrepreneur . chiffre d'"'"'affaires":"1000 €/mois"}' \
  --expect 21.1
```

Rules of the store:
- `--quote` must be an exact substring of the article text in that law snapshot, else the link is
  REJECTED and nothing is written.
- `--rule` must be a parsed rule of that rules snapshot.
- A link is **VERIFIED** only when it carries an executable check (`--check-rule`,
  `--check-situation`, `--expect`) and the check passes right now against the engine. A failing check
  is recorded as **FAILED** (not hidden). Without a check the link can only be `--status INFERRED`
  (textual link, no execution) or `UNKNOWN`.
- Approvals: there is no `--approve`. `--approval-file FILE` records an approval only with the hash
  of an existing evidence file. In this corpus no such file exists; the field reads
  `"none recorded"`. Do not invent one.
- Records are append-only and hash-chained (`links.jsonl`).

## 3. Revalidate after a change on either side

```sh
python3 src/sophon.py --store work/sophon/store snapshot-law   --id S8 --articles inputs/law/S8_legi-data-2.489.0/articles.json
python3 src/sophon.py --store work/sophon/store snapshot-rules --id G3 --rules-dir "inputs/rules/G3_d6c374271727/modele-social/règles" --meta inputs/rules/G3_d6c374271727/meta.json
python3 src/sophon.py --store work/sophon/store revalidate --law-snapshot S8 --rules-snapshot G3 --out work/sophon/reports/M1
```

For every link it compares the article version id and text hash (LAW_SAME / LAW_CHANGED /
LAW_TEXT_CHANGED), the rule body and file hashes (RULE_SAME / RULE_CHANGED / ...), and re-runs the
stored check (CHECK_PASS / CHECK_FAIL / NO_CHECK). Statuses: STILL_VERIFIED, REASSESS_LAW_CHANGED,
REASSESS_RULE_CHANGED, RULE_CHANGED_CHECK_STILL_PASSES, BROKEN, UNVERIFIED_NO_CHECK. The report also
lists `rules_to_reassess`, `articles_changed` and `articles_without_any_link` (changes you have no
link for are **not** detected by revalidation: that list is your reminder).

## 4. Reports

```sh
python3 src/sophon.py --store work/sophon/store report --out work/sophon/reports/evidence
python3 src/sophon.py --store work/sophon/store asof --date 2026-01-01 --article D613-4 --out work/sophon/reports/asof_D613-4_2026-01-01.json
python3 src/sophon.py --store work/sophon/store verify-store
```

`report` writes the evidence table (every link with hashes, check and approval status).
`asof` reconstructs, for a date, which article versions were in force in which snapshots, the
links recorded, their checks and the (absent) approvals, with the store's limits stated.
`verify-store` re-checks the hash chain, the quotes against the stored snapshots, and whether rule
files on disk still match their snapshot.

## 5. Evaluating rules directly (both arms have this)

```sh
node src/publicodes_eval.mjs build    --rules "inputs/rules/G0_d9242882f96b/modele-social/règles"
node src/publicodes_eval.mjs list     --rules "..." --prefix "dirigeant . auto-entrepreneur"
node src/publicodes_eval.mjs evaluate --rules "..." --situation '{"date":"01/07/2024", ...}' --rule "a . b" --rule "c . d"
```

A hash proves content is unchanged. It does not prove the content is correct, complete or authorised.
