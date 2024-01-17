from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class CourtContactController(http.Controller):

    @http.route('/court/contact/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def submit_contact_form(self, **post):
        # Get the data from the form
        name = post.get('name')
        email = post.get('email_from')
        phone = post.get('phone')
        company_name = post.get('company')
        subject = post.get('subject')
        description = post.get('description')

        # Basic Validation
        if not name or not email or not subject or not description:
            return request.render('egp_hr_recruitment.court_contact_us_page', {
                'error_message': 'Please fill in all required fields (Name, Email, Subject, Message).'
            })

        contact_id = None

        try:
            # Create Website Contact
            website_contact_vals = {
                'name': name,
                'email': email,
                'phone': phone,
                'company': company_name if company_name else '',
                'subject': subject,
                'message': description,
                'status': 'new',
            }

            new_contact = request.env['website.contact'].sudo().create(website_contact_vals)
            contact_id = new_contact.id

            # Send confirmation email to customer
            self._send_confirmation_email(new_contact, email, name, description)

            # Commit to database
            request.env.cr.commit()

        except Exception as e:
            _logger.error(f"Failed to create contact record: {str(e)}")
            request.env.cr.rollback()
            return request.render('egp_hr_recruitment.court_contact_us_page', {
                'error_message': 'An internal error occurred. Please try again later.'
            })

        return request.redirect('/contactus-thank-you')

    @http.route('/contactus-thank-you', type='http', auth='public', website=True)
    def contactus_thank_you(self):
        """Thank you page after form submission"""
        return request.render('egp_hr_recruitment.court_contact_thank_you')

    @http.route('/contactus', type='http', auth='public', website=True)
    def contact_us_page(self):
        """Display the contact us page"""
        return request.render('egp_hr_recruitment.court_contact_us_page', {})

    def _send_confirmation_email(self, contact, email, name, description):
        """Send confirmation email to the customer"""
        try:
            # Get company information
            company_name = request.env.company.name or 'Our Team'
            company_email = request.env.company.email or 'info@yourcompany.com'
            company_phone = request.env.company.phone or '+1 555-555-5555'

            # Send rich HTML email
            mail_values = {
                'subject': f'Thank you for contacting us - {contact.subject}',
                'email_from': company_email,
                'email_to': email,
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
                                <p>Dear <strong>{name}</strong>,</p>
                                <p>Thank you for reaching out to us. We have received your inquiry and our team will respond within 24 hours.</p>

                                <div class="message">
                                    <h3>Your Inquiry Details:</h3>
                                    <p><strong>Subject:</strong> {contact.subject}</p>
                                    <p><strong>Message:</strong></p>
                                    <p>{description}</p>
                                </div>

                                <p>If you need immediate assistance, please contact us:</p>
                                <p>📞 Phone: {company_phone}<br/>
                                📧 Email: {company_email}</p>

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

            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()

        except Exception as e:
            _logger.warning(f"Could not send confirmation email: {e}")