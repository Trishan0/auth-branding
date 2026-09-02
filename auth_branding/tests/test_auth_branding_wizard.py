import base64
from io import BytesIO

from PIL import Image

from odoo.tests.common import TransactionCase

from ..models.auth_branding_color_utils import extract_logo_palette


class TestAuthBrandingWizard(TransactionCase):
    @staticmethod
    def _test_logo():
        image = Image.new("RGB", (100, 100), "#CC2200")
        for x in range(70, 100):
            for y in range(100):
                image.putpixel((x, y), (0, 68, 204))
        output = BytesIO()
        image.save(output, format="PNG")
        return base64.b64encode(output.getvalue())

    def test_logo_palette_extraction(self):
        palette = extract_logo_palette(self._test_logo())
        self.assertTrue(palette)
        self.assertRegex(palette[0], r"^#[0-9A-F]{6}$")
        self.assertEqual(len(palette), 2)

    def test_wizard_suggests_logo_colors_and_applies(self):
        config = self.env["auth.branding.config"]._get_or_create_config()
        wizard = self.env["auth.branding.wizard"].create(
            {"config_id": config.id, "company_logo": self._test_logo()}
        )
        wizard._onchange_company_logo()
        self.assertTrue(wizard.suggested_primary_color)
        self.assertEqual(wizard.button_color, wizard.suggested_primary_color)

        wizard.tagline = "A guided welcome"
        wizard.template = "split"
        wizard.action_apply()
        self.assertEqual(config.tagline, "A guided welcome")
        self.assertEqual(config.template, "split")
        self.assertEqual(config.primary_color, wizard.primary_color)

    def test_open_wizard_carries_current_configuration(self):
        config = self.env["auth.branding.config"]._get_or_create_config()
        config.write({"primary_color": "#123456", "template": "fullbleed"})
        action = config.action_open_setup_wizard()
        self.assertEqual(action["res_model"], "auth.branding.wizard")
        self.assertEqual(action["context"]["default_primary_color"], "#123456")
        self.assertEqual(action["context"]["default_template"], "fullbleed")
