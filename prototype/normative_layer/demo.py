"""Complete walking-skeleton demonstration: two independent clients, live version propagation."""
import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from sophon_v0 import Store, make_server

HERE = Path(__file__).resolve().parent
CONTRACT = ("If monthly service availability falls below 99.5%, the customer is entitled to "
            "a service credit of 5% of the monthly subscription fee, excluding scheduled maintenance.")
POLICY = "Service credits above EUR 30 require founder approval."
FACTS = {"period_minutes": 43200, "outage_minutes": 300, "scheduled_maintenance_minutes": 0,
         "monthly_fee_eur": "400"}


def main():
    with tempfile.TemporaryDirectory() as root:
        db = Store(Path(root) / "lab.sqlite")
        server = make_server(db, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"

        def post(endpoint, data):
            req = Request(base + endpoint, json.dumps(data).encode(), {"Content-Type": "application/json"})
            with urlopen(req, timeout=5) as response:
                return json.load(response)

        def run_clients(label):
            print("\n===", label, "===", flush=True)
            for client in ("support_agent.py", "billing_agent.py"):
                args = [sys.executable, str(HERE / client), "--base", base,
                        "--contract-key", "customers/acme", "--policy-key", "policies/credits",
                        "--facts", json.dumps(FACTS)]
                print(subprocess.check_output(args, text=True).strip(), flush=True)

        try:
            c1 = post("/documents", {"doc_key": "customers/acme", "kind": "customer_contract",
                                     "effective_from": "2026-01-01", "text": CONTRACT})
            p1 = post("/documents", {"doc_key": "policies/credits", "kind": "internal_policy",
                                     "effective_from": "2026-01-01", "text": POLICY})
            for doc in (c1, p1):
                post("/approve", {"document_id": doc["id"], "reviewer": "LAB founder (self asserted)"})
            run_clients("approved contract v1")
            c2 = post("/documents", {"doc_key": "customers/acme", "kind": "customer_contract",
                                     "effective_from": "2026-01-01",
                                     "text": CONTRACT.replace("5% of the monthly", "10% of the monthly")})
            run_clients("v2 ingested but NOT approved: both still use v1")
            post("/approve", {"document_id": c2["id"], "reviewer": "LAB founder (self asserted)"})
            run_clients("v2 LAB-approved: both change with NO code edits")
            print("\nAudit events:", len(db.audit()), "(saved in SQLite during run)")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
            db.close()


if __name__ == "__main__":
    main()
