from odoo import api, fields, models

class AuthBrandingConfig(models.Model):
    _name = 'auth.branding.config'
    _description = 'Authentication Branding Configuration'

    # Layout
    template = fields.Selection([
        ('centered', 'Centered Card'),
        ('split', 'Split Screen'),
        ('fullbleed', 'Full Bleed Background')
    ], string='Template', default='centered', required=True)

    split_alignment = fields.Selection([
        ('left', 'Image on Left'),
        ('right', 'Image on Right')
    ], string='Split Alignment', default='left', help='Side for the image in Split Screen template')

    # Card & Glassmorphism
    card_background_color = fields.Char(string='Card Background Color', default='#FFFFFF')
    glassmorphism = fields.Boolean(string='Enable Glassmorphism', default=False, help='Make the login card semi-transparent and blurred')
    glassmorphism_blur = fields.Integer(string='Blur Factor (px)', default=10)
    glassmorphism_opacity = fields.Float(string='Card Opacity (0.0 - 1.0)', default=0.2)

    # Branding
    company_logo = fields.Binary(string='Company Logo')
    favicon = fields.Binary(string='Favicon')
    tagline = fields.Char(string='Tagline', help='Optional text shown below logo, e.g. "Welcome back."')

    # Colors
    primary_color = fields.Char(string='Primary Color', default='#714B67', required=True)
    secondary_color = fields.Char(string='Secondary Color', default='#FFFFFF', required=True)
    
    background_type = fields.Selection([
        ('solid', 'Solid Color'),
        ('gradient', 'Gradient'),
        ('animated_gradient', 'Animated Gradient'),
        ('image', 'Image')
    ], string='Background Type', default='solid', required=True)
    
    background_color = fields.Char(string='Background Color', default='#f8f9fa')
    gradient_start = fields.Char(string='Gradient Start', default='#714B67')
    gradient_end = fields.Char(string='Gradient End', default='#2B124C')
    gradient_direction = fields.Selection([
        ('to right', 'to right'),
        ('to bottom', 'to bottom'),
        ('to bottom right', 'to bottom right'),
        ('to bottom left', 'to bottom left')
    ], string='Gradient Direction', default='to bottom right')
    
    background_image = fields.Binary(string='Background Image')
    background_overlay_opacity = fields.Float(
        string='Overlay Opacity', 
        default=0.3,
        help='0.0 to 1.0, darkens image for text readability'
    )

    # Typography
    font_family = fields.Selection([
        ('Inter', 'Inter'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Lato', 'Lato'),
        ('Poppins', 'Poppins'),
        ('Georgia', 'Georgia'),
        ('system-ui', 'System Default')
    ], string='Font Family', default='Inter', required=True)
    
    text_color = fields.Char(string='Text Color', default='#212529', required=True)
    input_border_radius = fields.Integer(string='Input Border Radius (px)', default=6)
    button_border_radius = fields.Integer(string='Button Border Radius (px)', default=6)

    # Button
    button_color = fields.Char(string='Button Color', default='#714B67', required=True)
    button_text_color = fields.Char(string='Button Text Color', default='#FFFFFF', required=True)

    # Footer
    show_manage_databases = fields.Boolean(string='Show Manage Databases', default=True)
    show_powered_by_odoo = fields.Boolean(string='Show Powered by Odoo', default=True)
    custom_footer_text = fields.Char(string='Custom Footer Text', help='Custom text shown in the footer, e.g. your helpdesk number')

    # Custom Content
    login_welcome_title = fields.Char(string='Login Welcome Title', help='Override the default login heading, e.g. "Welcome back!"')
    login_welcome_subtitle = fields.Char(string='Login Welcome Subtitle', help='A short subtitle below the title, e.g. "Sign in to continue."')
    terms_url = fields.Char(string='Terms of Service URL')
    privacy_url = fields.Char(string='Privacy Policy URL')
    terms_label = fields.Char(string='Terms Label', default='Terms of Service')
    privacy_label = fields.Char(string='Privacy Label', default='Privacy Policy')

    # Security Toggles (Synced with Odoo General Settings)
    auth_signup_uninvited = fields.Selection([
        ('b2b', 'On Invitation (B2B)'),
        ('b2c', 'Free Sign Up (B2C)')
    ], string='Customer Account', compute='_compute_auth_settings', inverse='_inverse_auth_signup_uninvited',
    help='B2B: User must be invited. B2C: Any user can sign up.')

    auth_signup_reset_password = fields.Boolean(
        string='Password Reset', compute='_compute_auth_settings', inverse='_inverse_auth_signup_reset_password',
        help='Show/Hide "Reset Password" link on the login page.')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def _compute_auth_settings(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        for record in self:
            record.auth_signup_uninvited = get_param('auth_signup.invitation_scope', 'b2b')
            record.auth_signup_reset_password = get_param('auth_signup.reset_password', 'False').lower() == 'true'

    def _inverse_auth_signup_uninvited(self):
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param('auth_signup.invitation_scope', record.auth_signup_uninvited)

    def _inverse_auth_signup_reset_password(self):
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param('auth_signup.reset_password', str(record.auth_signup_reset_password))

    _sql_constraints = [
        ('company_uniq', 'unique (company_id)', 'The branding configuration must be unique per company !'),
    ]

    @api.model
    def get_or_create(self, company_id=False):
        if not company_id:
            company_id = self.env.company.id
        config = self.search([('company_id', '=', company_id)], limit=1)
        if not config:
            config = self.create({'company_id': company_id})
        return config

    def action_save(self):
        # Triggered by save button in the form
        return {'type': 'ir.actions.client', 'tag': 'reload'}
