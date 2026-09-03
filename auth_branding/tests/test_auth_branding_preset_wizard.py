from odoo.tests.common import TransactionCase


class TestAuthBrandingPresetWizard(TransactionCase):
    def test_save_current_visual_settings_as_custom_theme(self):
        config = self.env["auth.branding.config"]._get_or_create_config()
        config.write(
            {
                "template": "sidebar",
                "dark_mode": "on",
                "social_button_style": "pill",
                "primary_color": "#123456",
                "custom_css": ".oe_login_form { max-width: 29rem; }",
            }
        )
        wizard = self.env["auth.branding.preset.wizard"].create(
            {
                "config_id": config.id,
                "name": "Night Campaign",
                "description": "A reusable dark theme",
            }
        )
        wizard.action_save()

        preset = self.env["auth.branding.preset"].search(
            [("name", "=", "Night Campaign")], limit=1
        )
        self.assertTrue(preset)
        self.assertFalse(preset.is_system)
        self.assertEqual(preset.company_id, config.company_id)
        self.assertEqual(preset.template, "sidebar")
        self.assertEqual(preset.dark_mode, "on")
        self.assertEqual(preset.social_button_style, "pill")
        self.assertEqual(preset.custom_css, ".oe_login_form { max-width: 29rem; }")
