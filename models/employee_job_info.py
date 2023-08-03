# models/employee_job_information.py

from odoo.exceptions import UserError

from odoo import models, fields


class EmployeeJobInformation(models.Model):
    _name = 'employee.job.information'
    _description = 'Employee Job Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    job_id = fields.Many2one('hr.job', string='Job', related='employee_id.job_id', store=True, readonly=True,
                             tracking=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    tracking=True)
    father_names = fields.Char(string='Father Name', related='employee_id.father_name', store=True,
                               readonly=True
                               )
    grand_father_names = fields.Char(string='Grand Father Name', related='employee_id.grand_father_name',
                                     store=True,
                                     readonly=True
                                     )

    execution_type = fields.Selection(
        selection=lambda self: self.env['hr.employee']._fields[
            'execution_type'
        ].selection,
        string='Execution Type'
    )

    p2_form_no = fields.Char(
        string='P2 Form No'
    )

    p2_approval_date = fields.Date(
        string='P2 Approval Date'
    )
    country_id = fields.Many2one(
        'res.country', string="Country", tracking=True,
        default=lambda self: self.env.ref('base.af', raise_if_not_found=False)
    )

    province_id = fields.Many2one(
        "res.country.state", string='Province', ondelete='restrict',
        domain="[('country_id', '=?', country_id)]", tracking=True
    )

    job_district = fields.Many2one(
        'employee.district', string="Job District", tracking=True, ondelete='cascade')

    employee_department_id = fields.Many2one(
        'hr.department',
        string='Department',
        tracking=True,
    )

    employee_job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        tracking=True,
        domain="[('department_id', '=', employee_department_id)]",
    )

    grade_id = fields.Many2one('employee.grade', string='Grade')

    court_level = fields.Selection(
        selection=lambda self: self.env['hr.employee']._fields[
            'court_level'
        ].selection,
        string='Court Level', groups="egp_hr.group_supreme_court_employee_officers"
    )

    approval_date = fields.Date(
        string='Approval Date'
    )

    transfer_reason = fields.Text(
        string='Transfer Reason'
    )

    organizer = fields.Char(
        string='Organizer'
    )

    arranger_id = fields.Many2one(
        'res.users',
        string='Arranger'
    )

    approver = fields.Char(
        string='Approver'
    )

    transfer_date = fields.Date(
        string='Transfer Date'
    )

    attachments = fields.Many2many(
        'ir.attachment',
        string='Attachments'
    )

    def action_send_to_employee(self):
        self.ensure_one()

        if not self.employee_id:
            raise UserError(
                'Please select an employee first.'
            )

        vals = {
            'execution_type': self.execution_type,
            'p2_form_no': self.p2_form_no,
            'p2_approval_date': self.p2_approval_date,
            'province_id': self.province_id.id,
            'job_district': self.job_district.id,
            'department_id': self.employee_department_id.id,
            'job_id': self.employee_job_id.id,
            'grade_id': self.grade_id.id,
            'court_level': self.court_level,
            'approval_date': self.approval_date,
            'transfer_reason': self.transfer_reason,
            'organizer': self.organizer,
            'arranger_id': self.arranger_id.id,
            'approver': self.approver,
            'transfer_date': self.transfer_date,
        }

        self.employee_id.write(vals)

        # Copy attachments to employee
        if self.attachments:
            self.attachments.write({
                'res_model': 'hr.employee',
                'res_id': self.employee_id.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'res_id': self.employee_id.id,
            'target': 'current',
        }
