import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sophon_v0 import Store, make_server

CONTRACT_1 = ("If monthly service availability falls below 99.5%, the customer is entitled to "
              "a service credit of 5% of the monthly subscription fee, excluding scheduled maintenance.")
CONTRACT_2 = CONTRACT_1.replace("5% of the monthly", "10% of the monthly")
POLICY = "Service credits above EUR 30 require founder approval."
FACTS = {"period_minutes": 43200, "outage_minutes": 300, "scheduled_maintenance_minutes": 0,
         "monthly_fee_eur": "400"}


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "test.sqlite")
        self.server = make_server(self.store, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.store.close()
        self.tmp.cleanup()

    def call(self, route, body):
        req = Request(self.url + route, json.dumps(body).encode(),
                      {"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=3) as rsp:
            return json.load(rsp)

    def ingest(self, key, kind, text, effective="2026-01-01"):
        return self.call("/documents", {"doc_key": key, "kind": kind, "text": text,
                                        "effective_from": effective})

    def approve(self, document):
        return self.call("/approve", {"document_id": document["id"], "reviewer": "LAB founder"})

    def assess(self, **changes):
        p = {"contract_key": "customers/acme", "policy_key": "policies/credits",
             "on_date": "2026-10-12", "facts": FACTS}
        p.update(changes)
        return self.call("/assess", p)

    def seed(self):
        d1 = self.ingest("customers/acme", "customer_contract", CONTRACT_1)
        p = self.ingest("policies/credits", "internal_policy", POLICY)
        self.approve(d1)
        self.approve(p)
        return d1

    def test_end_to_end_amendment_both_agents_no_reprogramming(self):
        self.seed()
        support_result = self.assess()
        billing_result = self.assess()
        self.assertEqual(support_result["credit_eur"], "20.00")
        self.assertEqual(support_result["contract_version"], 1)
        self.assertEqual(support_result["status"], "CREDIT_PROPOSABLE")
        self.assertEqual(billing_result["credit_eur"], "20.00")
        self.assertFalse(support_result["execution_authorized"])
        self.assertEqual(support_result["approval_route"], "NO_EXTRA_THRESHOLD_APPROVAL_SPECIFIED")
        amendment = self.ingest("customers/acme", "customer_contract", CONTRACT_2)
        self.assertEqual(amendment["approval_state"], "PROPOSED_NOT_APPROVED")
        self.assertEqual(self.assess()["credit_eur"], "20.00")  # no unapproved propagation
        before_approval = self.store.active("customers/acme", "customer_contract", "2026-10-12", None)
        self.approve(amendment)
        # As-known query before the amendment was even observed cannot see v2.
        historical = self.assess(known_at=amendment["observed_at"])
        self.assertEqual(historical["contract_version"], 1)
        after_approval = self.assess()
        self.assertEqual(after_approval["credit_eur"], "40.00")
        self.assertEqual(after_approval["approval_route"], "FOUNDER_APPROVAL_REQUIRED")
        self.assertEqual(after_approval["contract_version"], 2)
        self.assertEqual(before_approval["version"], 1)
        self.assertEqual(self.assess()["credit_eur"], "40.00")  # second client same API
        self.assertIn("source_refs", after_approval)
        self.assertTrue(any(x["event"] == "LAB_APPROVAL_RECORDED" for x in self.store.audit()))

    def test_unrecognized_clause_and_missing_evidence_abstain(self):
        d = self.ingest("customers/acme", "customer_contract", CONTRACT_1 + "\nAct reasonably in all cases.")
        p = self.ingest("policies/credits", "internal_policy", POLICY)
        self.approve(d)
        self.approve(p)
        res = self.assess()
        self.assertEqual(res["status"], "UNRESOLVED")
        self.assertEqual(len(res["unresolved"]), 1)
        self.assertFalse(res["execution_authorized"])
        self.assertIn("Act reasonably", res["unresolved"][0]["excerpt"])
        self.assertEqual(self.assess(facts={})["status"], "UNRESOLVED")

    def test_reuse_with_second_customer_without_contract_specific_code(self):
        self.seed()
        second = self.ingest("customers/zephyr", "customer_contract",
                             CONTRACT_1.replace("99.5%", "99.9%").replace("5% of", "7.5% of"))
        self.approve(second)
        out = self.assess(contract_key="customers/zephyr")
        self.assertEqual(out["status"], "CREDIT_PROPOSABLE")
        self.assertEqual(out["credit_eur"], "30.00")
        self.assertEqual(out["contract_version"], 1)

    def test_missing_policy_and_missing_facts(self):
        d = self.ingest("customers/acme", "customer_contract", CONTRACT_1)
        self.approve(d)
        self.assertEqual(self.assess()["status"], "NOT_VERIFIED")
        p = self.ingest("policies/credits", "internal_policy", POLICY)
        self.approve(p)
        self.assertEqual(self.assess(facts={})["status"], "NEEDS_FACTS")
        self.assertFalse(self.assess(facts={})["execution_authorized"])

    def test_effective_date_and_previous_version_preserved(self):
        self.seed()
        d2 = self.ingest("customers/acme", "customer_contract", CONTRACT_2, effective="2027-01-01")
        self.approve(d2)
        self.assertEqual(self.assess(on_date="2026-10-12")["credit_eur"], "20.00")
        self.assertEqual(self.assess(on_date="2027-01-02")["credit_eur"], "40.00")

    def test_no_claimed_enforcement_and_invalid_facts_fail(self):
        self.seed()
        res = self.assess()
        self.assertEqual(res["facts_provenance"], "SUPPLIED_BY_CALLER_NOT_INDEPENDENTLY_VERIFIED")
        self.assertFalse(res["execution_authorized"])
        with self.assertRaises(Exception):
            self.assess(facts={**FACTS, "outage_minutes": 100000})
        self.assertEqual(len(self.store.audit()) > 0, True)


if __name__ == "__main__":
    unittest.main()
