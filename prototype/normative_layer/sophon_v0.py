"""Sophon V0 — deliberately small, LAB-ONLY normative context service.

NO production authorization or legal interpretation. Only two narrow text grammars
are automatically recognized; any other clause remains unresolved.
Python >=3.10, stdlib only. API is local and not authenticated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

CREDIT = re.compile(
    r"^If monthly service availability falls below (?P<availability>\d+(?:\.\d+)?)%[,]? "
    r"the customer is entitled to a service credit of (?P<credit>\d+(?:\.\d+)?)% "
    r"of the monthly subscription fee, excluding scheduled maintenance\.$",
    re.IGNORECASE,
)
APPROVAL = re.compile(
    r"^Service credits above (?:EUR|€)\s*(?P<limit>\d+(?:\.\d+)?) "
    r"require (?P<approver>[A-Za-z][A-Za-z ]*) approval\.$",
    re.IGNORECASE,
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def money(x: Decimal) -> str:
    return str(x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def as_decimal(value: Any, *, minimum: Decimal = Decimal("0")) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("numeric field may not be boolean")
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid decimal") from None
    if not n.is_finite() or n < minimum:
        raise ValueError("numeric field outside allowed range")
    return n


def ymd(s: str) -> str:
    return date.fromisoformat(s).isoformat()


def parse_clauses(text: str, kind: str) -> list[dict]:
    # Explicitly a narrow recognizer, NOT general contract understanding.
    clauses = [x.strip() for x in text.splitlines() if x.strip()]
    out = []
    for clause in clauses:
        m = CREDIT.fullmatch(clause) if kind == "customer_contract" else APPROVAL.fullmatch(clause)
        if not m:
            out.append({"type": "unresolved", "source_excerpt": clause,
                        "candidate": None, "reason": "UNSUPPORTED_OR_AMBIGUOUS_LANGUAGE"})
            continue
        if kind == "customer_contract":
            availability, rate = (as_decimal(m.group("availability")), as_decimal(m.group("credit")))
            if availability > 100 or rate > 100:
                out.append({"type": "unresolved", "source_excerpt": clause, "candidate": None,
                            "reason": "NUMERIC_OUT_OF_DOMAIN"})
                continue
            spec = {"availability_below_percent": str(availability), "credit_percent": str(rate),
                    "exclude_scheduled_maintenance": True, "period": "calendar_month",
                    "requires_facts": ["period_minutes", "outage_minutes", "scheduled_maintenance_minutes", "monthly_fee_eur"]}
            typ = "service_credit"
        else:
            spec = {"threshold_eur": str(as_decimal(m.group("limit"))),
                    "approver": m.group("approver").strip(), "comparison": "strictly_above"}
            typ = "credit_approval_policy"
        out.append({"type": typ, "source_excerpt": clause, "candidate": spec, "reason": None})
    return out


class Store:
    def __init__(self, filename: str | Path):
        self.db = sqlite3.connect(str(filename), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY, doc_key TEXT NOT NULL, version INTEGER NOT NULL,
                kind TEXT NOT NULL, source_text TEXT NOT NULL, source_sha256 TEXT NOT NULL,
                effective_from TEXT NOT NULL, observed_at TEXT NOT NULL,
                approved_at TEXT, approved_by TEXT,
                UNIQUE(doc_key, version)
            );
            CREATE TABLE IF NOT EXISTS clauses (
                id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES documents(id),
                clause_index INTEGER NOT NULL, kind TEXT NOT NULL,
                excerpt TEXT NOT NULL, proposed_spec TEXT, unresolved_reason TEXT,
                UNIQUE(document_id, clause_index)
            );
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY, happened_at TEXT NOT NULL,
                event TEXT NOT NULL, payload_json TEXT NOT NULL
            );
        """)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def _audit(self, event: str, payload: dict) -> None:
        # Exclude raw contracts and sensitive operational facts from event payloads.
        self.db.execute("INSERT INTO audit(happened_at,event,payload_json) VALUES(?,?,?)",
                        (now(), event, json.dumps(payload, sort_keys=True)))

    def ingest(self, payload: dict) -> dict:
        key = payload.get("doc_key")
        kind = payload.get("kind")
        text = payload.get("text")
        if not isinstance(key, str) or not re.fullmatch(r"[a-zA-Z0-9/_-]{1,120}", key):
            raise ValueError("doc_key must be a stable 1-120 character identifier")
        if kind not in ("customer_contract", "internal_policy"):
            raise ValueError("kind must be customer_contract or internal_policy")
        if not isinstance(text, str) or not text.strip() or len(text) > 100_000:
            raise ValueError("text must be nonempty and at most 100k characters")
        effective = ymd(payload.get("effective_from", ""))
        clauses = parse_clauses(text, kind)
        if not clauses:
            raise ValueError("no clauses")
        with self.db:
            v = self.db.execute("SELECT COALESCE(MAX(version),0)+1 FROM documents WHERE doc_key=?", (key,)).fetchone()[0]
            stamp = now()
            cur = self.db.execute("""INSERT INTO documents
                (doc_key, version, kind, source_text, source_sha256, effective_from, observed_at)
                VALUES (?,?,?,?,?,?,?)""",
                (key, v, kind, text, hashlib.sha256(text.encode()).hexdigest(), effective, stamp))
            doc_id = cur.lastrowid
            for i, c in enumerate(clauses, 1):
                self.db.execute("""INSERT INTO clauses
                    (document_id, clause_index, kind, excerpt, proposed_spec, unresolved_reason)
                    VALUES (?,?,?,?,?,?)""",
                    (doc_id, i, c["type"], c["source_excerpt"],
                     json.dumps(c["candidate"], sort_keys=True) if c["candidate"] else None, c["reason"]))
            self._audit("DOCUMENT_INGESTED", {"document_id": doc_id, "doc_key": key, "version": v,
                                                 "candidate_count": sum(c["candidate"] is not None for c in clauses),
                                                 "unresolved_count": sum(c["candidate"] is None for c in clauses)})
        return self.get_document(doc_id)

    def get_document(self, doc_id: int) -> dict:
        row = self.db.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        if row is None:
            raise LookupError("unknown document")
        rules = self.db.execute("SELECT * FROM clauses WHERE document_id=? ORDER BY clause_index", (doc_id,)).fetchall()
        return {"id": row["id"], "doc_key": row["doc_key"], "version": row["version"],
                "kind": row["kind"], "source_sha256": row["source_sha256"],
                "effective_from": row["effective_from"], "observed_at": row["observed_at"],
                "approval_state": "LAB_APPROVED_SIMULATED" if row["approved_at"] else "PROPOSED_NOT_APPROVED",
                "approved_at": row["approved_at"], "approved_by_claimed": row["approved_by"],
                "clauses": [{"clause_id": r["id"], "kind": r["kind"], "source_excerpt": r["excerpt"],
                             "candidate": json.loads(r["proposed_spec"]) if r["proposed_spec"] else None,
                             "unresolved_reason": r["unresolved_reason"]} for r in rules],
                "scope": "LAB_ONLY; unauthenticated approval, unverified source authority"}

    def approve(self, doc_id: int, reviewer: str) -> dict:
        # Simulation only: no real authentication/authority, intentionally never says LEGALLY_APPROVED.
        if not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 120:
            raise ValueError("nonempty reviewer label required")
        record = self.get_document(doc_id)
        if all(c["candidate"] is None for c in record["clauses"]):
            raise ValueError("no supported candidate to approve; unresolved clauses cannot be auto-authorized")
        with self.db:
            row = self.db.execute("SELECT approved_at FROM documents WHERE id=?", (doc_id,)).fetchone()
            if row["approved_at"] is not None:
                raise ValueError("document already approved")
            self.db.execute("UPDATE documents SET approved_at=?,approved_by=? WHERE id=?",
                            (now(), reviewer.strip(), doc_id))
            self._audit("LAB_APPROVAL_RECORDED", {"document_id": doc_id,
                                                  "reviewer_claimed": reviewer.strip(),
                                                  "unresolved_count": sum(c["candidate"] is None for c in record["clauses"])})
        return self.get_document(doc_id)

    def active(self, key: str, kind: str, effective_on: str, known_at: str | None) -> dict | None:
        # Version routing by BOTH effective date and knowledge/approval time.
        q = """SELECT id FROM documents WHERE doc_key=? AND kind=? AND approved_at IS NOT NULL
               AND effective_from<=?"""
        args: list[Any] = [key, kind, effective_on]
        if known_at is not None:
            stamp = datetime.fromisoformat(known_at.replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("known_at must include timezone (e.g., Z)")
            q += " AND approved_at<=?"
            args.append(stamp.astimezone(timezone.utc).isoformat(timespec="microseconds"))
        q += " ORDER BY effective_from DESC, version DESC LIMIT 1"
        r = self.db.execute(q, args).fetchone()
        return self.get_document(r["id"]) if r else None

    def assess(self, req: dict) -> dict:
        contract_key, policy_key = req.get("contract_key"), req.get("policy_key")
        if not isinstance(contract_key, str) or not isinstance(policy_key, str):
            raise ValueError("contract_key and policy_key required")
        effective_on = ymd(req.get("on_date", date.today().isoformat()))
        known_at = req.get("known_at")
        contract = self.active(contract_key, "customer_contract", effective_on, known_at)
        policy = self.active(policy_key, "internal_policy", effective_on, known_at)
        baseline = {"execution_authorized": False, "implementation": "advisory_only_no_action_tool",
                    "facts_provenance": "SUPPLIED_BY_CALLER_NOT_INDEPENDENTLY_VERIFIED",
                    "effective_on": effective_on, "known_at": known_at,
                    "contract_version": contract["version"] if contract else None,
                    "policy_version": policy["version"] if policy else None,
                    "source_refs": [], "unresolved": []}
        if contract is None or policy is None:
            return {**baseline, "status": "NOT_VERIFIED", "reason": "MISSING_APPROVED_APPLICABLE_DOCUMENT"}
        baseline["source_refs"] = [{"doc_key": d["doc_key"], "version": d["version"],
                                    "sha256": d["source_sha256"], "clause_id": c["clause_id"],
                                    "excerpt": c["source_excerpt"]}
                                   for d in (contract, policy) for c in d["clauses"]]
        baseline["unresolved"] = [{"doc_key": d["doc_key"], "excerpt": c["source_excerpt"],
                                   "reason": c["unresolved_reason"]}
                                  for d in (contract, policy) for c in d["clauses"] if c["unresolved_reason"]]
        if baseline["unresolved"]:
            return {**baseline, "status": "UNRESOLVED", "reason": "UNMODELED_GOVERNING_LANGUAGE"}
        cs = [x["candidate"] for x in contract["clauses"] if x["kind"] == "service_credit"]
        ps = [x["candidate"] for x in policy["clauses"] if x["kind"] == "credit_approval_policy"]
        if len(cs) != 1 or len(ps) != 1:
            return {**baseline, "status": "UNRESOLVED", "reason": "UNSUPPORTED_OR_MULTIPLE_RULES"}
        spec, approval = cs[0], ps[0]
        facts = req.get("facts", {})
        if not isinstance(facts, dict):
            raise ValueError("facts must be an object")
        missing = [x for x in spec["requires_facts"] if x not in facts]
        if missing:
            return {**baseline, "status": "NEEDS_FACTS", "required_fields": missing}
        period, outage, planned, fee = (as_decimal(facts[f]) for f in spec["requires_facts"])
        if period <= 0 or outage > period or planned > outage:
            raise ValueError("period must be positive; 0 <= scheduled <= outage <= period")
        availability = Decimal("100") * (period - (outage - planned)) / period
        eligible = availability < Decimal(spec["availability_below_percent"])
        credit = fee * Decimal(spec["credit_percent"]) / Decimal("100") if eligible else Decimal("0")
        review = ("FOUNDER_APPROVAL_REQUIRED" if credit > Decimal(approval["threshold_eur"])
                  else "NO_EXTRA_THRESHOLD_APPROVAL_SPECIFIED")
        outcome = {**baseline, "status": "CREDIT_PROPOSABLE" if eligible else "NO_CREDIT_UNDER_MODELED_RULE",
                   "availability_percent": str(availability.quantize(Decimal("0.0001"))),
                   "credit_eur": money(credit), "approval_route": review,
                   "approver": approval["approver"] if review == "FOUNDER_APPROVAL_REQUIRED" else None,
                   "note": "Advisory calculation from caller-supplied facts; no legally binding or payment decision"}
        with self.db:
            self._audit("ASSESSMENT", {"contract_key": contract_key, "policy_key": policy_key,
                                       "on_date": effective_on, "status": outcome["status"],
                                       "contract_version": contract["version"], "policy_version": policy["version"]})
        return outcome

    def audit(self) -> list[dict]:
        return [{"id": r["id"], "timestamp": r["happened_at"], "event": r["event"],
                 "details": json.loads(r["payload_json"])}
                for r in self.db.execute("SELECT * FROM audit ORDER BY id")]


def make_server(store: Store, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    if host not in ("127.0.0.1", "localhost"):
        raise ValueError("V0 is unauthenticated: bind to loopback only")

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, data: dict | list) -> None:
            b = json.dumps(data, indent=2).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_POST(self) -> None:
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= 120_000:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(n))
                if not isinstance(payload, dict):
                    raise ValueError("JSON object required")
                if self.path == "/documents":
                    response = store.ingest(payload)
                elif self.path == "/approve":
                    response = store.approve(int(payload["document_id"]), payload["reviewer"])
                elif self.path == "/assess":
                    response = store.assess(payload)
                else:
                    return self._send(404, {"error": "unknown route"})
                self._send(200, response)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
                self._send(400, {"error": str(e)})
            except LookupError as e:
                self._send(404, {"error": str(e)})

        def do_GET(self) -> None:
            if self.path == "/health":
                return self._send(200, {"status": "ok", "scope": "LAB_ONLY"})
            if self.path == "/audit":
                return self._send(200, store.audit())
            self._send(404, {"error": "unknown route"})

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["serve"])
    p.add_argument("--db", default=".sophon-v0.sqlite")
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args()
    store = Store(a.db)
    server = make_server(store, port=a.port)
    print(f"Sophon V0 LAB ONLY: http://127.0.0.1:{a.port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        store.close()


if __name__ == "__main__":
    main()
