#!/usr/bin/env python3
"""Build output/answer.json + output/NOTES.md for R2 (and append the R2 section to work/README.md) from the recorded artefacts.
usage: python3 -I work/scripts/gen_answer_R2.py <self_reported_tool_calls>"""
import json, glob, os, sys, re, hashlib
SELF_CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 0
COMMIT = json.load(open('inputs/diffs/R2_1932d654cf7a/meta.json'))
raw = json.load(open('inputs/law/S4_legi-data-2.384.0/articles.json'))['articles']
arts = {k: v[0] for k, v in raw.items()}
VID = {k: arts[k]['id'] for k in arts}
# ---- sophon link results
links = []
for ln in open('work/sophon/link_results_R2.jsonl'):
    rec = json.loads(ln)
    try: j = json.loads(rec['stdout'].splitlines()[-1])
    except Exception: j = {'raw': rec['stdout'][:300]}
    cr = j.get('check_result') or {}
    links.append({'tag': rec['tag'], 'id': j.get('link_id'), 'status': j.get('status'), 'article': rec['article'], 'article_id': rec['article_id'], 'rule': rec['rule'],
                  'rules_snapshot': rec['snap'], 'check_rule': rec['check_rule'], 'date': rec['situation'].get('date'), 'expected': cr.get('expected', rec['expect']),
                  'observed': cr.get('observed'), 'error': (cr.get('error') or None), 'quote': rec['quote']})
def L(tag):
    for l in links:
        if l['tag'] == tag: return l
    return {}
reports = sorted(glob.glob('work/sophon/reports/R2_*'))
# ---- engine artefacts
names_b = json.load(open('work/proposals/R2/list_before.json'))['names']; names_a = json.load(open('work/proposals/R2/list_after.json'))['names']
new_names = sorted(set(names_a) - set(names_b)); gone_names = sorted(set(names_b) - set(names_a))
def load_evals(path):
    d = {}
    for ln in open(path):
        r = json.loads(ln)
        try: ev = json.loads(r['stdout'])['evaluations']
        except Exception: ev = {'__error__': r['stderr'][-300:]}
        d[r['id']] = ev
    return d
EB = {}; EA = {}
for cs in ('cases_R1', 'cases_R2_acre'):
    EB.update(load_evals(f'work/evals/R2_{cs}_before_G1.jsonl')); EA.update(load_evals(f'work/evals/R2_{cs}_after_G1post.jsonl'))
def v(E, cid, rule):
    e = E.get(cid, {}).get(rule, {})
    if 'error' in e: return 'ERROR: ' + e['error'][-140:]
    u = e.get('unit'); n = e.get('nodeValue')
    return (f"{n} {u}" if u else f"{n}") if n is not None else 'null'
# public-rule identity check over every (case, rule) except the taux ACRE probes
diffs = []; n_pairs = 0
for cid in EB:
    if cid.endswith('_TAUXACRE@01/09/2024'): continue
    for rule in EB[cid]:
        n_pairs += 1
        if json.dumps(EB[cid][rule], sort_keys=True) != json.dumps(EA.get(cid, {}).get(rule), sort_keys=True): diffs.append((cid, rule))
tables_identical = (open('work/evals/R2_cases_R1_before_table.txt').read().splitlines()[1:] == open('work/evals/R2_cases_R1_after_table.txt').read().splitlines()[1:])
C = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . "
TA = C + "taux ACRE"
tauxacre_rows = []
for cid in EB:
    if cid.endswith('_TAUXACRE@01/09/2024'):
        tauxacre_rows.append(f"{cid}: BEFORE {v(EB, cid, TA)[:60]}... | AFTER {v(EA, cid, TA)}")
sit_180 = json.load(open('work/evals/cases_R2_acre.json'))
SIT = {c['id']: c['situation'] for c in sit_180}
reval_a = json.load(open('work/sophon/reports/R2_revalidate_S4_G1.json')); reval_b = json.load(open('work/sophon/reports/R2_revalidate_S4_G1post_R2.json'))
ra = {r['link_id']: {k: x for k, x in r.items() if k != 'rules_snapshot'} for r in reval_a['rows']}; rb = {r['link_id']: {k: x for k, x in r.items() if k != 'rules_snapshot'} for r in reval_b['rows']}
reval_identical = (json.dumps(ra, sort_keys=True) == json.dumps(rb, sort_keys=True))
verify = json.load(open('work/sophon/reports/R2_verify-store.json')) if os.path.exists('work/sophon/reports/R2_verify-store.json') else {}
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
F_B = "inputs/rules/G1_2a0e452617fc/modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes"; F_A = "work/proposals/R2/after/modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes"
law_same = open('work/law/S3_dump.txt').read().splitlines()[1:] == open('work/law/S4_dump.txt').read().splitlines()[1:]
q_l6137 = L('R2-G1post_R2-L613-7-tauxACRE').get('quote'); q_12m = L('R2-G1post_R2-D131-6-1-dans-les-12-mois').get('quote'); q_bnc = L('R2-G1post_R2-D613-4-BNC').get('quote'); q_cipav = L('R2-G1post_R2-D613-4-CIPAV').get('quote'); q_bic = L('R2-G1post_R2-D613-4-BIC').get('quote')
ls = lambda t: f"{L(t).get('id')}:{L(t).get('status')}"
A180 = 'AE_BNC_ACRE_cre2024_180j@01/09/2024'; A500 = 'AE_BNC_ACRE_cre2023_500j@01/09/2024'; N180 = 'AE_BNC_noACRE_cre2024_180j@01/09/2024'
answer = {
 "task": "R2",
 "commit": COMMIT['commit'],
 "label": "HARMLESS_REFACTOR",
 "confidence": "high",
 "rationale": (f"Commit {COMMIT['commit'][:12]} ('{COMMIT['subject']}', {COMMIT['committed']}) deletes exactly one line in one file of the rule library: the attribute "
   "`privé: oui` of the rule `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE` (modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes). "
   "`privé` is a publicodes visibility attribute (whether a rule may be referenced/evaluated/set from outside its namespace and shown in the documentation); it is not part of any formula, unit, "
   "default, threshold or applicability. Engine proof on a disposable AFTER tree (copy of G1 + the forward patch): build 641 raw rules on both sides; every value of every public rule is identical "
   f"before and after ({n_pairs} (situation, rule) pairs over 31 situations covering AE BNC/BIC/vente/CIPAV with and without ACRE at 01/09/2024, DROM, indépendant and salarié cases; {len(diffs)} differences); "
   "the only observable change is exposure: the parsed-rule list grows from 1220 to 1227 names (`taux ACRE` and its six `avec` children become listed) and `taux ACRE` becomes evaluable "
   "(BEFORE: engine error \"n'est pas accessible\"; AFTER: 50 % for an AE created 01/03/2024 at 180 days with ACRE, null otherwise) with the same internal value it already contributed to the public rates "
   "(BNC 10.6 % / 106 €/mois with ACRE on both sides). sophon revalidate S4/G1 and S4/G1post_R2 give identical per-link results for all 113 pre-existing links. "
   "Law snapshot S4 (legi-data 2.384.0) is identical to S3 for all 12 bounded articles (same version ids and texts), so nothing on the law side changed either. "
   "This is documentation/metadata only: HARMLESS_REFACTOR. The 50 % ACRE value now exposed rests on a decree article outside the bounded set (L613-7 I only delegates it: 'fixé par décret') and the "
   f"pre-existing misalignment of the AE rates with D613-4 v.{VID['D613-4']} (23,1 % BNC / 23,2 % CIPAV in force since 2024-07-01; library 21,1 / 21,2) exists identically on both sides; "
   "both are reported below, not as the label of this change."),
 "evidence": [
  {"kind": "diff_excerpt", "article": None, "article_version_id": None,
   "quote_or_values": ("inputs/diffs/R2_1932d654cf7a/diff.patch: 1 file changed, 1 deletion(-): modele-social/règles/dirigeant/auto-entrepreneur/exonérations.publicodes @@ -62,7 +62,6 @@ "
     "under `dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE:` the line `-  privé: oui` is removed; the rule keeps `applicable si: dirigeant . exonérations . ACRE`, "
     "`unité: '%'`, its `variations` (grilles 25/50/90 % and 25/75/90 % for creations before 04/2019 and 04/2020, else 50 % while `entreprise . durée d'activité < 1 an`) and its `avec` children "
     f"(CIPAV, prestation de service, service BIC, service BNC, vente restauration hébergement, notification). File sha256 BEFORE {sha(F_B)[:12]}... AFTER {sha(F_A)[:12]}...; `diff -r` of the two trees shows only this line. "
     "Note: the hunk context is re-indented (2 spaces) relative to G1 (4 spaces), so the commit's parent is a reformatted descendant of G1; applied with `patch -l` (whitespace-insensitive), context verified.")},
  {"kind": "engine_before_after", "article": None, "article_version_id": None,
   "quote_or_values": (f"`build`: raw_rule_count 641 both; parsed_rule_count 1220 (BEFORE, G1) -> 1227 (AFTER). `list`: names only in AFTER = {new_names}; names only in BEFORE = {gone_names}. "
     "These rules existed before (they already replaced the public rates via `remplace`) but were hidden by `privé: oui`; no other name changes.")},
  {"kind": "engine_before_after", "article": None, "article_version_id": None,
   "quote_or_values": (f"Rule `{TA}`, situation {json.dumps(SIT[A180 + ''], ensure_ascii=False)}: BEFORE -> {v(EB, A180.replace('@', '_TAUXACRE@'), TA)} ; AFTER -> {v(EA, A180.replace('@', '_TAUXACRE@'), TA)}. "
     f"Same rule, created 01/03/2023 / 500 jour / ACRE oui: AFTER -> {v(EA, A500.replace('@', '_TAUXACRE@'), TA)}; ACRE non (created 01/03/2024, 180 jour): AFTER -> {v(EA, N180.replace('@', '_TAUXACRE@'), TA)}; "
     f"created 01/01/2018 or 01/06/2019 with 400 jour: AFTER -> null (dirigeant . exonérations . ACRE evaluates non applicable on both sides). All 20 probes: " + ' || '.join(tauxacre_rows[:4]) + ' ...')},
  {"kind": "engine_before_after", "article": "D131-6-1", "article_version_id": VID['D131-6-1'],
   "quote_or_values": (f"Public rules, BEFORE = AFTER: {A180}: taux service BNC {v(EB, A180, C + 'taux service BNC')} / {v(EA, A180, C + 'taux service BNC')}; cotisations {v(EB, A180, C[:-3])} / {v(EA, A180, C[:-3])}; "
     f"revenu net {v(EB, A180, 'dirigeant . auto-entrepreneur . revenu net')} / {v(EA, A180, 'dirigeant . auto-entrepreneur . revenu net')}. {A500}: taux service BNC {v(EB, A500, C + 'taux service BNC')} / {v(EA, A500, C + 'taux service BNC')} (reduction stops after 12 months). "
     f"{N180}: {v(EB, N180, C + 'taux service BNC')} / {v(EA, N180, C + 'taux service BNC')}. AE_VENTE_ACRE_cre2024_180j: taux vente {v(EB, 'AE_VENTE_ACRE_cre2024_180j@01/09/2024', C + 'vente restauration hébergement . taux')} / {v(EA, 'AE_VENTE_ACRE_cre2024_180j@01/09/2024', C + 'vente restauration hébergement . taux')}; "
     f"AE_BIC_ACRE_cre2024_180j: taux service BIC {v(EB, 'AE_BIC_ACRE_cre2024_180j@01/09/2024', C + 'service BIC . taux')} / {v(EA, 'AE_BIC_ACRE_cre2024_180j@01/09/2024', C + 'service BIC . taux')} (ACRE sub-rule `service BIC` copies the full rate: pre-existing); "
     f"AE_CIPAV_ACRE_cre2024_180j: cotisations CIPAV . taux {v(EB, 'AE_CIPAV_ACRE_cre2024_180j@01/09/2024', C + 'cotisations CIPAV . taux')} / {v(EA, 'AE_CIPAV_ACRE_cre2024_180j@01/09/2024', C + 'cotisations CIPAV . taux')}, cotisations {v(EB, 'AE_CIPAV_ACRE_cre2024_180j@01/09/2024', C[:-3])} / {v(EA, 'AE_CIPAV_ACRE_cre2024_180j@01/09/2024', C[:-3])}. "
     f"Regression set cases_R1 (11 situations: salarié ATMP, AE BNC/BIC/vente/CIPAV/DROM, indépendant base/ACRE/trader at 01/07/2024 and 01/12/2024): tables identical = {tables_identical}. Total pairs compared {n_pairs}, differences {len(diffs)}.")},
  {"kind": "article_quote", "article": "L613-7", "article_version_id": VID['L613-7'],
   "quote_or_values": (f"{q_l6137}  (in force 2023-12-28..) -> the ACRE-period global rate of micro-entrepreneurs is delegated to a decree whose article is not in the bounded set; the library's 50 % (now exposed as `taux ACRE`) "
     f"is therefore recorded as an engine value, not as a text value: sophon link attempt on G1 = {ls('R2-G1-L613-7-tauxACRE')} (the store refused it: 'taux ACRE' is not a parsed rule of snapshot G1 because private rules are not listed; nothing written) and {ls('R2-G1post_R2-L613-7-tauxACRE')} (G1post_R2: observed 50).")},
  {"kind": "article_quote", "article": "D131-6-1", "article_version_id": VID['D131-6-1'],
   "quote_or_values": (f"{q_12m}  (in force 2018-01-01..) -> 12-month duration: library applies the reduction at 180 days (taux service BNC 10.6 = arrondi(50 % x 21.1)) and not at 500 days (21.1): "
     f"links {ls('R2-G1post_R2-D131-6-1-dans-les-12-mois')} and {ls('R2-G1post_R2-D131-6-1-apres-12-mois')}. D131-6-1 II (formula E/0,25 PSS x (PSS-R)) concerns the non-micro regime and gives no micro rate.")},
  {"kind": "article_quote", "article": "D613-4", "article_version_id": VID['D613-4'],
   "quote_or_values": (f"{q_bnc}  and  {q_cipav}  (in force 2024-07-01..2025-05-01) -> library AFTER still computes taux service BNC 21.1 and cotisations CIPAV . taux 21.2 at 01/09/2024: links {ls('R2-G1post_R2-D613-4-BNC')}, {ls('R2-G1post_R2-D613-4-CIPAV')} (FAILED = pre-existing gap, identical to G1 links L0113 of R1); "
     f"{q_bic} -> service BIC . taux 21.2: {ls('R2-G1post_R2-D613-4-BIC')} (aligned).")},
  {"kind": "engine_before_after", "article": None, "article_version_id": None,
   "quote_or_values": (f"sophon revalidate --law-snapshot S4 --rules-snapshot G1 vs G1post_R2: counts {json.dumps(reval_a['counts'])} on both; per-link rows identical after removing the snapshot id = {reval_identical}; "
     f"articles_without_any_link = {reval_a['articles_without_any_link']}; articles_changed vs stored links = {reval_a['articles_changed']} (inherited from the T0/T1a links on older versions, not from this event). "
     f"Law S3 -> S4 dump diff: header only (identical = {law_same}).")}
 ],
 "expected_values_if_mismatch": [],
 "pre_existing_gaps_not_caused_by_this_commit": [
  {"rule": C + "taux service BNC", "date": "01/09/2024", "found": 21.1, "text_value": 23.1, "article": "D613-4", "article_version_id": VID['D613-4'], "quote": q_bnc, "status": "identical before and after; link FAILED on G1post_R2 (and on G1 in R1)"},
  {"rule": C + "cotisations CIPAV . taux", "date": "01/09/2024", "found": 21.2, "text_value": 23.2, "article": "D613-4", "article_version_id": VID['D613-4'], "quote": q_cipav, "status": "identical before and after; link FAILED on G1post_R2"},
  {"rule": TA + " . CIPAV", "date": "01/09/2024", "found": 12.1, "text_value": None, "article": None, "article_version_id": None, "quote": None, "status": "CIPAV AE created >= 01/04/2020 is charged 12.1 % even with ACRE = non (1452 €/an on 12 000 €/an) on both sides; the ACRE-period rate is outside the bounded set, so no expected value is asserted"},
  {"note": "Other open items carried from T0/T1a/T1b/R1 (D613-6 v.LEGIARTI000049625264 shares, D632-1 2024 floor, meublés de tourisme 6 %, L613-7 minimum-contribution option, D756-5 II cap, 2024 unified base lines) are untouched by this commit; see work/README.md."}
 ],
 "outside_bounded_set": [
  "The decree article fixing the reduced global rate of ACRE-eligible micro-entrepreneurs (L613-7 I: 'Un taux global différent peut être fixé par décret ...'); D131-6-1 as given sets only the 12-month duration and the exemption formula of the non-micro regime. The library's 50 % (and the older 25/50/90 % and 25/75/90 % grids) cite URSSAF FAQ and service-public.fr pages, also outside the set. No value from these sources is asserted here.",
  "L131-6-4 (conditions and beneficiaries of the ACRE), referenced by D131-6-1 I/II, is not in the bounded set; the library's applicability rule `dirigeant . exonérations . ACRE` is therefore not checked against text.",
  "The semantics of `privé: oui` are engine documentation (publicodes), not law; they were established by running the engine (list 1220 -> 1227 names; evaluate error before / value after)."
 ],
 "approval": "none recorded",
 "notes": (f"AFTER tree = copy of G1 + forward application of the commit's hunk with GNU `patch -p1 -l` (the hunk is re-indented relative to G1; context verified by patch, `.orig` removed), at work/proposals/R2/after (meta.json), "
   "registered in sophon as rules snapshot G1post_R2 (first registration happened on the unpatched copy by mistake and was overwritten by re-registering the patched tree before any link referenced it; "
   "the snapshot file now has parsed_rule_count 1227 and the patched file hash). BEFORE = G1 itself (the commit's real parent is a later, reformatted descendant of G1 not available here; the only "
   "règles-level difference carried by this commit is the deleted line). Decision date 2024-09-02; law S4 unchanged vs S3. Approvals: none recorded anywhere in the corpus. "
   f"verify-store: ok={verify.get('ok')}, problems={verify.get('problems')}, links_checked={verify.get('links_checked')}."),
 "sophon_reports": reports,
 "sophon_links_added": [{k: l[k] for k in ('tag', 'id', 'status', 'article', 'article_id', 'rule', 'rules_snapshot', 'check_rule', 'date', 'expected', 'observed', 'error')} for l in links],
 "self_reported_tool_calls": SELF_CALLS
}
os.makedirs('output', exist_ok=True)
json.dump(answer, open('output/answer.json', 'w'), ensure_ascii=False, indent=1)
notes = f"""# R2 — reverse check of commit {COMMIT['commit'][:12]} (decision date 2024-09-02, law S4, rules G1)

## Verdict
**HARMLESS_REFACTOR** (confidence high). Commit `{COMMIT['commit']}` — "{COMMIT['subject']}" (authored {COMMIT['authored']}, committed {COMMIT['committed']}) —
deletes one line in one file of `modele-social/règles`: the attribute `privé: oui` of the rule
`dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux ACRE` (`dirigeant/auto-entrepreneur/exonérations.publicodes`).
`privé` only controls whether a rule is visible/evaluable/settable from outside its namespace (and shown in the documentation). No formula, unit,
default, threshold, date or applicability condition changes.

## Why not the other labels
- Not MISMATCH: nothing any bounded rule computes changed ({n_pairs} (situation, rule) pairs identical, {len(diffs)} differences; sophon revalidation identical on 113 links). The AE-rate
  misalignment with D613-4 v.{VID['D613-4']} (23,1 / 23,2 % since 2024-07-01, library 21,1 / 21,2) is pre-existing and identical on both sides; it is reported, not attributed to this commit.
- Not LEGITIMATE_INDEPENDENT_CHANGE: no implementation choice is made; the 50 % ACRE value that becomes visible already drove the public rates before.
- Not UNRESOLVED: the bounded text is not needed to settle a visibility-only edit; what is outside the set (the decree fixing the micro ACRE rate) concerns the pre-existing rule content, not this change.

## What the engine shows (BEFORE = G1, AFTER = G1 + patch)
- AFTER tree: `work/proposals/R2/after/modele-social` (copy of G1 + `patch -p1 -l`; the hunk is written against a 2-space re-indented file, G1 has 4 spaces; `diff -r` shows only the deleted line;
  file sha256 {sha(F_B)[:16]} -> {sha(F_A)[:16]}).
- `build`: 641 raw rules both; parsed 1220 -> 1227. `list` gains exactly these names (hidden before by `privé`):
{chr(10).join('  - ' + n for n in new_names)}
- `taux ACRE` itself (situation AE BNC, created 01/03/2024, `entreprise . durée d'activité` 180 jour, ACRE oui, date 01/09/2024): BEFORE `{v(EB, A180.replace('@', '_TAUXACRE@'), TA)}`; AFTER `{v(EA, A180.replace('@', '_TAUXACRE@'), TA)}`.
  At 500 jours (created 01/03/2023) AFTER = {v(EA, A500.replace('@', '_TAUXACRE@'), TA)}; with ACRE non AFTER = {v(EA, N180.replace('@', '_TAUXACRE@'), TA)}; created 2018/2019 with 400 jours: null on both sides (applicability rule `dirigeant . exonérations . ACRE` evaluates non applicable).
- Public rules identical, e.g. BNC with ACRE at 180 jours: taux service BNC {v(EB, A180, C + 'taux service BNC')} / {v(EA, A180, C + 'taux service BNC')}, cotisations {v(EB, A180, C[:-3])} / {v(EA, A180, C[:-3])}, revenu net {v(EB, A180, 'dirigeant . auto-entrepreneur . revenu net')} / {v(EA, A180, 'dirigeant . auto-entrepreneur . revenu net')};
  at 500 jours {v(EB, A500, C + 'taux service BNC')} / {v(EA, A500, C + 'taux service BNC')}; ACRE non {v(EB, N180, C + 'taux service BNC')} / {v(EA, N180, C + 'taux service BNC')}; vente with ACRE {v(EB, 'AE_VENTE_ACRE_cre2024_180j@01/09/2024', C + 'vente restauration hébergement . taux')} both; BIC with ACRE {v(EB, 'AE_BIC_ACRE_cre2024_180j@01/09/2024', C + 'service BIC . taux')} both (ACRE sub-rule `service BIC` copies the full rate, pre-existing);
  CIPAV created 2024: 12.1 % / 1452 €/an both (pre-existing leak). Regression set `cases_R1` (11 situations, salarié/AE/indépendant at 01/07/2024 and 01/12/2024): identical = {tables_identical}.
- Files: `work/evals/cases_R2_acre.json` (40 cases: 4 natures x 4 creation/duration regimes x public rules / `taux ACRE` probe + ACRE=non controls), outputs `R2_cases_*_before_G1.jsonl` / `_after_G1post.jsonl`, tables `R2_*_table.txt`.

## Law side
- S4 (legi-data 2.384.0, published 2024-09-01) vs S3: all 12 bounded articles have the same version ids and texts (dump diff = header only). Nothing on the law side moved.
- L613-7 v.{VID['L613-7']}: "{q_l6137}" — the ACRE-period micro rate is fixed by a decree article that is NOT in the bounded set.
- D131-6-1 v.{VID['D131-6-1']}: "{q_12m}" — 12-month duration; II gives the exemption formula for the non-micro regime only.
- D613-4 v.{VID['D613-4']}: "{q_bnc}" / "{q_cipav}" — in force at the decision date; library still 21.1 / 21.2 (pre-existing).

## sophon (system of record)
- Snapshots: S4 registered; G1 re-registered (idempotent); AFTER tree registered as `G1post_R2` (build 641/1227). A first registration of `G1post_R2` was made on the still-unpatched copy by mistake; it was overwritten by re-registering the patched tree before any link referenced it.
- `revalidate S4/G1` and `S4/G1post_R2`: counts {json.dumps(reval_a['counts'])} on both, per-link rows identical ({reval_identical}); no bounded article without a link; articles_changed {reval_a['articles_changed']} are inherited from links recorded on older versions (T0/T1a).
- Links added: {', '.join(l['tag'] + '=' + str(l.get('id')) + ':' + str(l.get('status')) for l in links)}.
  The L613-7 pair documents the flip: on G1 the store REJECTED the link ("not a parsed rule of snapshot G1": a private rule is not in the parsed list; nothing written) -> VERIFIED on G1post_R2 (observed 50).
  (The stored claim of that link says "expected FAILED" for G1; the actual outcome was REJECTED, which is stronger: the rule is not even addressable before the commit.) D613-4 BNC/CIPAV FAILED = pre-existing gap; BIC VERIFIED.
- Reports: {', '.join(reports)}. verify-store: ok={verify.get('ok')}, problems={verify.get('problems')}, links checked {verify.get('links_checked')}.

## Approval
none recorded (no sign-off, ratification or approval record exists in the corpus; a merge/commit/test is not an approval).

## Tool calls
self-reported: {SELF_CALLS} (including reads).
"""
open('output/NOTES.md', 'w').write(notes)
readme_add = f"""
## R2 (decision date 2024-09-02, law S4 = legi-data 2.384.0, rules G1; reverse check of commit 1932d654cf7a) — what was added
- Verdict HARMLESS_REFACTOR (high): commit "docs(auto-entrepreneur): Rend publique la règle taux ACRE des auto-entrepreneurs" = deletes `privé: oui` on `... cotisations . taux ACRE`. Public values identical ({n_pairs} pairs, 31 situations); `list` 1220 -> 1227 names (taux ACRE + 6 `avec` children become listed); `taux ACRE` evaluable after (50 at 180 jours, ACRE oui, created 01/03/2024).
- Law S4 == S3 for all 12 articles (dump diff header only). `law/S4_dump.txt`.
- LESSON patch: the commit hunk was re-indented (2 spaces) vs G1 (4 spaces): `patch -d <copy> -p1 -l -i diff.patch` (ignore whitespace) applies forward; delete the `.orig`. For reverse-apply keep `make_before_tree.py`. Check `diff -r` afterwards.
- LESSON engine: `privé: oui` hides the rule AND its `avec` children from `list`/parsed_rule_count; `evaluate` of a private rule returns an `error` entry ("n'est pas accessible") inside `evaluations` with rc 0.
- LESSON sophon: `snapshot-rules` with an existing id OVERWRITES the snapshot file (safe only if no link references it yet). Register snapshots only after the tree is final.
- AE ACRE facts (G1): `dirigeant . exonérations . ACRE` (dirigeant.publicodes) applicable if (AE and durée < 3 ans and création < 04/2020) or durée en début d'année < 1 an; with the override `entreprise . durée d'activité: "400 jour"` and creation 2018/2019 it evaluates non applicable (not investigated). ACRE sub-rule `service BIC` = full rate (no reduction) — pre-existing oddity.
- Files: `evals/cases_R2_acre.json`, `evals/R2_*`; `proposals/R2/after` (+ meta.json, list_before/after.json); `scripts/add_links_R2.py` (links {', '.join(str(l.get('id')) for l in links)}), `scripts/gen_answer_R2.py <calls>`; reports `sophon/reports/R2_*`. Store: {verify.get('links_checked')} links.
- Still open (unchanged): AE rates since 07/2024 (D613-4 v.{VID['D613-4']}: BNC 23,1 / CIPAV 23,2 vs 21,1 / 21,2), D613-6 shares, micro ACRE rate article outside set, CIPAV ACRE leak 12,1, plus the T0/T1a/T1b list.
"""
open('work/README.md', 'a').write(readme_add)
print('written output/answer.json, output/NOTES.md, README appended'); print('links:', [(l['tag'], l['id'], l['status']) for l in links]); print('pairs', n_pairs, 'diffs', diffs[:5], 'tables_identical', tables_identical, 'reval_identical', reval_identical, 'law_same', law_same)
