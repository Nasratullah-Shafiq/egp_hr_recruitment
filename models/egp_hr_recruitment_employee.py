from odoo import fields, models, api
class egp_hr_recruitmentEmployee(models.Model):
    _inherit = "hr.employee"
    issue_date = fields.Date(string='Issue Date',groups="egp_hr_recruitment.group_recruitment_id_card_manager")
    expire_date = fields.Date(string='Expire Date',groups ="egp_hr_recruitment.group_recruitment_id_card_manager" )

    father_name = fields.Char(string='Father Name')
    recruitment_date = fields.Date(string="Recruitment Date", readonly=True)


    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.",
                          groups="egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_id_card_manager",copy=False)
    #hr_holidays(Time off) fields that located in hr.employee model i have assign my group to it
    current_leave_id = fields.Many2one('hr.leave', string="Current Leave",
                                       groups="egp_hr.super_admin,egp_hr.officer,egp_hr_recruitment.group_recruitment_id_card_manager")
    message_main_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Main Attachment",
        groups="base.group_erp_manager,egp_hr.group_employee_officers,egp_hr.group_employee_expert,egp_hr_recruitment.group_recruitment_id_card_manager,egp_hr_recruitment.group_recruitment_amir")


@api.model
def create(self, vals):
    # Create the employee record
    employee = super(egp_hr_recruitmentEmployee, self).create(vals)

    # Increment the no_of_hired_employee field on the associated job position
    if employee.job_id:
        employee.job_id.no_of_hired_employee += 1

    return employee