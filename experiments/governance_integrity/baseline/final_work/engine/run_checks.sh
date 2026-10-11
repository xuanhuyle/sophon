#!/usr/bin/env bash
# Usage: run_checks.sh <rules_dir[|rules_dir2...]> <spec.json> [out.jsonl]   (several rule dirs separated by "|", e.g. modele-ti/règles|modele-commun/règles)
# spec.json = [{"id":"...","situation":{...},"rules":["a . b", ...]}, ...]
# Runs the organisation's engine wrapper once per check and prints compact lines.
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RULES="$1"; SPEC="$2"; OUT="${3:-/dev/null}"
node -e '
const fs=require("fs"),{execFileSync}=require("child_process");
const [rules,spec,out,root]=process.argv.slice(1);
const checks=JSON.parse(fs.readFileSync(spec,"utf8"));
let lines=[];
for(const c of checks){
  const args=["src/publicodes_eval.mjs","evaluate"]; for(const d of rules.split("|")) args.push("--rules",d); args.push("--situation",JSON.stringify(c.situation));
  for(const r of c.rules) args.push("--rule",r);
  let res; try{ res=JSON.parse(execFileSync("node",args,{cwd:root,encoding:"utf8",maxBuffer:1e8})); }catch(e){ res={error:String(e.stdout||e.message).slice(0,500)}; }
  const rec={id:c.id,date:c.situation.date,situation:c.situation,situation_error:res.situation_error||null,error:res.error||null,results:{}};
  for(const [k,v] of Object.entries(res.evaluations||{})) rec.results[k]=v.error?{error:v.error}:{value:v.nodeValue,unit:v.unit,missing:v.missing_count,missing_names:v.missing_variables};
  lines.push(JSON.stringify(rec));
  console.log("### "+c.id+" @ "+c.situation.date+(rec.situation_error?"  SITUATION_ERROR: "+rec.situation_error:"")+(rec.error?"  ERROR: "+rec.error:""));
  for(const [k,v] of Object.entries(rec.results)) console.log("   "+k+" = "+(v.error?("ERR "+v.error):(JSON.stringify(v.value)+(v.unit?" "+v.unit:"")+(v.missing?"  [missing:"+v.missing+": "+(v.missing_names||[]).slice(0,6).join("; ")+"]":""))));
}
if(out!=="/dev/null") fs.writeFileSync(out,lines.join("\n")+"\n");
' "$RULES" "$SPEC" "$OUT" "$ROOT"
