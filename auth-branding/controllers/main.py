import urllib.parse
from odoo import http
from odoo.http import request

class AuthBrandingController(http.Controller):

    @http.route('/auth_branding/preview', type='http', auth='user', website=True)
    def preview(self, page='login', **kwargs):
        # Fetch config
        config = request.env['auth.branding.config'].sudo().get_or_create()
        
        # Merge saved config with kwargs overrides for live preview
        ab_config = {
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
        elif bg_type == 'image':
            # Rely on saved image, we can't preview image blob directly from iframe unless we base64 it
            bg_css = f"background: url('/auth_branding/image/background_image') no-repeat center center fixed !important; background-size: cover !important;"

        # Build inline styles using the overrides to inject into the template
        inline_style = f"""
        :root {{
            --ab-primary: {ab_config['primary_color'] or '#714B67'};
            --ab-secondary: {ab_config['secondary_color'] or '#FFFFFF'};
            --ab-overlay-opacity: {ab_config['background_overlay_opacity'] or '0.3'};
            --ab-font: {ab_config['font_family_css']};
            --ab-text-color: {ab_config['text_color'] or '#212529'};
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
            'signup_enabled': True,
            'reset_password_enabled': True,
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
        config = request.env['auth.branding.config'].sudo().get_or_create()
        
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
        elif config.background_type == 'image':
            bg_css = f"background: url('/auth_branding/image/background_image') no-repeat center center fixed !important; background-size: cover !important;"
            
        css = f"""
:root {{
    --ab-primary: {config.primary_color or '#714B67'};
    --ab-secondary: {config.secondary_color or '#FFFFFF'};
    --ab-overlay-opacity: {config.background_overlay_opacity or '0.3'};
    --ab-font: {font_map.get(config.font_family, font_map['system-ui'])};
    --ab-text-color: {config.text_color or '#212529'};
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
        config = request.env['auth.branding.config'].sudo().get_or_create()
        if not getattr(config, field, False):
            return request.not_found()
        return request.env['ir.binary']._get_stream_from(config, field).get_response()
