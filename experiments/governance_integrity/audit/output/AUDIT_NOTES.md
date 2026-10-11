# T4 as-of adversarial audit — method and commands

Auditor working directory: `/tmp/claude-0/-home-user-sophon/980382c3-789d-515f-926e-c8bdd3dd6b4b/scratchpad/runs/audit` (all paths below are relative to it). No network, no git. All Python run with `python3 -I`. Tool calls used: 50 in total (46 investigation, 2 writes, 1 validation, 1 hand-back). Scratch files written by me are in `scratch/` (B's as-of re-run for 2026-01-01 and the extracted L0301 check).

## Rules I applied
- A hash is VERIFIED only if I recomputed it from the sealed file (sha256sum / hashlib) and it matched the arm's record.
- A check is VERIFIED only if I re-ran it with `node src/publicodes_eval.mjs evaluate` on the sealed pin (and on the arm's proposal tree) and got the recorded value.
- A quote is VERIFIED only if I found it as an exact substring of the sealed text (or nota) of the exact article version named.
- Statements of the form "approval: none recorded" are marked ABSENT (the record is absent; the statement is correct), after grepping the sealed inputs and the arms' work for any approval artefact.
- Citation-shaped text (URLs, decree numbers, commit ids) counts as "cited only" unless the cited content itself is preserved and checkable.

## 1. Orientation (calls 1–12)
- Read `PROMPT.md`; `find` over the tree (2126 files; arm B's `work/proposals/*` and arm A's `work/proposals/*` are full rule-tree copies); read `arms/*/WORK_SOURCE.txt`, `src/USAGE.md`, both `work/README.md`, `wc -c` of notes/answers/stores.
- `ls inputs/law/S9_*/` — each snapshot is a single `articles.json` with keys `snapshot, legi_data_version, code, published, tarball_sha256, integrity, articles_missing_in_snapshot, articles`; each article maps to a list of records with `id, etat, dateDebut, dateFin, text, text_sha256, nota, articleVersions, lienModifications`.
- `head -c` of every `inputs/rules/G*/meta.json` and `HISTORY.txt`.

## 2. Sealed ground truth (calls 13, 20, 42, 47)
```
python3 -I  # over inputs/law/S*/articles.json: for D131-6-1 print published, id, etat, dateDebut, dateFin,
            # text_sha256 and hashlib.sha256(text).hexdigest(), articleVersions, lienModifications, nota
```
Result: S0–S8 → LEGIARTI000036475110 (VIGUEUR 2018-01-01, sha af896c57…4707, recomputed equal). S9 (published 2026-03-31T16:18:17.431Z) and S10 → LEGIARTI000053451315 v8.0, VIGUEUR, dateDebut 1767225600000 = 2026-01-01, sha 59f4edcf…ebf5 (recomputed equal), lien Décret n°2026-69 du 6 février 2026 art. 1 (publi 2026-02-08, signé 2026-02-06), nota "entrent en vigueur le 1 er janvier 2026 et s'appliquent aux créations et reprises d'entreprise intervenant à compter de cette date". S8 (published 2026-01-01T15:46:43.781Z) has no successor version listed.
```
python3 -I  # D613-4 in S7/S8/S9 and D756-5 in S0/S5/S9: id, etat, dates, recomputed sha, lien, nota, '25,6' context, full D756-5 text
```
Result: D613-4 S8/S9 = LEGIARTI000052218738 VIGUEUR 2026-01-01, Décret 2025-943 (publi 2025-09-09), sha f86c045c… equal, row e "23 609 euros 34 % 15 582 euros 25,6 %"; S7 = …097 ABROGE_DIFF with …738 VIGUEUR_DIFF (no text). D756-5 = LEGIARTI000034726710 (2017-05-12, Décret 2017-972), sha 74b05fcc…9638 equal in S0/S5/S9, full text read (1/6 or 1/3, 1/2, 2/3, "arrondi au dixième de pour cent supérieur", cites D. 131-6-1 / L. 133-6-8; II CA cap).
```
python3 -I  # grep needles '26,1 %','4,4 %','13,1 %','17,4 %','4,3 %','12,8 %','17,1 %','25,6 %' over all sealed texts+notas
```
Result: only '25,6 %' found (D613-4 LEGIARTI000052218738 in S8/S9/S10). 'taux global' occurs only in L613-7 and D613-4.
```
grep -E '^(88cb2ce9|55470937|ea8f00f0|bdfbd61c)' inputs/rules/G4_a61b72947fec/HISTORY.txt
grep -n -E '25\.6|26\.1' inputs/rules/G4_a61b72947fec/history_bounded_rules.patch
grep -ril -E 'approv|sign-off|signoff|ratif' inputs/rules/*/meta.json inputs/rules/*/HISTORY.txt inputs/law ; grep -ic approv …/history_bounded_rules.patch
```
Result: 88cb2ce9660ba41bbc91ae6676a6ef96bb0281af 2026-01-08 12:12:20 +0100 Alice Dahan "chore(auto-entrepreneur): mise à jour des taux de cotisation et de répartition"; patch l.267–268 `-alors: 26.1%` / `+alors: 25.6%`. The `-l` grep listed HISTORY.txt files but `grep -i approv` on G4 HISTORY.txt printed nothing and the patch count is 0 → no approval record in the sealed inputs.
```
sha256sum "inputs/rules/G4_a61b72947fec/modele-social/règles/dirigeant/exonérations.publicodes"   # ef52869dc171882c2a81c9dff4d0290ddb97fac2324960318c9125d765d3f025
sha256sum … dirigeant/auto-entrepreneur/exonérations.publicodes                                   # befe40c7…7932
sha256sum … dirigeant/auto-entrepreneur/cotisations-et-contributions.publicodes                   # 0f7d906a…be7e
sha256sum … dirigeant/exonérations/ACRE.publicodes                                                # b8dc9c1a…fe87
node src/publicodes_eval.mjs build --rules "inputs/rules/G4_a61b72947fec/modele-social/règles"     # 652 raw / 1334 parsed
grep -n -A 14 "^dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux:" … dirigeant/exonérations.publicodes   # line 236: taux progressif 100 % ≤ 75 %, 0 % at 100 %
grep -n -E 'DROM|référence|http|…' … dirigeant/auto-entrepreneur/exonérations.publicodes          # DROM taux service BNC 4.4/13.1/17.4 %, références = URSSAF URLs
```

## 3. Engine re-runs (calls 34, 41)
```
TI='{"date":"01/06/2026","salarié":"non","dirigeant . régime social":"'indépendant'","entreprise . catégorie juridique":"'EI'","entreprise . catégorie juridique . EI . auto-entrepreneur":"non","entreprise . imposition":"'IR'","entreprise . activité . nature":"'commerciale'","établissement . commune . département . outre-mer":"non","entreprise . date de création":"01/01/2026","entreprise . durée d'activité . en début d'année":"0 an","dirigeant . exonérations . ACRE":"oui","dirigeant . indépendant . revenu professionnel":"20000 €/an"}'
node src/publicodes_eval.mjs evaluate --rules <T> --situation "$TI" --rule "dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux" --rule "… retraite de base" --rule "… cotisations"
```
- sealed G4 → taux 100 %, retraite de base 0 €/an, cotisations 1400 €/an
- arms/A/work/proposals/M2/modele-social/règles → 25 %, 2663, 4333
- arms/B/work/proposals/M2/modele-social/règles → 25 %, 2663, 4333
```
AE='{"date":"01/01/2026", … auto-entrepreneur oui, libérale, réglementée non, CA 1000 €/mois, création 01/01/2021, ACRE non, outre-mer non}'
node src/publicodes_eval.mjs evaluate --rules <G3|G4> --situation "$AE" --rule "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . service BNC . taux"
```
- sealed G3 d6c374271727 → 26.1 % ; sealed G4 a61b72947fec → 25.6 % (the name `… cotisations . taux service BNC` no longer exists at G3/G4; the valued rule is `… service BNC . taux`).
```
# arm B's stored check L0301 (extracted to scratch/L0301_check.json): situation date 01/07/2026, création 01/01/2026, revenu 20000 €/an, no 'régime social' key
node src/publicodes_eval.mjs evaluate --rules <G4|B proposal> --situation "$SIT" --rule "… exonérations . ACRE . taux"
```
- sealed G4 → 100 % (L0301 FAILED reproduced) ; B proposal → 25 % (L0329 VERIFIED reproduced)

## 4. Arm A artifacts (calls 14, 15, 18, 23, 24, 27, 35, 36, 37, 43, 46)
- Read in full: `arms/A/work/notes/M2_findings.md`, `M1_findings.md`, `R3_findings.md`, `arms/A/outputs/M2/NOTES.md`; structure and selected entries of `arms/A/outputs/M2/answer.json` (keys, changed_articles[0], approval, abstentions, rules[] entry for `… ACRE . taux`, evaluations for that rule, build), `arms/A/outputs/M1/answer.json` (approval, rules_pin, law_snapshots, changed_articles), `arms/A/outputs/R3/answer.json` (keys, evidence kinds, approval, expected_values_if_mismatch).
- `head -c` of `arms/A/work/engine/checks_M2_ti.json`, `results_M2_G4_ti.jsonl`, `results_M2_proposal_ti.jsonl`, `run_checks.sh`.
- Quote verification (python): every string of the form `<art> <LEGIARTI> (etat …)[ [nota]]: "…"` in rules[].evidence, evaluations[].law_basis and abstentions[].reason of A's M2 answer tested as exact substring of the sealed S8/S9 text or nota of that version → 462 found / 0 missing. R3 `article_quote` entries (8) → all found (one D613-4 quote lives in the sealed nota, confirmed).
- `grep -o https?://…` over A's R3/M2 NOTES and answer.json → no URLs; URLs appear only in `arms/A/work/proposals/M2/…/auto-entrepreneur/exonérations.publicodes` (upstream URSSAF links + two legifrance links A added). `sha256` occurrences in A's M2 answer = 49, all article text hashes in `unchanged_articles`; none in R3 answer; `arms/A/work/law/S*_index.json` has ids/dates/versions/liens but no text hash.
- Verbatim text check: sealed S9 texts of D756-5 and D131-6-1 are exact substrings of `arms/A/work/law/S9_texts.md`; sealed S5 D756-5 text is in `S5_texts.md`.
- A's recorded engine values: `results_M1_G3_ae.jsonl` BNC@01-01-2026 = 26.1 %, `results_M1_proposal_ae.jsonl` = 25.6 %, `results_M2_G4_ae.jsonl` = 25.6 % — matched by my re-runs.
- Mentions of the commit author: 0 in A's answer.json files (M1, M2); commit 88cb2ce9 named in A's M2 NOTES and notes only.

## 5. Arm B artifacts (calls 16, 17, 19, 21, 22, 25, 26, 28, 30, 31, 32, 33, 38, 40, 44, 45)
- Read in full: `arms/B/outputs/M2/NOTES.md` (identical to `work/notes/M2_NOTES.md` by `cmp`); report file list; `M2_asof_D131-6-1_2026-03-31.json` (links summary + article_versions_known + rules_snapshots_known + approvals + limits); `M2_verify_store.json`, `M2_report_cmd.json`, head of `M2_revalidate_S9_G4_cmd.json`; `M1_asof_D613-4_2026-01-01.json` summary; approval fields of B's M1/M2/R3 answer.json; `grep` of B's M1 NOTES §8 and R3 NOTES D756-5 lines.
- `arms/B/work/sophon/store/links.jsonl`: 356 records, keys listed; projections of all links on D131-6-1 (56), on G4/P_M2 with id ≥ L0301, on D613-4 LEGIARTI000052218738 (24), on D756-5/DROM (78).
- `arms/B/work/sophon/store/rules/G4.json`: meta (commit a61b72947fec1e13…, committed 2026-03-03 09:30:36 +0100), engine_build 652/1334, files map (58) — the four file hashes above match my sha256sum exactly; rule `… ACRE . taux` body_sha256 16f80bb3c82f7b10…; nested `DROM . taux service BNC` not indexed (links use `rule_owner`).
- Body hash recomputation: `yaml.safe_load` of the sealed G4 `dirigeant/exonérations.publicodes`, body of `… exonérations . ACRE . taux`, `sha256(json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(',',':')))` (= sophon's `canonical`, read at `src/sophon.py` lines 63–64 and 184–204) → 16f80bb3c82f7b10… match.
- Hash chain: independent re-implementation over all 356 records (`record_hash == sha256(canonical(record minus record_hash))`, `prev_hash == previous record_hash`) → 356 ok / 0 bad.
- Quotes/offsets/sha: for every link on D131-6-1 (55), D613-4 (74), D756-5 (70): the version exists in the recorded sealed snapshot; `article_text_sha256 == sealed text_sha256 == recomputed`; `quote in text` and `text[quote_offset:quote_offset+len(quote)] == quote` → 0 problems. L613-7 DROM links L0010/L0145: quote and sha verified.
```
python3 -I src/sophon.py --store arms/B/work/sophon/store verify-store      # {"ok": true, "problems": [], "links_checked": 356} in 0.7 s
python3 -I src/sophon.py --store arms/B/work/sophon/store asof --date 2026-01-01 --article D131-6-1 --out scratch/B_asof_D131-6-1_2026-01-01.json
```
The regenerated as-of (date 2026-01-01) lists the same 55 links (29 VERIFIED / 11 INFERRED / 8 UNKNOWN / 7 FAILED), S0–S8 → …110, S9/S10 → …315, approvals ['none recorded'], the three limits. Caveat: `G4.json.rules_dirs` is an absolute path under `…/runs/B/R4/inputs/…` (outside this directory), so verify-store's "rule files on disk still match" part cannot have re-read the sealed files here; I did not rely on it.

## 6. Findings in one paragraph each
- **Q1**: Both arms correctly reconstruct D131-6-1 LEGIARTI000053451315 (in force 2026-01-01, applies to créations/reprises from that date; Décret 2026-69; first visible in S9 published 2026-03-31; S8 published 2026-01-01 still showed …110), requiring "le quart" (25 %) of the maladie/maternité/veuvage/vieillesse de base/invalidité-décès/AF contributions when income ≤ 3/4 PSS. The implementing rule `dirigeant . indépendant . cotisations et contributions . exonérations . ACRE . taux` at the sealed pin G4 a61b72947fec still gives 100 % (re-run); both proposals give 25 %. Arm A records only the commit (no rule-file hash) and uses its own status vocabulary (AFFECTED/high + abstentions) but all 462 quote-shaped evidence strings are exact sealed substrings; arm B records file/body/article hashes, exact quotes with offsets, chained records, failing checks on G4 and passing checks on P_M2, all recomputed. Approval: absent in both, correctly stated.
- **Q2**: The primary source is D756-5 LEGIARTI000034726710 (fractions 1/6 or 1/3, 1/2, 2/3 of the D613-4 rates, rounded up to 0,1 %) combined with the D613-4 version in force. Arm B preserves it with hashes, quotes, offsets and checks; arm A preserves verbatim text copies, index entries and exact quotes but no hashes. Both only cite the URSSAF URLs that the upstream rules carry (no content/hash preserved). Neither has — and neither claims — a primary source for G4's 2026 DROM BNC 4,4/13,1/17,4 % (fractions of a 26,1 % that appears in no sealed text); the 1/6-vs-1/3 classification (L611-1), L751-1, the renumbering decree and the D756-5 II cap remain unsourced/unimplemented.
- **Q3**: No approval evidence exists in either arm or in the sealed inputs. What exists: S8 (published 2026-01-01) with D613-4 LEGIARTI000052218738 (Décret 2025-943, row e 25,6 %), upstream commit 88cb2ce9 (2026-01-08, author Alice Dahan in sealed HISTORY.txt — not an approver; neither arm names anyone), G3 → 26,1 % vs G4 → 25,6 % (re-run), and both arms' checks (A: result files; B: links L0217 FAILED on G3, L0259/L0321/L0349 VERIFIED on P_M1/G4/P_M2). Both arms answer "none recorded".
