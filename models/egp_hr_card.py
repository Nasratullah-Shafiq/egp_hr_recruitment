from odoo import _, models, fields, api
from odoo.exceptions import UserError

class EmployeeCard(models.Model):
    _name = 'hr.employee.card'
    _description = 'Employee Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _order = 'id desc'

    # =========================================================
    # EMPLOYEE
    # =========================================================

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True
    )
    employee_photo = fields.Image(
        string='Employee Photo',
        related='employee_id.avatar_1920',
        readonly=True
    )


    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True,
        readonly=True,
        tracking=True
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True,
        tracking=True
    )

    father_names = fields.Char(
        string='Father Name',
        related='employee_id.father_name',
        store=True,
        readonly=True
    )

    grand_father_names = fields.Char(
        string='Grand Father Name',
        related='employee_id.grand_father_name',
        store=True,
        readonly=True
    )

    job_status = fields.Selection(
        related='employee_id.job_status',
        string='Job Status',
        store=True,
        readonly=True,
        tracking=True
    )
    category = fields.Selection(
        related='employee_id.category',
        string='Employee Category',
        store=True,
        readonly=True,
        tracking=True,

    )

    identification_no = fields.Char(
        string='Identification No',
        related='employee_id.identification_no',
        store=True,
        readonly=True,
        tracking=True
    )

    english_name = fields.Char(
        string='English Name',
        related='employee_id.english_name',
        store=True,
    )

    english_father_name = fields.Char(
        string='English Father Name',
        related='employee_id.english_father_name',
        store=True,
    )

    english_job_position = fields.Char(
        string='English Job Position',
        related='employee_id.english_job_position',
        store=True,

    )

    card_count = fields.Integer(
        string='Card Count',
        default=1
    )

    # =========================================================
    # CARD INFORMATION
    # =========================================================

    issue_date = fields.Date(
        string='Issue Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )

    expire_date = fields.Date(
        string='Expire Date',
        tracking=True
    )



    card_status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('printed', 'Printed'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string='Card Status',
        default='draft',
        required=True,
        tracking=True
    )

    def action_print_employee_card(self):
        self.ensure_one()

        if self.card_status in ['cancelled', 'expired']:
            raise UserError(_('This employee card cannot be printed.'))

        if not self.category:
            raise UserError(
                _('Please select an employee category before printing.')
            )

        # Select report according to employee category
        report_xmlids = {
            'administrative': 'egp_hr_recruitment.action_administrative_employee_card',
            'service': 'egp_hr_recruitment.action_service_employee_card',
            'judicial': 'egp_hr_recruitment.action_judical_employee_card',
            'military': 'egp_hr_recruitment.action_military_employee_card',
        }

        report_xmlid = report_xmlids.get(self.category)

        if not report_xmlid:
            raise UserError(_('Please select an employee category before printing the employee card.'))

        report = self.env.ref(report_xmlid)

        # Change status from Draft to Printed
        if self.card_status == 'draft':
            self.write({
                'card_status': 'printed'
            })

        # Print the employee card
        return report.report_action(self)

    # def action_print_employee_card(self):
    #     self.ensure_one()
    #
    #     if self.category == 'administrative':
    #         return self.env.ref(
    #             'egp_hr_recruitment.action_administrative_employee_card'
    #         ).report_action(self)
    #
    #     elif self.category == 'service':
    #         return self.env.ref(
    #             'egp_hr_recruitment.action_service_employee_card'
    #         ).report_action(self)
    #
    #     elif self.category == 'judicial':
    #         return self.env.ref(
    #             'egp_hr_recruitment.action_judical_employee_card'
    #         ).report_action(self)
    #
    #     elif self.category == 'military':
    #         return self.env.ref(
    #             'egp_hr_recruitment.action_military_employee_card'
    #         ).report_action(self)
    #
    #     raise UserError(
    #         _('Please select an employee category before printing the employee card.')
    #     )

    def action_print_arcs_employee_card(self):
        self.ensure_one()

    def action_cancel_card(self):
        self.ensure_one()

        if self.card_status != 'printed':
            raise UserError(
                _('Only printed employee cards can be cancelled.')
            )

        self.write({'card_status': 'cancelled'})

        return True

    def action_reset_to_draft(self):
        self.ensure_one()

        if self.card_status != 'cancelled':
            raise UserError(
                _('Only cancelled employee cards can be reset to draft.')
            )

        self.write({
            'card_status': 'draft'
        })

        return True

    def action_expire_card(self):
        self.ensure_one()

        today = fields.Date.today()

        if self.card_status != 'printed':
            raise UserError(_('Only printed cards can be expired.'))

        if not self.expire_date or self.expire_date > today:
            raise UserError(_('This employee card has not reached its expiration date.'))

        self.write({'card_status': 'expired'})
        return True

    @api.model
    def _cron_expire_employee_cards(self):
        today = fields.Date.today()

        expired_cards = self.search([
            ('card_status', '=', 'printed'),
            ('expire_date', '!=', False),
            ('expire_date', '<=', today),
        ])

        if expired_cards:
            expired_cards.write({'card_status': 'expired'})

        return True