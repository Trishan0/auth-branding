import base64
import json

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAuthBrandingImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env["auth.branding.config"]._get_or_create_config()

    def _wizard_for_payload(self, payload):
        return self.env["auth.branding.import.wizard"].create(
            {
                "config_id": self.config.id,
                "import_file": base64.b64encode(json.dumps(payload).encode()),
                "import_filename": "brand.json",
            }
        )

    def test_export_review_and_apply_as_draft(self):
        self.config.write(
            {
                "primary_color": "#123456",
                "tagline": "Portable brand",
                "company_logo": base64.b64encode(b"logo"),
            }
        )
        payload = self.config._get_export_payload()
        self.config.write(
            {"primary_color": "#654321", "tagline": False, "company_logo": False}
        )

        wizard = self._wizard_for_payload(payload)
        wizard.action_review()
        self.assertEqual(wizard.state, "review")
        self.assertIn("Settings ready to import", wizard.import_summary)
        wizard.action_apply()

        self.assertEqual(self.config.primary_color, "#123456")
        self.assertEqual(self.config.tagline, "Portable brand")
        self.assertTrue(self.config.company_logo)
        self.assertTrue(self.config.has_unpublished_changes)
        self.assertNotEqual(
            self.config._get_frontend_values()["primary_color"], "#123456"
        )

    def test_import_rejects_unknown_format(self):
        wizard = self._wizard_for_payload({"format": "other", "schema_version": 1})
        with self.assertRaises(UserError):
            wizard.action_review()
