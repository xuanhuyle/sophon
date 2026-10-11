"""Tamper tests for the sophon store (PROTOCOL.md §3: robustness diagnostics, never episodes).

Each test builds a tiny store from the sealed inputs, records one VERIFIED link, then tampers
with exactly one thing and asserts that the kernel refuses, invalidates or fails closed:

  1. editing the cited quote in the store                    -> verify-store fails (hash chain + quote)
  2. changing the effective date / version of the article    -> revalidate reports REASSESS_LAW_CHANGED
  3. recording an approval without an evidence file           -> refused
  4. claiming VERIFIED without an executable check            -> refused
  5. changing the rule's logic (the rate value) on disk       -> revalidate reports BROKEN, verify-store reports the edit
  6. a quote that is not in the article text                  -> link REJECTED

Run:  python -B -m pytest tests/ -q   (or python -B tests/test_tamper.py)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOPHON = ROOT / "src" / "sophon.py"
LAW_S0 = next((ROOT / "inputs" / "law").glob("S0_*")) / "articles.json"
LAW_S3 = next((ROOT / "inputs" / "law").glob("S3_*")) / "articles.json"
RULES_G0 = next((ROOT / "inputs" / "rules").glob("G0_*"))
BNC = "dirigeant . auto-entrepreneur . cotisations et contributions . cotisations . taux service BNC"
SITUATION = json.dumps({"date": "01/05/2024", "salarié": "non", "entreprise . catégorie juridique": "'EI'",
                        "entreprise . catégorie juridique . EI . auto-entrepreneur": "oui", "dirigeant . auto-entrepreneur": "oui",
                        "entreprise . activité . nature": "'libérale'", "dirigeant . auto-entrepreneur . chiffre d'affaires": "1000 €/mois"}, ensure_ascii=False)
QUOTE = "10 000 euros 34 % 6 600 euros 21,1 %"


def run(store: Path, *args: str) -> tuple[int, dict]:
    r = subprocess.run([sys.executable, "-B", str(SOPHON), "--store", str(store), *args], capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    try:
        return r.returncode, json.loads(out[-1]) if out else {}
    except json.JSONDecodeError:
        # asof prints a multi-line JSON document
        return r.returncode, json.loads(r.stdout)


def fresh(tmp: Path) -> tuple[Path, Path]:
    """Store with S0 law, a private copy of G0 rules, and one VERIFIED link. Returns (store, rules_copy)."""
    rules_copy = tmp / "G0" / "modele-social"
    shutil.copytree(RULES_G0 / "modele-social", rules_copy)
    store = tmp / "store"
    rc, _ = run(store, "snapshot-law", "--id", "S0", "--articles", str(LAW_S0)); assert rc == 0
    rc, _ = run(store, "snapshot-law", "--id", "S3", "--articles", str(LAW_S3)); assert rc == 0
    rc, o = run(store, "snapshot-rules", "--id", "G0", "--rules-dir", str(rules_copy / "règles"), "--meta", str(RULES_G0 / "meta.json")); assert rc == 0 and o["ok"], o
    rc, o = run(store, "link", "add", "--rule", BNC, "--rules-snapshot", "G0", "--article", "D613-4", "--law-snapshot", "S0",
                "--quote", QUOTE, "--claim", "BNC global rate 21,1 %", "--check-rule", BNC, "--check-situation", SITUATION, "--expect", "21.1")
    assert rc == 0 and o["status"] == "VERIFIED", o
    return store, rules_copy


def test_clean_store_verifies():
    with tempfile.TemporaryDirectory() as t:
        store, _ = fresh(Path(t))
        rc, o = run(store, "verify-store")
        assert rc == 0 and o["ok"], o


def test_1_edited_quote_is_detected():
    with tempfile.TemporaryDirectory() as t:
        store, _ = fresh(Path(t))
        p = store / "links.jsonl"
        p.write_text(p.read_text(encoding="utf-8").replace("21,1 %\"", "21,2 %\""), encoding="utf-8")
        rc, o = run(store, "verify-store")
        assert rc == 2 and not o["ok"] and any("hash mismatch" in x for x in o["problems"]), o


def test_2_changed_effective_date_or_version_triggers_reassessment():
    with tempfile.TemporaryDirectory() as t:
        store, rules_copy = fresh(Path(t))
        # S3 carries a newer D613-4 version (in force 2024-07-01): revalidating against it must flag the link
        rc, o = run(store, "revalidate", "--law-snapshot", "S3", "--rules-snapshot", "G0")
        assert rc == 0 and o["counts"].get("REASSESS_LAW_CHANGED") == 1, o
        assert BNC in o["rules_to_reassess"] and "D613-4" in o["articles_changed"]
        # tampering with the stored effective date inside the snapshot is caught by verify-store
        law = store / "law" / "S0.json"
        j = json.load(open(law, encoding="utf-8"))
        j["articles"]["D613-4"]["text"] = j["articles"]["D613-4"]["text"].replace("21,1 %", "23,1 %")
        json.dump(j, open(law, "w", encoding="utf-8"), ensure_ascii=False)
        rc, o = run(store, "verify-store")
        assert rc == 2 and any("tampered snapshot" in x or "no longer matches" in x for x in o["problems"]), o


def test_3_approval_without_evidence_is_refused():
    with tempfile.TemporaryDirectory() as t:
        store, _ = fresh(Path(t))
        rc, o = run(store, "link", "add", "--rule", BNC, "--rules-snapshot", "G0", "--article", "D613-4", "--law-snapshot", "S0",
                    "--quote", QUOTE, "--claim", "x", "--status", "INFERRED", "--approval-file", str(Path(t) / "does-not-exist.pdf"))
        assert rc != 0
        links = [json.loads(l) for l in (store / "links.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(links) == 1 and links[0]["approval"]["status"] == "none recorded"


def test_4_verified_without_check_is_refused():
    with tempfile.TemporaryDirectory() as t:
        store, _ = fresh(Path(t))
        rc, o = run(store, "link", "add", "--rule", BNC, "--rules-snapshot", "G0", "--article", "D613-4", "--law-snapshot", "S0",
                    "--quote", QUOTE, "--claim", "x", "--status", "VERIFIED")
        assert rc == 1 and o["status"] == "REJECTED", o


def test_5_changed_rule_logic_breaks_the_check():
    with tempfile.TemporaryDirectory() as t:
        store, rules_copy = fresh(Path(t))
        f = rules_copy / "règles" / "dirigeant" / "auto-entrepreneur" / "auto-entrepreneur.publicodes"
        s = f.read_text(encoding="utf-8")
        assert "alors: 21.1%" in s
        f.write_text(s.replace("alors: 21.1%", "alors: 23.1%", 1), encoding="utf-8")
        rc, o = run(store, "revalidate", "--law-snapshot", "S0", "--rules-snapshot", "G0")
        assert rc == 0 and o["counts"].get("BROKEN") == 1, o
        rc, o = run(store, "verify-store")
        assert rc == 2 and any("edited after snapshot" in x for x in o["problems"]), o


def test_6_quote_not_in_text_is_rejected():
    with tempfile.TemporaryDirectory() as t:
        store, _ = fresh(Path(t))
        rc, o = run(store, "link", "add", "--rule", BNC, "--rules-snapshot", "G0", "--article", "D613-4", "--law-snapshot", "S0",
                    "--quote", "23,1 %", "--claim", "x")
        assert rc == 1 and o["status"] == "REJECTED" and "quote" in o["problems"][0], o


if __name__ == "__main__":
    import inspect
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and inspect.isfunction(fn):
            try:
                fn(); print(f"PASS {name}")
            except AssertionError as e:
                failures += 1; print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
