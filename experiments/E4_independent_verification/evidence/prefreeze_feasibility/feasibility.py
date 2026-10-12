# PRE-FREEZE FEASIBILITY ONLY: does each candidate stack build and does its native query execute? (not scored)
import sys, json
from pathlib import Path
sys.path.insert(0, 'src')
import candidate_stack as cs
E4 = Path('.').resolve()
out = {}
plan = [("M1","PINNED"),("M6B","BOUNDARY"),("M3","BOUNDARY"),("M4","PINNED"),("M2","PINNED"),("M5","PINNED"),("M5B","PINNED"),("M6","PINNED"),("C4","PINNED"),("M1","NEGQTY"),("M2","STALE")]
for cid, snap in plan:
    c = json.load(open(f'candidates/{cid}.json'))
    st = cs.build(f'feas_{cid}_{snap}', c['patch'], E4/'runs'/'snapshots'/snap, E4/'.upstream', E4/'runs'/'feasibility_stacks')
    r = {"build_ok": st['ok'], "error": st.get('error'), "steps": {k: v['exit_code'] for k, v in st.get('steps', {}).items()}}
    if st['ok']:
        e = cs.execute(st, c['query']); el = cs.execute(st, {**c['query'], 'group_by': ['sales']})
        r.update(year_exit=e.get('exit_code'), year_ok=e['ok'], line_exit=el.get('exit_code'), line_ok=el['ok'], line_rows=len(el.get('rows') or []),
                 err=(e.get('stdout_tail') or e.get('error') or '')[-300:] if not e['ok'] else None)
    out[f"{cid}@{snap}"] = r
    print(cid, snap, json.dumps(r)[:400], flush=True)
json.dump(out, open('runs/feasibility_result.json','w'), indent=1)
