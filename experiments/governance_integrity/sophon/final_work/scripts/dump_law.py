import json,datetime,sys
p=sys.argv[1]
d=json.load(open(p))
def dt(ms):
    if ms is None: return None
    try: return datetime.datetime.utcfromtimestamp(ms/1000).strftime("%Y-%m-%d")
    except Exception: return str(ms)
print("SNAPSHOT", d.get("snapshot"), "legi_data", d.get("legi_data_version"), "published", d.get("published"), "missing", d.get("articles_missing_in_snapshot"))
for key,lst in d["articles"].items():
    for a in lst:
        print("="*100)
        print(f"ARTICLE {a['num']}  id={a['id']}  cid={a.get('cid')}  etat={a.get('etat')}  dateDebut={dt(a.get('dateDebut'))}  dateFin={dt(a.get('dateFin'))}")
        print("articleVersions:")
        for av in a.get("articleVersions",[]):
            print("   ", {kk:(dt(vv) if kk in ("dateDebut","dateFin") else vv) for kk,vv in av.items()})
        print("lienModifications:")
        for lm in a.get("lienModifications",[]): print("   ", json.dumps(lm, ensure_ascii=False))
        other={k:v for k,v in a.items() if k not in ("text","articleVersions","lienModifications","num","id","cid","etat","dateDebut","dateFin")}
        if other: print("other:", json.dumps(other, ensure_ascii=False)[:500])
        print("--- TEXT ---")
        print(a.get("text"))
