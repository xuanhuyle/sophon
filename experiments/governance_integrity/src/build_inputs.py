#!/usr/bin/env python3
"""Build the sealed, immutable inputs of the governance-integrity experiment.

Everything this script writes is derived from artifacts pinned in SOURCES.json:
  * governing corpus: the bounded Code de la securite sociale article set, extracted
    from dated @socialgouv/legi-data snapshots (already downloaded and hashed);
  * semantic model: the mon-entreprise rule trees at pinned git commits (git archive),
    the project's own regression fixtures at those commits, and the git history of the
    rule directories up to each pin date (never after);
  * reverse-case diffs: the exact commits named in PROTOCOL.md, with the parent tree
    where the rules moved to another package;
  * held-out material for the scorer only: OpenFisca-France parameter files and the
    maintainers' later commits (not gold, kept for comparison).

Run from the experiment directory:
  python -B src/build_inputs.py --legidata DIR --mon-entreprise DIR --openfisca DIR --out .

It refuses to overwrite an existing inputs/ or held_out/ directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

CSS_ID = "LEGITEXT000006073189"

# Protocol §2.1: bounded article set
ARTICLES = ["L131-6", "L136-3", "L613-7", "D131-6-1", "D136-5", "D613-4", "D613-5", "D613-6",
            "D621-2", "D632-1", "D633-3", "D756-5"]

# Protocol §2.1: snapshots (id -> legi-data version). Publish dates and hashes come from SOURCES.json.
SNAPSHOTS = {
    "S0": "2.360.0", "S1": "2.361.0", "S2": "2.375.0", "S3": "2.381.0", "S4": "2.384.0",
    "S5": "2.385.0", "S6": "2.464.0", "S7": "2.469.0", "S8": "2.489.0", "S9": "2.514.0", "S10": "2.572.0",
}

# Protocol §2.2: git pins (id -> commit)
PINS = {
    "G0": "d9242882f96bda5b4418b7c1c3ff46b0e2a1c5ce",
    "G1": "2a0e452617fc33b955096f4bb7f7f305ec0670ad",
    "G2": "3a4091ae1cafdd4572bfd10d6352fd04db8da419",
    "G3": "d6c37427172707b4c0fa64d9e6f18ea67f9f67b4",
    "G4": "a61b72947fec1e1383e07b3278424593dc296ba2",
}

# Protocol §3: reverse-case diffs (id -> commit). R4 and R5 touch modele-ti, so their parent
# trees (modele-ti + modele-commun) are sealed as context.
REVERSE = {
    "R1": ("2a0e452617fc33b955096f4bb7f7f305ec0670ad", ["modele-social/règles"], None),
    "R2": ("1932d654c", ["modele-social/règles"], None),
    "R3": ("9bb43d710094d8f572c64997ce991c8d395c5753", ["modele-social/règles"], None),
    "R4": ("d3e0cfe0f", ["modele-ti/règles", "modele-commun/règles"], "parent"),
    "R5": ("c14ee26d0", ["modele-ti/règles", "modele-commun/règles"], "parent"),
}

# Scorer-only: the maintainers' later commits for the episodes (not gold).
MAINTAINER_COMMITS = {
    "E1_step1_8d04dbb65": "8d04dbb650366c0bb4af0858a569049d845a7230",
    "E1_step2_1d2874c5e": "1d2874c5eb0f5a26b913c72a83920504c42766c9",
    "E2_88cb2ce96": "88cb2ce9660ba41bbc91ae6676a6ef96bb0281af",
    "E3_4ad1f7e4d": "4ad1f7e4d",
    "E3_ff1c02dd1": "ff1c02dd1",
    "E4_acre_212c2dc07": "212c2dc07ef886449bc590e4d71c8ad24b161480",
}

ORACLE_FILES = [
    "openfisca_france/parameters/prelevements_sociaux/professions_liberales/auto_entrepreneur/cotisations_prestations/service.yaml",
    "openfisca_france/parameters/prelevements_sociaux/professions_liberales/auto_entrepreneur/cotisations_prestations/cipav.yaml",
    "openfisca_france/parameters/prelevements_sociaux/professions_liberales/auto_entrepreneur/cotisations_prestations/vente.yaml",
    "openfisca_france/parameters/prelevements_sociaux/professions_liberales/auto_entrepreneur/cotisations_prestations/service_bic.yaml",
    "openfisca_france/parameters/prelevements_sociaux/cotisations_taxes_independants_artisans_commercants/ret_ac/tous_independants/tout_salaire.yaml",
    "LICENSE",
]

# Protocol §3: task table (decision date, law snapshot(s), rules pin, diff)
TASKS = [
    {"task": "T0", "decision_date": "2024-05-25", "law": ["S0"], "rules": "G0", "diff": None},
    {"task": "T1a", "decision_date": "2024-06-01", "law": ["S1"], "rules": "G0", "diff": None},
    {"task": "T1b", "decision_date": "2024-07-17", "law": ["S3"], "rules": "G1", "diff": None},
    {"task": "R1", "decision_date": "2024-07-17", "law": ["S3"], "rules": "G1", "diff": "R1"},
    {"task": "R2", "decision_date": "2024-09-02", "law": ["S4"], "rules": "G1", "diff": "R2"},
    {"task": "R3", "decision_date": "2024-10-19", "law": ["S5"], "rules": "G2", "diff": "R3"},
    {"task": "R4", "decision_date": "2026-03-31", "law": ["S9"], "rules": "G4", "diff": "R4"},
    {"task": "R5", "decision_date": "2026-10-05", "law": ["S10"], "rules": "G4", "diff": "R5"},
    {"task": "M0", "decision_date": "2025-10-01", "law": ["S6", "S7"], "rules": "G3", "diff": None},
    {"task": "M1", "decision_date": "2026-01-01", "law": ["S7", "S8"], "rules": "G3", "diff": None},
    {"task": "M2", "decision_date": "2026-03-31", "law": ["S8", "S9"], "rules": "G4", "diff": None},
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_html(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


def git(repo: Path, *args: str, binary: bool = False):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def extract_articles(legidata_json: Path):
    css = json.load(open(legidata_json, encoding="utf-8"))
    found = {}

    def walk(n):
        if isinstance(n, dict):
            d = n.get("data", {})
            if n.get("type") == "article" and d.get("num") in ARTICLES:
                rec = {k: d.get(k) for k in ("num", "id", "cid", "etat", "dateDebut", "dateFin", "articleVersions",
                                             "lienModifications", "nota")}
                rec["text"] = strip_html(d.get("texte", ""))
                rec["text_sha256"] = hashlib.sha256(rec["text"].encode("utf-8")).hexdigest()
                found.setdefault(d["num"], []).append(rec)
            for c in n.get("children", []) or []:
                walk(c)
        elif isinstance(n, list):
            for c in n:
                walk(c)

    walk(css)
    return found


def build_law(legidata_root: Path, sources: dict, out: Path, manifest: dict):
    pkgs = {p["version"]: p for p in sources["npm_packages"] if p["name"] == "@socialgouv/legi-data"}
    for sid, ver in SNAPSHOTS.items():
        src = legidata_root / f"v{ver}" / "package" / "data" / f"{CSS_ID}.json"
        if not src.exists():
            sys.exit(f"missing legi-data snapshot {ver} at {src}")
        arts = extract_articles(src)
        missing = [a for a in ARTICLES if a not in arts]
        d = out / "inputs" / "law" / f"{sid}_legi-data-{ver}"
        d.mkdir(parents=True)
        json.dump({"snapshot": sid, "legi_data_version": ver, "code": CSS_ID,
                   "published": pkgs.get(ver, {}).get("published"),
                   "tarball_sha256": pkgs.get(ver, {}).get("tarball_sha256"),
                   "integrity": pkgs.get(ver, {}).get("integrity"),
                   "articles_missing_in_snapshot": missing,
                   "articles": arts}, open(d / "articles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        manifest["law"][sid] = {"dir": str(d.relative_to(out)), "legi_data_version": ver, "missing": missing}
        print(f"law {sid} <- legi-data {ver}: {sum(len(v) for v in arts.values())} article records, missing={missing}")


def archive_tree(repo: Path, commit: str, paths: list, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    data = git(repo, "archive", commit, *paths, binary=True)
    import io
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        tf.extractall(dest, filter="data")  # trusted local clone pinned by commit


def commit_meta(repo: Path, commit: str) -> dict:
    full = git(repo, "rev-parse", commit).strip()
    line = git(repo, "log", "-1", "--format=%H%x00%ci%x00%ai%x00%an%x00%s", full).strip().split("\x00")
    return {"commit": line[0], "committed": line[1], "authored": line[2], "author": line[3], "subject": line[4]}


def build_rules(repo: Path, out: Path, manifest: dict):
    for gid, commit in PINS.items():
        meta = commit_meta(repo, commit)
        d = out / "inputs" / "rules" / f"{gid}_{meta['commit'][:12]}"
        archive_tree(repo, meta["commit"], ["modele-social/règles", "modele-social/package.json",
                                            "modele-social/CHANGELOG.md"], d)
        # pre-existing tests at the pin (same-organisation evidence)
        tests = ["site/test/regressions/auto-entrepreneur.yaml",
                 "site/test/regressions/__snapshots__/auto-entrepreneur.test.ts.snap",
                 "site/test/regressions/auto-entrepreneur.test.ts",
                 "api/source/test-e2e/index.test.ts"]
        present = [t for t in tests if git(repo, "ls-tree", "--name-only", meta["commit"], "--", t).strip()]
        if present:
            archive_tree(repo, meta["commit"], present, d / "existing_tests")
        # history up to the pin's commit date, never after
        until = meta["committed"]
        hist = git(repo, "log", "--format=%H %ci %an %s", f"--until={until}", meta["commit"], "--", "modele-social/règles")
        (d / "HISTORY.txt").write_text(f"# git log for modele-social/règles up to {until} (commit {meta['commit']})\n{hist}", encoding="utf-8")
        # diffs of the bounded rule files over the 18 months before the pin (bounded size)
        bounded = ["modele-social/règles/dirigeant/auto-entrepreneur", "modele-social/règles/dirigeant/indépendant",
                   "modele-social/règles/dirigeant/indépendant.publicodes", "modele-social/règles/dirigeant/exonérations",
                   "modele-social/règles/dirigeant/exonérations.publicodes", "modele-social/règles/dirigeant/dirigeant.publicodes"]
        patch = git(repo, "log", "-p", "--format=commit %H%n%ci %an%n%s%n", f"--until={until}", "--since=18 months ago" if False else "--since=" + shift_months(until, -18),
                    meta["commit"], "--", *bounded)
        (d / "history_bounded_rules.patch").write_text(patch, encoding="utf-8")
        version = json.load(open(d / "modele-social" / "package.json", encoding="utf-8")).get("version")
        meta.update({"in_tree_modele_social_version": version, "existing_tests": present})
        json.dump(meta, open(d / "meta.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        manifest["rules"][gid] = {"dir": str(d.relative_to(out)), **meta}
        print(f"rules {gid} <- {meta['commit'][:12]} ({meta['committed']}), in-tree version {version}, tests {len(present)}")


def shift_months(iso_date: str, months: int) -> str:
    y, m = int(iso_date[:4]), int(iso_date[5:7])
    m2 = m + months
    y += (m2 - 1) // 12
    m2 = (m2 - 1) % 12 + 1
    return f"{y:04d}-{m2:02d}-01"


def build_reverse(repo: Path, out: Path, manifest: dict):
    for rid, (commit, paths, ctx) in REVERSE.items():
        meta = commit_meta(repo, commit)
        d = out / "inputs" / "diffs" / f"{rid}_{meta['commit'][:12]}"
        d.mkdir(parents=True)
        patch = git(repo, "show", "--format=commit %H%nAuthor: %an%nAuthorDate: %ai%nCommitDate: %ci%n%n    %s%n%n%b", meta["commit"], "--", *paths)
        (d / "diff.patch").write_text(patch, encoding="utf-8")
        stat = git(repo, "show", "--stat", "--format=", meta["commit"])
        (d / "stat.txt").write_text(stat, encoding="utf-8")
        if ctx == "parent":
            archive_tree(repo, meta["commit"] + "^", paths, d / "context_parent_tree")
            archive_tree(repo, meta["commit"], paths, d / "context_tree_after")
        json.dump(meta, open(d / "meta.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        manifest["diffs"][rid] = {"dir": str(d.relative_to(out)), **meta}
        print(f"diff {rid} <- {meta['commit'][:12]} {meta['subject']}")


def build_held_out(repo: Path, openfisca: Path, out: Path, manifest: dict):
    ho = out / "held_out"
    (ho / "oracle").mkdir(parents=True)
    for rel in ORACLE_FILES:
        src = openfisca / rel
        if src.exists():
            dst = ho / "oracle" / Path(rel).name
            shutil.copy2(src, dst)
    (ho / "oracle" / "ORIGIN.txt").write_text(
        "OpenFisca-France parameter files copied verbatim from https://github.com/openfisca/openfisca-france at commit "
        + git(openfisca, "rev-parse", "HEAD").strip() + " (AGPL-3.0; LICENSE copied alongside). Used only as an independent reference by the scorer.\n",
        encoding="utf-8")
    (ho / "maintainers").mkdir()
    for name, commit in MAINTAINER_COMMITS.items():
        meta = commit_meta(repo, commit)
        patch = git(repo, "show", "--format=commit %H%nAuthorDate: %ai%nCommitDate: %ci%n%s%n", meta["commit"], "--", "modele-social/règles", "modele-ti/règles", "modele-commun/règles")
        (ho / "maintainers" / f"{name}.patch").write_text(patch, encoding="utf-8")
    (ho / "README.md").write_text(
        "# held_out\n\nScorer-only material. Solver arms must never read this directory; during solver runs it is encrypted.\n\n"
        "- `oracle/`: OpenFisca-France parameter files (independent encoding of the same law).\n"
        "- `maintainers/`: what the mon-entreprise maintainers actually committed later. Not gold.\n"
        "- `REFERENCE.json`, `COVERAGE.json`: written by `src/build_reference.py` from the article texts before any solver run.\n",
        encoding="utf-8")
    manifest["held_out"] = {"oracle_commit": git(openfisca, "rev-parse", "HEAD").strip(), "maintainer_patches": list(MAINTAINER_COMMITS)}


def write_manifest(out: Path, manifest: dict):
    files = {}
    for base in ("inputs", "held_out"):
        for p in sorted((out / base).rglob("*")):
            if p.is_file():
                files[str(p.relative_to(out))] = sha256_file(p)
    manifest["files"] = files
    json.dump(manifest, open(out / "inputs" / "MANIFEST.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"manifest: {len(files)} files hashed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legidata", required=True, help="directory holding v<version>/package/data/*.json extractions")
    ap.add_argument("--mon-entreprise", required=True)
    ap.add_argument("--openfisca", required=True)
    ap.add_argument("--out", default=".", help="experiment directory (contains SOURCES.json)")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    sources = json.load(open(out / "SOURCES.json", encoding="utf-8"))
    for base in ("inputs", "held_out"):
        if (out / base).exists():
            sys.exit(f"{out / base} exists; refusing to overwrite sealed inputs")
    manifest = {"built_from": {"legidata_dir": str(Path(a.legidata).resolve()), "mon_entreprise_head": git(Path(a.mon_entreprise), "rev-parse", "HEAD").strip(),
                               "openfisca_head": git(Path(a.openfisca), "rev-parse", "HEAD").strip()},
                "protocol_sha256": (out / "PROTOCOL.sha256").read_text().split()[0], "articles": ARTICLES,
                "law": {}, "rules": {}, "diffs": {}, "tasks": TASKS}
    build_law(Path(a.legidata), sources, out, manifest)
    build_rules(Path(a.mon_entreprise), out, manifest)
    build_reverse(Path(a.mon_entreprise), out, manifest)
    build_held_out(Path(a.mon_entreprise), Path(a.openfisca), out, manifest)
    json.dump(TASKS, open(out / "inputs" / "TASKS.json", "w", encoding="utf-8"), indent=1)
    write_manifest(out, manifest)


if __name__ == "__main__":
    main()
