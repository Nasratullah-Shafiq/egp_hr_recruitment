from odoo import api, fields, models, _, tools
from datetime import datetime, date


class HrUnAllocatedSeats(models.TransientModel):
    _name = "hr.applicant.empty.report"
    _description = "HR job Report"

    position_ids = fields.Many2many('hr.job', string='Position Name', domain="[('position_activeness_check', '=','position_active')]")
    def action_print_report(self):
        data = {
            'position_ids': self.position_ids.ids,
            'create_date': self.create_date,

        }

        return self.env.ref('egp_hr_recruitment.action_un_allocated_seats').report_action(self, data=data)


class HrUnAllocatedSeatsWizardAbstract(models.AbstractModel):
    _name = "report.egp_hr_recruitment.un_allocated_seat_template"

    def _get_report_values(self, docids, data=None):
        domain = []
        if data.get('position_ids'):
            domain.append(('id', 'in', data['position_ids']))

        docs = self.env['hr.job'].search(domain)

        # Prepare data for the report
        report_data = []
        for job in docs:
            total_target = job.no_of_recruitment  # Assuming this field exists
            unallocated_count = total_target - job.applicant_hired

            report_data.append({
                'department': job.department_id.name,
                'position_title': job.name,
                'position_rank': job.position_rank,
                'no_of_recruitment': job.no_of_recruitment,
                 'hired':job.applicant_hired,
                'unallocated_count': unallocated_count,
            })

        return {
            'doc_ids': docs.ids,
            'doc_model': 'hr.job',
            'docs': docs,
            'datas': report_data,
            'creation_year': data.get('creation_year')

}