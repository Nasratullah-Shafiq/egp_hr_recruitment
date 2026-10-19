from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # company's description
    about = fields.Html(string='About the Company', help='A detailed description of the company.')