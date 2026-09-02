from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAuthBrandingPreset(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env["auth.branding.config"]._get_or_create_config()
        cls.system_preset = cls.env.ref("auth_branding.preset_corporate_blue")

    def test_system_preset_applies_to_config(self):
        self.system_preset.apply_preset(self.config.id)
        self.assertEqual(self.config.template, "split")
        self.assertEqual(self.config.primary_color, "#2563EB")
        self.assertEqual(self.config.background_type, "gradient")

    def test_create_custom_preset_from_config(self):
        self.config.primary_color = "#123456"
        preset_id = self.env["auth.branding.preset"].create_from_config(
            self.config.id, "My Company Theme"
        )
        preset = self.env["auth.branding.preset"].browse(preset_id)
        self.assertFalse(preset.is_system)
        self.assertEqual(preset.company_id, self.config.company_id)
        self.assertEqual(preset.primary_color, "#123456")

    def test_system_preset_is_protected(self):
        with self.assertRaises(UserError):
            self.system_preset.write({"name": "Changed"})
        with self.assertRaises(UserError):
            self.system_preset.unlink()

    def test_custom_preset_can_be_deleted(self):
        preset_id = self.env["auth.branding.preset"].create_from_config(
            self.config.id, "Disposable Theme"
        )
        preset = self.env["auth.branding.preset"].browse(preset_id)
        preset.unlink()
        self.assertFalse(preset.exists())

    def test_preset_color_validation(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.env["auth.branding.preset"].create(
                {"name": "Unsafe", "primary_color": "red; color: black"}
            )
