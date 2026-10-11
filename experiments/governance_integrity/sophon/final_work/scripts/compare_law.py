"""Compare two law snapshots: a sophon store law/<S>.json or an inputs articles.json.
usage: python3 -I work/scripts/compare_law.py OLD NEW [--full ART ...]
Prints per-article id/etat/date/version changes and a word-level text diff."""
import json,sys,difflib,datetime
def dt(ms):
    if ms is None: return None
    if isinstance(ms,str): return ms
    return datetime.datetime.fromtimestamp(ms/1000,datetime.timezone.utc).strftime("%Y-%m-%d")
def load(p):
    d=json.load(open(p))
    arts={}
    if "articles" in d and isinstance(d["articles"],dict):
        for k,lst in d["articles"].items():
            if isinstance(lst,list):
                for a in lst: arts[a["num"]]=a
            elif isinstance(lst,dict): arts[lst.get("num",k)]=lst
    else:
        print("UNKNOWN STRUCTURE keys=",list(d.keys())[:20]); 
        for k,v in d.items():
            if isinstance(v,dict) and "text" in v: arts[v.get("num",k)]=v
    return d,arts
old,A=load(sys.argv[1]); new,B=load(sys.argv[2])
full=set(sys.argv[sys.argv.index("--full")+1:]) if "--full" in sys.argv else set()
print("OLD keys:",list(old.keys())[:12]); print("NEW keys:",list(new.keys())[:12])
for num in sorted(set(A)|set(B)):
    a=A.get(num); b=B.get(num)
    if a is None or b is None: print(f"## {num}: only in {'NEW' if a is None else 'OLD'}"); continue
    ch=[]
    for k in ("id","etat","dateDebut","dateFin"):
        if a.get(k)!=b.get(k): ch.append(f"{k}: {dt(a.get(k))} -> {dt(b.get(k))}")
    va={v["id"]:v for v in a.get("articleVersions",[])}; vb={v["id"]:v for v in b.get("articleVersions",[])}
    for vid in vb:
        if vid not in va: ch.append(f"NEW VERSION {vid} v{vb[vid].get('version')} {vb[vid].get('etat')} {dt(vb[vid].get('dateDebut'))}..{dt(vb[vid].get('dateFin'))}")
        elif va[vid]!=vb[vid]: ch.append(f"VERSION META {vid}: {va[vid].get('etat')} {dt(va[vid].get('dateDebut'))}..{dt(va[vid].get('dateFin'))} -> {vb[vid].get('etat')} {dt(vb[vid].get('dateDebut'))}..{dt(vb[vid].get('dateFin'))}")
    ta=a.get("text") or ""; tb=b.get("text") or ""
    if ta!=tb:
        wa=ta.split(); wb=tb.split()
        sm=difflib.SequenceMatcher(None,wa,wb,autojunk=False)
        ops=[(t,' '.join(wa[i1:i2]),' '.join(wb[j1:j2])) for t,i1,i2,j1,j2 in sm.get_opcodes() if t!='equal']
        ch.append(f"TEXT differs: chars {len(ta)}->{len(tb)}; words {len(wa)}->{len(wb)}; word-level ops={len(ops)} (0 ops => whitespace only)")
        for t,x,y in ops[:40]: ch.append(f"   {t}: '{x}' -> '{y}'")
    print(f"## {num}: " + ("UNCHANGED" if not ch else ""))
    for c in ch: print("   ",c)
    if num in full:
        print("   lienModifications NEW:"); [print("      ",json.dumps(l,ensure_ascii=False)) for l in b.get("lienModifications",[])]
        print("   nota NEW:",b.get("nota")); print("   --- FULL NEW TEXT ---"); print(tb); print("   --- END ---")
