from odoo import api, fields, models


class Job(models.Model):
    _inherit = 'hr.job'
    website_published = fields.Boolean(help='Set if the application is published on the website of the company.'
                                       ,
                                       groups="hr.group_hr_user,egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_expert",
                                       tracking=True)

    hired_employee_names = fields.Char(
        compute='_compute_hired_employee_names'
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        compute="_compute_employee_id",
        readonly=True,
        help="Employee currently assigned to this job position.",
    )

    @api.depends("employee_ids")
    def _compute_employee_id(self):
        for job in self:
            job.employee_id = job.employee_ids[:1] if job.employee_ids else False



    def _compute_hired_employee_names(self):
        for job in self:
            applicants = self.env['hr.applicant'].search([
                ('job_id', '=', job.id),
                ('emp_id', '!=', False),
                ('date_closed', '!=', False)
            ])
            employees = applicants.mapped('emp_id.name')
            job.hired_employee_names = ', '.join(employees)

    sequence_number = fields.Integer(string="Sequence Number", related='stage_id.sequence')

    stage_id = fields.Many2one(
        'hr.recruitment.stage',
        string='Recruitment Stage',
        ondelete='set null'
    )
