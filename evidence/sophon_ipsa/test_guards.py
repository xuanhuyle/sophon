"""Run: python -m unittest discover -s sophon_ipsa -p 'test_*.py'"""
import unittest

from replay import decide


class AuthorityGuards(unittest.TestCase):
    def test_published_status_cannot_grant_clearance(self):
        features = {"Category": "Office Costs", "Cost Type": "Software & applications"}
        paid = decide({**features, "Status": "Paid", "Amount Paid": "100.00"})
        refused = decide({**features, "Status": "Not Paid", "Amount Paid": "0.00"})
        self.assertEqual(paid, refused)
        self.assertEqual(paid["decision"], "REQUEST_FACT")
        self.assertIn("certified_parliamentary_purpose", paid["missing_facts"])

    def test_known_category_still_needs_underlying_evidence(self):
        decision = decide({"Category": "MP Travel", "Cost Type": "Rail"})
        self.assertEqual(decision["decision"], "REQUEST_FACT")
        self.assertIn("comparable_permitted_fare_at_booking", decision["missing_facts"])


if __name__ == "__main__":
    unittest.main()
