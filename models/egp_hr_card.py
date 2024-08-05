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
            ('active', 'Active'),
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

        if self.category == 'administrative':
            return self.env.ref(
                'egp_hr_recruitment.action_administrative_employee_card'
            ).report_action(self)

        elif self.category == 'service':
            return self.env.ref(
                'egp_hr_recruitment.action_service_employee_card'
            ).report_action(self)

        elif self.category == 'judicial':
            return self.env.ref(
                'egp_hr_recruitment.action_judical_employee_card'
            ).report_action(self)

        elif self.category == 'military':
            return self.env.ref(
                'egp_hr_recruitment.action_military_employee_card'
            ).report_action(self)

        raise UserError(
            _('Please select an employee category before printing the employee card.')
        )