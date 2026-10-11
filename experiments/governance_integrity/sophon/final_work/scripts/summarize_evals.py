"""Compact table from evalbatch jsonl files: id | rule tail=value unit. usage: summarize_evals.py file.jsonl [...]"""
import json,sys
def find(o):
    if isinstance(o,dict):
        if "nodeValue" in o: return None
        for k in ("results","evaluations","values"):
            if k in o and isinstance(o[k],(dict,list)): return o[k]
        return {k:v for k,v in o.items() if isinstance(v,dict) and "nodeValue" in v} or o
    return o
for f in sys.argv[1:]:
    print("##",f)
    for line in open(f):
        r=json.loads(line)
        try: res=find(json.loads(r["stdout"]))
        except Exception: print("  ",r["id"],"RAW",r["stdout"][:300],r["stderr"][:200]); continue
        vals=[]
        items=res.items() if isinstance(res,dict) else [(x.get("rule") or x.get("name"),x) for x in res]
        for k,v in items:
            if isinstance(v,dict) and "nodeValue" in v:
                vals.append(f"{k.split(' . ')[-1] if k and k.count(' . ')>=3 else k}={v.get('nodeValue')}{v.get('unit') or ''}")
        print("  ",f"{r['id']:<28}"," | ".join(vals) if vals else ("KEYS="+str(list(res)[:8]) if isinstance(res,dict) else str(res)[:200]))
