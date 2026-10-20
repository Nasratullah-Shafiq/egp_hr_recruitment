from odoo import models, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    code = fields.Char(required=False)