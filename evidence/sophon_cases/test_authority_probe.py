import unittest
from authority_probe import probe


class PublicAuthorityBoundaries(unittest.TestCase):
    def test_named_exception_does_not_transfer_to_another_person(self):
        self.assertEqual(probe("OTHER_MP", "personal_effects_storage", "2024-02-01")["status"], "REQUEST_AUTHORITY")

    def test_expired_exception_does_not_authorize_new_period(self):
        self.assertEqual(probe("COM-1613", "personal_effects_storage", "2024-04-01")["status"], "REQUEST_AUTHORITY")

    def test_in_window_document_does_not_clear_payment(self):
        self.assertEqual(probe("COM-1613", "personal_effects_storage", "2024-02-01")["status"], "AUTHORITY_EVIDENCE_ONLY")

    def test_announcement_does_not_create_general_guidance(self):
        self.assertEqual(probe("OTHER_MP", "festive_hospitality", "2025-05-01")["status"], "REQUEST_AUTHORITY")

    def test_review_decision_does_not_grant_repeat_claim(self):
        self.assertEqual(probe("OTHER_MP", "electricity_bill_partial", "2025-01-01")["status"], "REQUEST_AUTHORITY")

    def test_expressly_non_precedential_half_funding_does_not_spread(self):
        self.assertEqual(probe("OTHER_MP", "mixed_content_newsletter", "2025-07-01")["status"], "REQUEST_AUTHORITY")


if __name__ == "__main__":
    unittest.main()
