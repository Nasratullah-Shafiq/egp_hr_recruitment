from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class WebsiteContactReplyWizard(models.TransientModel):
    _name = 'website.contact.reply.wizard'
    _description = 'Reply to Contact Wizard'

    contact_id = fields.Many2one('website.contact', string='Contact', required=True)
    email = fields.Char(string='To', readonly=True)
    name = fields.Char(string='Customer Name', readonly=True)
    subject = fields.Char(string='Subject', required=True)
    reply_message = fields.Html(string='Reply Message', required=True,
                                default="""<p>Dear Customer,</p>
<br/>
<p>Thank you for your message. We have received your inquiry and will get back to you shortly.</p>
<br/>
<p>Best regards,<br/>
HR Team</p>""")
    send_copy = fields.Boolean(string='Send copy to myself', default=True)
    attach_log = fields.Boolean(string='Log in chatter', default=True)

    def action_send_reply(self):
        """Send the reply email"""
        self.ensure_one()

        try:
            # Prepare email
            company_name = self.env.company.name or 'Our Company'
            company_email = self.env.company.email or 'info@yourcompany.com'

            # Send to customer
            mail_values = {
                'subject': self.subject,
                'email_from': company_email,
                'email_to': self.email,
                'body_html': self.reply_message,
            }

            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            _logger.info(f"Reply sent to {self.email}")

            # Send copy to myself if requested
            if self.send_copy and self.env.user.email:
                copy_values = {
                    'subject': f'Copy: {self.subject}',
                    'email_from': company_email,
                    'email_to': self.env.user.email,
                    'body_html': f"""
                        <div style="font-family: Arial, sans-serif;">
                            <h3>Reply Sent to Customer</h3>
                            <p><strong>To:</strong> {self.email}</p>
                            <p><strong>Customer:</strong> {self.name}</p>
                            <p><strong>Subject:</strong> {self.subject}</p>
                            <hr/>
                            <h4>Your Reply:</h4>
                            {self.reply_message}
                            <hr/>
                            <p><em>This is a copy of the reply sent to the customer.</em></p>
                        </div>
                    """,
                }
                copy_mail = self.env['mail.mail'].sudo().create(copy_values)
                copy_mail.send()
                _logger.info(f"Copy sent to {self.env.user.email}")

            # Update contact record
            self.contact_id.write({
                'reply_message': self.reply_message,
                'status': 'replied',
                'reply_date': fields.Datetime.now(),
                'replied_by': self.env.user.id,
                'last_activity_date': fields.Datetime.now(),
            })

            # Add message to chatter
            if self.attach_log:
                self.contact_id.message_post(
                    body=f"""
                    <div>
                        <h4>Reply Sent to {self.email}</h4>
                        <p><strong>Subject:</strong> {self.subject}</p>
                        <p><strong>Reply:</strong></p>
                        {self.reply_message}
                    </div>
                    """,
                    subject="Reply Sent",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )

            # Show success message
            return {
                'type': 'ir.actions.act_window_close',
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Reply sent successfully!',
                    'type': 'rainbow_man',
                }
            }

        except Exception as e:
            raise UserError(f"Failed to send reply: {str(e)}")
