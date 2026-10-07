from odoo.tests import HttpCase, tagged


WAIT_FOR_JS = """
    const waitFor = async (selector, root = document) => {
        for (let attempt = 0; attempt < 100; attempt++) {
            const element = root.querySelector(selector);
            if (element) {
                return element;
            }
            await new Promise((resolve) => setTimeout(resolve, 100));
        }
        throw new Error(`Element not found: ${selector}`);
    };
"""


@tagged("post_install", "-at_install")
class TestAuthBrandingUi(HttpCase):
    def test_brand_studio_widgets_render_and_apply_preset(self):
        config = self.env["auth.branding.config"]._get_or_create_config()
        config.primary_color = "#714B67"
        preset = self.env.ref("auth_branding.preset_corporate_blue")
        code = WAIT_FOR_JS + """
            (async () => {
                await waitFor(".ab-design-health");
                await waitFor(".ab-preview-iframe[src*='/auth_branding/preview']");
                await waitFor(".ab-preset-card");
                const card = [...document.querySelectorAll(".ab-preset-card")].find(
                    (element) => element.textContent.includes("%s")
                );
                if (!card) {
                    throw new Error("Preset card not rendered");
                }
                card.click();
                await waitFor(".ab-preset-card.is-selected");

                (await waitFor(".o_notebook .nav-link[name='brand']")).click();
                const colorInput = await waitFor(
                    "div[name='primary_color'] .ab-color-field input[type=color]"
                );
                if (colorInput.value.toLowerCase() !== "#2563eb") {
                    throw new Error(`Preset not applied to the record: ${colorInput.value}`);
                }

                (await waitFor(".o_notebook .nav-link[name='layout']")).click();
                await waitFor(".ab-template-card.active");

                // Applying a preset only changes the unsaved draft: discard it.
                (await waitFor(".o_form_button_cancel")).click();
                for (let attempt = 0; document.querySelector(".o_form_dirty"); attempt++) {
                    if (attempt > 50) {
                        throw new Error("Form changes were not discarded");
                    }
                    await new Promise((resolve) => setTimeout(resolve, 100));
                }
                console.log("test successful");
            })().catch((error) => console.error(error.message));
        """ % preset.name
        self.browser_js(
            f"/odoo/auth.branding.config/{config.id}", code, login="admin", timeout=120
        )

    def test_login_page_renders_without_javascript_errors(self):
        self.browser_js(
            "/web/login",
            WAIT_FOR_JS + """
                waitFor("body.ab-template-centered .oe_login_form")
                    .then(() => console.log("test successful"))
                    .catch((error) => console.error(error.message));
            """,
        )
