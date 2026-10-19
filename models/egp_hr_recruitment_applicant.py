from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import urllib
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

class HrApplicant(models.Model):
    _inherit = "hr.applicant"
    _order = "total_marks desc"

    father_name = fields.Char(string='Father Name', required=True)
    last_name = fields.Char(string='Last Name')
    grand_father_name = fields.Char(string='Grand Father Name', required=True)
    partner_name = fields.Char(string="Applicant's Name", required=True)
    date_of_birth = fields.Date(string="Date of birth", required=True)
    country_id = fields.Many2one(
        'res.country',
        string="Country",
        default=lambda self: self.env.ref('base.af', raise_if_not_found=False),
    )
    province_id = fields.Many2one('res.country.state', string="Province", ondelete='cascade')
    district_id = fields.Many2one(
        "employee.district", string='District', ondelete='restrict', tracking=True,
    )
    stage_sequence = fields.Integer(
        string='Stage Sequence',
        related='stage_id.sequence',
        store=True,
    )
    village = fields.Char(string="Village")
    current_province_id = fields.Many2one('res.country.state', string="Province", ondelete='cascade')
    current_district_id = fields.Many2one(
        "employee.district", string='District', ondelete='restrict', tracking=True,
    )
    current_village = fields.Char(string="Current Village")
    comment = fields.Text(string="Comment", help="Add comments specific to this applicant",
                          groups="egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_expert")

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default="male", tracking=True)

    LANGUAGES = [
        ('en_US', 'English'),
        ('ps', 'Pashto'),
        ('prs', 'Dari'),
        ('uz', 'Uzbeki'),
        ('to', 'Torkmani'),
        ('pas', 'Pashayee'),
        ('sh', 'Shaghni'),
        ('ba', 'Balochi'),
        ('arabic', 'Arabic'),
        ('other', 'Other'),
    ]

    native_language = fields.Selection(LANGUAGES, string='Native Language', default='ps')
    other_language = fields.Char(string='Other Language')
    type_of_application = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline')
    ], default="offline", string='Type of application')
    written_test_marks = fields.Float(string="Written Test Marks")
    interview_marks = fields.Float(string="Interview Marks")
    total_marks = fields.Float(string="Total Marks", compute="_compute_total_marks", store=True)

    sequence_number = fields.Integer(string="Sequence Number", related='stage_id.sequence')
    sequence_number1 = fields.Integer(string="Sequence Number", related='stage_id.sequence')

    website_published = fields.Boolean(help='Set if the application is published on the website of the company.',
                                       tracking=True, default=0)
    salary_proposed_extra = fields.Char("Proposed Salary Extra",
                                        help="Salary Proposed by the Organisation, extra advantages", tracking=True,
                                        groups="hr_recruitment.group_hr_recruitment_user,egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_expert")

    salary_expected_extra = fields.Char("Expected Salary Extra", help="Salary Expected by Applicant, extra advantages",
                                        tracking=True,
                                        groups="hr_recruitment.group_hr_recruitment_user,egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_expert")
    salary_proposed = fields.Float("Proposed Salary", group_operator="avg", help="Salary Proposed by the Organisation",
                                   tracking=True,
                                   groups="hr_recruitment.group_hr_recruitment_user,egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_expert")
    salary_expected = fields.Float("Expected Salary", group_operator="avg", help="Salary Expected by Applicant",
                                   tracking=True,
                                   groups="hr_recruitment.group_hr_recruitment_user,egp_hr_recruitment.group_recruitment_amir,egp_hr_recruitment.group_recruitment_expert")
    job_id = fields.Many2one('hr.job', "Applied Job")
    position_rank_id = fields.Selection(related='job_id.position_rank', string='Position Rank', store=True)
    position_code = fields.Char(related='job_id.code', string='Job Code', store=True)
    work_location_id = fields.Many2one(related='job_id.work_location_id', string='Work Location')
    job_department_id = fields.Many2one(related='job_id.department_id', string='Department')
    recruitment_date = fields.Date(string="Recruitment Date", readonly=True)

    total_years_experience = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', 'Above than 10'),
        ('12', 'none experience')
    ], string='Total Years of Experience')

    applicant_faculty_name = fields.Selection(
        selection=[
            ('computer_science', 'Computer Science'),
            ('business_administration', 'Business Administration'),
            ('engineering', 'Engineering'),
            ('medicine', 'Medicine'),
            ('law', 'Law'),
            ('hr', 'HR'),
            ('education', 'Education'),
            ('arts', 'Arts'),
            ('economics', 'Economics'),
            ('agriculture', 'Agriculture'),
            ('veterinary', 'Veterinary Science'),
            ('environmental_science', 'Environmental Science'),
            ('social_sciences', 'Social Sciences'),
            ('psychology', 'Psychology'),
            ('public_health', 'Public Health'),
            ('pharmacy', 'Pharmacy'),
            ('nursing', 'Nursing'),
            ('political_science', 'Political Science'),
            ('islamic_studies', 'Islamic Studies'),
            ('architecture', 'Architecture'),
            ('geography', 'Geography'),
            ('mathematics', 'Mathematics'),
            ('physics', 'Physics'),
            ('chemistry', 'Chemistry'),
            ('biology', 'Biology'),
            ('sharia', 'Sharia'),
            ('journalism', 'Journalism'),
            ('fine_arts', 'Fine Arts'),
            ('dari_literature', 'Dari Literature'),
            ('pashto_literature', 'Pashto Literature'),
            ('turkish_literature', 'Turkish Literature'),
            ('public_administration', 'Public Administration'),
            ('military_science', 'Military Science'),
            ('mining_and_geology', 'Mining and Geology'),
            ('telecommunication', 'Telecommunication'),
            ('information_technology', 'Information Technology'),
            ('information_system', 'Information System'),
            ('software_engineering', 'Software Engineering'),
        ],
        string='Faculty Name',
    )

    committee_members = fields.Many2many('hr.employee', string='Committee Members', tracking=True)
    committee_chief = fields.Many2one('hr.employee', string='Committee Chief', tracking=True)

    # hr.applicant relation with committee team
    committee_team_id = fields.Many2one('egp.recruitment.committee', string="Committee Team")

    committee_member_positions = fields.Char(compute="_compute_committee_member_positions", string="Positions")
    email_from = fields.Char("Email", size=128, compute='_compute_partner_phone_email',
                             inverse='_inverse_partner_email', store=True, index='trigram')

    partner_phone = fields.Char("Phone", size=15, store=True, readonly=False, index='btree_not_null')

    whatsapp_sent = fields.Boolean(string="WhatsApp Sent", default=False)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', required=True)
    tazkira_number = fields.Char("Tazkira Number", store=True, required=True, unique=True)

    education_country = fields.Many2one(
        'res.country',
        string="Education Country",
        default=lambda self: self.env.ref('base.af', raise_if_not_found=False),
    )
    education_reference = fields.Char("Education Reference", store=True, required=True)
    graduation_year = fields.Char("Graduation Year", store=True, required=True)
    is_document_approved = fields.Boolean(string="Is Document Approved?")

    # job information and Lecturer fields
    previous_job = fields.Char(string="Previous Job")
    current_job = fields.Char(string="Current Job")
    lecturer_level = fields.Many2one('hr.recruitment.degree', string="Lecturer level")
    computer_skill_ids = fields.Many2many(
        'applicant.skill',
        string='Computer Skills'
    )
    lecturer_time = fields.Date(string="Lecturer Start Date")
    lecturer_end_date = fields.Date(string="Lecturer End Date")
    is_currently_lecturer = fields.Boolean(string="Currently Working as Lecturer")

    lecturer_duration_display = fields.Char(
        string="Lecturer Duration",
        compute='_compute_lecturer_duration',
        store=True
    )

    @api.constrains('tazkira_number', 'job_id')
    def _check_unique_tazkira_per_job(self):
        for record in self:
            if record.tazkira_number and record.job_id:
                # Check if another applicant with same tazkira_number exists for this job
                existing = self.search([
                    ('tazkira_number', '=', record.tazkira_number),
                    ('job_id', '=', record.job_id.id),
                    ('id', '!=', record.id)  # Exclude current record when editing
                ])
                if existing:
                    raise ValidationError(_(
                        'An application with Tazkira Number %s already exists for this position.\n'
                        'Duplicate applications are not allowed.' % record.tazkira_number
                    ))

    @api.depends('lecturer_time', 'lecturer_end_date', 'is_currently_lecturer')
    def _compute_lecturer_duration(self):
        for record in self:

            if not record.lecturer_time:
                record.lecturer_duration_display = ''
                continue

            if record.is_currently_lecturer:
                end_date = fields.Date.today()
                is_present = True
            else:
                if not record.lecturer_end_date:
                    record.lecturer_duration_display = ''
                    continue
                end_date = record.lecturer_end_date
                is_present = False

            if record.lecturer_time > end_date:
                record.lecturer_duration_display = 'Invalid dates (Start after End)'
                continue

            delta = relativedelta(end_date, record.lecturer_time)

            parts = []
            if delta.years:
                parts.append(f"{delta.years} year{'s' if delta.years != 1 else ''}")
            if delta.months:
                parts.append(f"{delta.months} month{'s' if delta.months != 1 else ''}")
            if delta.days and not delta.years and not delta.months:
                parts.append(f"{delta.days} day{'s' if delta.days != 1 else ''}")

            duration = ' '.join(parts) if parts else 'Less than a day'

            if is_present:
                duration += ' (Present)'

            record.lecturer_duration_display = duration

    @api.constrains('lecturer_time', 'lecturer_end_date', 'is_currently_lecturer')
    def _check_dates(self):
        for rec in self:
            if rec.lecturer_time and rec.lecturer_end_date and not rec.is_currently_lecturer:
                if rec.lecturer_time > rec.lecturer_end_date:
                    raise ValidationError("Start Date cannot be after End Date.")

    # method to get current date
    def get_current_date(self):
        return datetime.now().strftime('%Y-%m-%d')

    def get_current_datetime(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_current_year(self):
        return datetime.now().year

    def get_age(self):
        if self.date_of_birth:
            today = datetime.now().date()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or (
                    today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
                age -= 1
            return age
        return 0

    age_display = fields.Char(string='Age', compute='_compute_age_display', store=False)

    def _compute_age_display(self):
        for record in self:
            if record.date_of_birth:
                today = datetime.now().date()
                age = today.year - record.date_of_birth.year
                if today.month < record.date_of_birth.month or (
                        today.month == record.date_of_birth.month and today.day < record.date_of_birth.day):
                    age -= 1
                record.age_display = f"{age} year{'s' if age != 1 else ''}"
            else:
                record.age_display = ""

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        self._compute_age_display()

    def action_send_stage_notification(self):
        for rec in self:

            if not rec.email_from:
                raise UserError("Applicant email is missing!")

            stage_seq = rec.stage_id.sequence

            # AFTER SHORT LIST → SEND WRITTEN TEST
            if stage_seq == 1:
                template = self.env.ref('egp_hr_recruitment.email_template_written_test')

            #  AFTER WRITTEN TEST → SEND INTERVIEW
            elif stage_seq == 2:
                template = self.env.ref('egp_hr_recruitment.email_template_interview')

            else:
                raise UserError("Only allowed for Short List and Written Test stages!")

            #  SEND EMAIL
            template.with_context(force_send=True).send_mail(rec.id, force_send=True)

            #  SEND WHATSAPP (OPEN URL)
            return rec._send_whatsapp_message()

        return True

    def _send_whatsapp_message(self):
        self.ensure_one()

        if not self.partner_phone:
            raise UserError(_("Phone number is missing!"))

        message = f"""
    Dear {self.partner_name},

    You are selected for next stage.

    Stage: {self.stage_id.name}
    Job: {self.job_id.name}
    Location: {self.work_location_id.name}

    Regards,
    {self.company_id.name}
    """

        #  ENCODE MESSAGE (IMPORTANT FIX)
        encoded_msg = urllib.parse.quote(message)

        phone = self.partner_phone.replace('+', '').replace(' ', '')

        url = f"https://wa.me/{phone}?text={encoded_msg}"

        #  LOG MESSAGE
        self.message_post(body=f"WhatsApp Message:<br/>{message}")
        self.whatsapp_sent = True

        # ✅ OPEN WHATSAPP IN BROWSER
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    # automatic send email into applicant
    def write(self, vals):
        res = super().write(vals)

        #  Trigger only when stage changes
        if 'stage_id' in vals:
            for rec in self:

                stage_seq = rec.stage_id.sequence

                #  AFTER SHORT LIST → SEND WRITTEN TEST
                if stage_seq == 1:
                    template = self.env.ref('egp_hr_recruitment.email_template_written_test')

                #  AFTER WRITTEN TEST → SEND INTERVIEW
                elif stage_seq == 2:
                    template = self.env.ref('egp_hr_recruitment.email_template_interview')

                else:
                    continue

                #  SEND EMAIL
                if rec.email_from:
                    template.send_mail(rec.id, force_send=True)
        return res

    def action_set_status_short_list(self):
        self.set_stage_by_sequence(1)

    def action_set_status_written_test(self):
        self.set_stage_by_sequence(2)

    def action_set_status_interview(self):
        for record in self:
            # Check if written_test_marks is filled
            if record.written_test_marks == 0.00:
                raise UserError(_("Please enter the written test marks before moving to the Interview stage."))
        self.set_stage_by_sequence(3)

    # def action_set_status_hired(self):
    #     for record in self:
    #         # Check if written_test_marks is filled
    #         if record.interview_marks == 0.00:
    #             raise UserError(_("Please enter the Interview mark before moving to the Hired stage."))
    #     self.set_stage_by_sequence(4)

    def action_set_status_hired(self):
        for record in self:
            # Check if written_test_marks is filled
            if record.interview_marks == 0.00:
                raise UserError(_("Please enter the Interview mark before moving to the Hired stage."))

            if record.job_id:
                record.job_id.write({
                    'no_of_hired_employee': record.job_id.no_of_hired_employee + 1
                })
        self.set_stage_by_sequence(4)

    def action_move_to_next_stage(self):
        for applicant in self:
            # Find the next stage
            current_stage = applicant.stage_id
            next_stage = self.env['hr.recruitment.stage'].search(
                [('sequence', '>', current_stage.sequence)],
                order='sequence asc',
                limit=1
            )
            if next_stage:
                applicant.stage_id = next_stage.id
            else:
                pass

    def action_move_to_previous_stage(self):
        for applicant in self:
            current_stage = applicant.stage_id
            previous_stage = self.env['hr.recruitment.stage'].search(
                [('sequence', '<', current_stage.sequence)],
                order='sequence desc',
                limit=1
            )
            if previous_stage:
                applicant.stage_id = previous_stage.id

    @api.onchange('sequence_number')
    def onchange_sequence_number(self):
        self.sequence_number1 = self.sequence_number;

    @api.depends('written_test_marks', 'interview_marks')
    def _compute_total_marks(self):
        for record in self:
            record.total_marks = record.written_test_marks + record.interview_marks;

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        for record in self:
            if record.sequence_number > 2 and record.written_test_marks == 0.00:
                raise ValidationError("Please Enter the written test marks to go further !!!")

            if record.sequence_number > 3 and record.interview_marks == 0.00:
                raise ValidationError("Please Enter the Interview marks to go further !!!")

    @api.model
    def write(self, vals):
        # Check if the state is being updated
        if 'stage_id' in vals:
            state = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            # If the state is set to "Hired" (sequence == 5), set recruitment_date
            if state.sequence == 4 and not self.recruitment_date:
                vals['recruitment_date'] = fields.Date.context_today(self)
        return super(HrApplicant, self).write(vals)

    def _get_employee_create_vals(self):
        self.ensure_one()
        address_id = self.partner_id.address_get(['contact'])['contact']
        address_sudo = self.env['res.partner'].sudo().browse(address_id)

        # Call the super method to get default values
        employee_vals = super(HrApplicant, self)._get_employee_create_vals()
        # Add custom fields to the values
        employee_vals.update({
            'father_name': self.father_name,
            'private_phone': self.partner_phone,
            'recruitment_date': self.recruitment_date,
        })

        return employee_vals

    def get_province_name(self):
        """Return the name of the province if set; otherwise, return an empty string."""
        for rec in self:
            return rec.province.name if rec.province else ""

    def get_native_language_display(self):
        for rec in self:
            if rec.native_language:
                return dict(self._fields['native_language'].selection).get(rec.native_language)
        return ""

    @api.depends('committee_members')
    def _compute_committee_member_positions(self):
        for record in self:
            record.committee_member_positions = ', '.join(record.committee_members.mapped('job_id.name'))

    @api.constrains('email_from')
    def _check_email_from(self):
        # Define a regex pattern for validating email addresses
        email_pattern = r'^[\w\.-]+@[a-zA-Z\d-]+\.[a-zA-Z]{2,}$'

        for applicant in self:
            # Check if email is empty or does not match the pattern
            if not applicant.email_from:
                raise ValidationError(_("Email cannot be empty. Please enter a valid email address."))
            elif not re.match(email_pattern, applicant.email_from):
                raise ValidationError(
                    _("The email '%s' is not valid. Please enter a valid email address.") % applicant.email_from)

    def set_stage_by_sequence(self, sequence):
        """Set the stage based on the sequence number."""
        stage = self.env['hr.recruitment.stage'].search([('sequence', '=', sequence)], limit=1)
        if stage:
            self.stage_id = stage.id
        else:
            raise ValidationError(f"No stage found with sequence {sequence}")
