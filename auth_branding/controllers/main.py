import urllib.parse
from odoo import http
from odoo.http import request

class AuthBrandingController(http.Controller):

    @http.route('/auth_branding/preview', type='http', auth='user', website=True)
    def preview(self, page='login', **kwargs):
        # Fetch config
        company_id = int(kwargs.get('company_id', 0))
        config = request.env['auth.branding.config'].sudo().get_or_create(company_id=company_id)
        
        # Merge saved config with kwargs overrides for live preview
        ab_config = {
            'company_id': config.company_id.id,
            'template': kwargs.get('template', config.template),
            'tagline': kwargs.get('tagline', config.tagline or ''),
            'primary_color': kwargs.get('primary_color', config.primary_color),
            'secondary_color': kwargs.get('secondary_color', config.secondary_color),
            'background_type': kwargs.get('background_type', config.background_type),
            'background_color': kwargs.get('background_color', config.background_color),
            'gradient_start': kwargs.get('gradient_start', config.gradient_start),
            'gradient_end': kwargs.get('gradient_end', config.gradient_end),
            'gradient_direction': kwargs.get('gradient_direction', config.gradient_direction),
            'background_overlay_opacity': kwargs.get('background_overlay_opacity', str(config.background_overlay_opacity)),
            'font_family': kwargs.get('font_family', config.font_family),
            'text_color': kwargs.get('text_color', config.text_color),
            'input_border_radius': kwargs.get('input_border_radius', str(config.input_border_radius)),
            'button_border_radius': kwargs.get('button_border_radius', str(config.button_border_radius)),
            'button_color': kwargs.get('button_color', config.button_color),
            'button_text_color': kwargs.get('button_text_color', config.button_text_color),
            'show_manage_databases': kwargs.get('show_manage_databases') == 'true' if 'show_manage_databases' in kwargs else config.show_manage_databases,
            'show_powered_by_odoo': kwargs.get('show_powered_by_odoo') == 'true' if 'show_powered_by_odoo' in kwargs else config.show_powered_by_odoo,
            'split_alignment': kwargs.get('split_alignment', config.split_alignment or 'left'),
            'card_background_color': kwargs.get('card_background_color', config.card_background_color or '#FFFFFF'),
            'glassmorphism': kwargs.get('glassmorphism') == 'true' if 'glassmorphism' in kwargs else config.glassmorphism,
            'glassmorphism_blur': kwargs.get('glassmorphism_blur', str(config.glassmorphism_blur)),
            'glassmorphism_opacity': kwargs.get('glassmorphism_opacity', str(config.glassmorphism_opacity)),
            'custom_footer_text': kwargs.get('custom_footer_text', config.custom_footer_text or ''),
            'login_welcome_title': kwargs.get('login_welcome_title', config.login_welcome_title or ''),
            'login_welcome_subtitle': kwargs.get('login_welcome_subtitle', config.login_welcome_subtitle or ''),
            'terms_url': kwargs.get('terms_url', config.terms_url or ''),
            'privacy_url': kwargs.get('privacy_url', config.privacy_url or ''),
            'terms_label': kwargs.get('terms_label', config.terms_label or 'Terms of Service'),
            'privacy_label': kwargs.get('privacy_label', config.privacy_label or 'Privacy Policy'),
            'auth_signup_uninvited': kwargs.get('auth_signup_uninvited', config.auth_signup_uninvited),
            'auth_signup_reset_password': kwargs.get('auth_signup_reset_password') == 'true' if 'auth_signup_reset_password' in kwargs else config.auth_signup_reset_password,
            'is_preview': True,
        }
        
        font_map = {
            'system-ui': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'Inter': '"Inter", sans-serif',
            'Roboto': '"Roboto", sans-serif',
            'Open Sans': '"Open Sans", sans-serif',
            'Lato': '"Lato", sans-serif',
            'Poppins': '"Poppins", sans-serif',
            'Georgia': 'Georgia, serif',
        }
        ab_config['font_family_css'] = font_map.get(ab_config['font_family'], font_map['system-ui'])
        
        # Background logic for preview
        bg_css = ""
        bg_type = ab_config['background_type']
        if bg_type == 'solid':
            bg_css = f"background: {ab_config['background_color'] or '#f8f9fa'} !important;"
        elif bg_type == 'gradient':
            bg_css = f"background: linear-gradient({ab_config['gradient_direction'] or 'to bottom right'}, {ab_config['gradient_start'] or '#714B67'}, {ab_config['gradient_end'] or '#2B124C'}) !important;"
        elif bg_type == 'animated_gradient':
            bg_css = f"background: linear-gradient(-45deg, {ab_config['gradient_start'] or '#714B67'}, {ab_config['gradient_end'] or '#2B124C'}, {ab_config['primary_color'] or '#714B67'}) !important; background-size: 400% 400% !important; animation: abGradientAnim 15s ease infinite !important;"
        elif bg_type == 'image':
            # Rely on saved image, we can't preview image blob directly from iframe unless we base64 it
            bg_css = f"background: url('/auth_branding/image/background_image?company_id={ab_config['company_id']}') no-repeat center center fixed !important; background-size: cover !important;"

        # Build inline styles using the overrides to inject into the template
        inline_style = f"""
        @keyframes abGradientAnim {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        :root {{
            --ab-primary: {ab_config['primary_color'] or '#714B67'};
            --ab-secondary: {ab_config['secondary_color'] or '#FFFFFF'};
            --ab-overlay-opacity: {ab_config['background_overlay_opacity'] or '0.3'};
            --ab-font: {ab_config['font_family_css']};
            --ab-text-color: {ab_config['text_color'] or '#212529'};
            --ab-card-bg: {ab_config['card_background_color'] or '#FFFFFF'};
            --ab-glass-blur: {ab_config['glassmorphism_blur'] or '10'}px;
            --ab-glass-opacity: {ab_config['glassmorphism_opacity'] or '0.2'};
            --ab-input-radius: {ab_config['input_border_radius'] or '6'}px;
            --ab-btn-radius: {ab_config['button_border_radius'] or '6'}px;
            --ab-btn-color: {ab_config['button_color'] or '#714B67'};
            --ab-btn-text: {ab_config['button_text_color'] or '#FFFFFF'};
        }}
        body.ab-template-centered, body.ab-template-fullbleed {{
            {bg_css}
        }}
        body.ab-template-split .ab-split-aside {{
            {bg_css}
        }}
        """
        ab_config['inline_style'] = inline_style
        
        # Inject the preview config into context so QWeb can access it safely
        request.env = request.env(context=dict(request.env.context, ab_preview_config=ab_config))
        
        qcontext = {
            'error': False,
            'message': False,
            'login': 'admin',
            'redirect': '',
            'providers': [],
            'signup_enabled': ab_config['auth_signup_uninvited'] == 'b2c',
            'reset_password_enabled': ab_config['auth_signup_reset_password'],
            'token': False,
        }
        
        template = 'web.login'
        if page == 'signup':
            template = 'auth_signup.signup'
        elif page == 'reset':
            template = 'auth_signup.reset_password'
            
        return request.render(template, qcontext)

    @http.route('/auth_branding/theme.css', type='http', auth='public')
    def theme_css(self, **kwargs):
        company_id = int(kwargs.get('company_id', 0))
        config = request.env['auth.branding.config'].sudo().get_or_create(company_id=company_id)
        
        font_map = {
            'system-ui': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'Inter': '"Inter", sans-serif',
            'Roboto': '"Roboto", sans-serif',
            'Open Sans': '"Open Sans", sans-serif',
            'Lato': '"Lato", sans-serif',
            'Poppins': '"Poppins", sans-serif',
            'Georgia': 'Georgia, serif',
        }
        
        # Background logic
        bg_css = ""
        if config.background_type == 'solid':
            bg_css = f"background: {config.background_color or '#f8f9fa'} !important;"
        elif config.background_type == 'gradient':
            bg_css = f"background: linear-gradient({config.gradient_direction or 'to bottom right'}, {config.gradient_start or '#714B67'}, {config.gradient_end or '#2B124C'}) !important;"
        elif config.background_type == 'animated_gradient':
            bg_css = f"background: linear-gradient(-45deg, {config.gradient_start or '#714B67'}, {config.gradient_end or '#2B124C'}, {config.primary_color or '#714B67'}) !important; background-size: 400% 400% !important; animation: abGradientAnim 15s ease infinite !important;"
        elif config.background_type == 'image':
            bg_css = f"background: url('/auth_branding/image/background_image?company_id={config.company_id.id}') no-repeat center center fixed !important; background-size: cover !important;"
            
        css = f"""
@keyframes abGradientAnim {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
:root {{
    --ab-primary: {config.primary_color or '#714B67'};
    --ab-secondary: {config.secondary_color or '#FFFFFF'};
    --ab-overlay-opacity: {config.background_overlay_opacity or '0.3'};
    --ab-font: {font_map.get(config.font_family, font_map['system-ui'])};
    --ab-text-color: {config.text_color or '#212529'};
    --ab-card-bg: {config.card_background_color or '#FFFFFF'};
    --ab-glass-blur: {config.glassmorphism_blur or '10'}px;
    --ab-glass-opacity: {config.glassmorphism_opacity or '0.2'};
    --ab-input-radius: {config.input_border_radius or '6'}px;
    --ab-btn-radius: {config.button_border_radius or '6'}px;
    --ab-btn-color: {config.button_color or config.primary_color or '#714B67'};
    --ab-btn-text: {config.button_text_color or '#FFFFFF'};
}}

body.ab-template-centered, body.ab-template-fullbleed {{
    {bg_css}
}}
body.ab-template-split .ab-split-aside {{
    {bg_css}
}}
"""
        return request.make_response(css, headers=[
            ('Content-Type', 'text/css'),
            ('Cache-Control', 'max-age=60')
        ])
        
    @http.route('/auth_branding/image/<string:field>', type='http', auth='public')
    def get_image(self, field, **kwargs):
        company_id = int(kwargs.get('company_id', 0))
        config = request.env['auth.branding.config'].sudo().get_or_create(company_id=company_id)
        if not getattr(config, field, False):
            return request.not_found()
        return request.env['ir.binary']._get_stream_from(config, field).get_response()
