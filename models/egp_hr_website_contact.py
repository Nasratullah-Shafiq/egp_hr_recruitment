from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)



class WebsiteContact(models.Model):
    _name = 'website.contact'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Website Contact Messages'
    _order = 'create_date desc'
    _rec_name = 'subject'

    # Basic Information
    name = fields.Char(string='Full Name', required=True, tracking=True)
    email = fields.Char(string='Email Address', required=True, tracking=True)
    phone = fields.Char(string='Phone Number', tracking=True)
    company = fields.Char(string='Company Name', tracking=True)
    subject = fields.Char(string='Subject', required=True, tracking=True)
    message = fields.Text(string='Message', required=True, tracking=True)

    # Status with colors
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('replied', 'Replied'),
        ('closed', 'Closed')
    ], string='Status', default='new', required=True, tracking=True)

    # Reply tracking
    reply_message = fields.Html(string='Reply Message')
    reply_date = fields.Datetime(string='Reply Date')
    replied_by = fields.Many2one('res.users', string='Replied By')

    # Email tracking
    confirmation_sent = fields.Boolean(string='Confirmation Email Sent', default=False)
    confirmation_sent_date = fields.Datetime(string='Confirmation Sent Date')

    # Priority
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)

    # Dates
    create_date = fields.Datetime(string='Created Date', readonly=True)
    last_activity_date = fields.Datetime(string='Last Activity Date')

    # Company relation
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(_("Invalid email address!"))

    def action_mark_in_progress(self):
        for record in self:
            record.status = 'in_progress'
            record.last_activity_date = datetime.now()
            record.message_post(
                body=f"Status changed to: In Progress",
                message_type='notification'
            )

    def action_mark_replied(self):
        for record in self:
            record.status = 'replied'
            record.reply_date = datetime.now()
            record.replied_by = self.env.user
            record.last_activity_date = datetime.now()
            record.message_post(
                body=f"Status changed to: Replied by {self.env.user.name}",
                message_type='notification'
            )

    def action_mark_closed(self):
        for record in self:
            record.status = 'closed'
            record.last_activity_date = datetime.now()
            record.message_post(
                body=f"Status changed to: Closed",
                message_type='notification'
            )

    def action_send_reply(self):
        """Open wizard to compose reply email"""
        self.ensure_one()

        return {
            'name': 'Send Reply',
            'type': 'ir.actions.act_window',
            'res_model': 'website.contact.reply.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contact_id': self.id,
                'default_email': self.email,
                'default_name': self.name,
                'default_subject': f'Re: {self.subject}',
            }
        }

    def action_send_confirmation(self):
        """Resend confirmation email"""
        self.ensure_one()
        self._send_confirmation_email()

    def action_send_test_email(self):
        """Send test email for debugging"""
        self.ensure_one()
        self._send_confirmation_email(is_test=True)

    def _send_confirmation_email(self, is_test=False):
        """Send confirmation email to customer"""
        self.ensure_one()

        try:
            template = self.env.ref('egp_hr_recruitment.contact_confirmation_email_template_contact',
                                    raise_if_not_found=False)
            if template:
                # Send using template
                template.send_mail(self.id, force_send=True)
                if not is_test:
                    self.confirmation_sent = True
                    self.confirmation_sent_date = datetime.now()
                _logger.info(f"Confirmation email sent to {self.email}")
            else:
                # Fallback to manual email
                company_name = self.company_id.name or 'Our Company'
                company_email = self.company_id.email or 'info@yourcompany.com'

                mail_values = {
                    'subject': f'Thank you for contacting us - {self.subject}',
                    'email_from': company_email,
                    'email_to': self.email,
                    'body_html': f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; }}
                                .container {{ max-width: 600px; margin: 0 auto; }}
                                .header {{ background-color: #004085; color: white; padding: 20px; text-align: center; }}
                                .content {{ padding: 20px; }}
                                .message {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                                .footer {{ background-color: #f8f9fa; color: #666; padding: 10px; text-align: center; font-size: 12px; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h2>Thank You for Contacting Us</h2>
                                </div>
                                <div class="content">
                                    <p>Dear <strong>{self.name}</strong>,</p>
                                    <p>Thank you for reaching out to us. We have received your inquiry and our team will respond within 24 hours.</p>

                                    <div class="message">
                                        <h3>Your Inquiry Details:</h3>
                                        <p><strong>Subject:</strong> {self.subject}</p>
                                        <p><strong>Message:</strong></p>
                                        <p>{self.message}</p>
                                    </div>

                                    <p>Best regards,<br/>
                                    <strong>{company_name}</strong></p>
                                </div>
                                <div class="footer">
                                    <p>&copy; {company_name} - All Rights Reserved</p>
                                </div>
                            </div>
                        </body>
                        </html>
                    """,
                }
                mail = self.env['mail.mail'].sudo().create(mail_values)
                mail.send()
                if not is_test:
                    self.confirmation_sent = True
                    self.confirmation_sent_date = datetime.now()
                _logger.info(f"Confirmation email sent to {self.email}")

        except Exception as e:
            _logger.error(f"Failed to send confirmation email: {e}")
            if is_test:
                raise UserError(f"Failed to send email: {str(e)}")