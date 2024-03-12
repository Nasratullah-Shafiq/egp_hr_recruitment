{
    'name': 'EGP HR Recruitment',
    'version': '1.0.1',
    'summary': 'MCIT-Afghanistan ERP HR module streamlines HR with Recruitment processes',
    'description': 'MCIT-Afghanistan HRMIS',
    'sequence': -3,
    'author': 'Nasratullah Shafiq',
    'website': 'https://mcit.gov.af/',
    'depends': ['hr', 'website', 'mail', 'portal', 'auth_signup', 'website_hr_recruitment', 'base', 'hr_recruitment',
                'egp_hr_org_structure', 'egp_hr',
                'hr_recruitment_skills'],

    'data': [
        # Security files
        'security/egp_hr_recruitment_groups.xml',
        'security/egp_hr_recruitment_security.xml',
        'security/ir.model.access.csv',

        # Default Data Files
        'data/egp_hr_recruitment_users_default_data.xml',
        'data/court_committee_team_sequence.xml',
        'data/email_templates.xml',
        'data/hr_recruitment_data.xml',
        'data/written_test_email_templates.xml',
        'data/skill_data.xml',

        # Report PDF files
        'report/egp_hr_recruitment_job_summary_paper_format.xml',
        'report/egp_hr_recruitment_employee_badge_card.xml',
        'report/egp_hr_recruitment_long_list.xml',
        'report/egp_hr_recruitment_short_list.xml',
        'report/egp_hr_recruitment_written_test.xml',
        'report/egp_hr_recruitment_hired.xml',
        'report/egp_hr_recruitment_job_description_template.xml',
        'report/egp_hr_recruitment_report_action.xml',
        'report/egp_hr_recruitment_un_allocated_seats.xml',

        # Employee Card Report files
        'report/egp_hr_recruitment_applicant_report.xml',

        # Paper formats must be loaded before report actions
        'report/egp_hr_recruitment_report_paper_format.xml',

        # Report actions
        'report/egp_hr_card_action.xml',

        # Report templates
        'report/egp_hr_card_template.xml',
        'report/egp_hr_service_card_template.xml',
        'report/egp_hr_administrative_card_template.xml',
        'report/egp_hr_military_card_template.xml',
        'report/egp_hr_judical_card_template.xml',
        'report/egp_hr_arcs_card_template.xml',

        'report/egp_hr_recruitment_arcs_temporary_employee_card.xml',
        'report/paperformat_temporary_employee_card.xml',

        # Recruitment View files
        'views/egp_hr_recruitment_applicant_view.xml',
        'views/egp_hr_recruitment_create_employee_profile.xml',
        'views/egp_hr_recruitment_employee_view.xml',
        'views/egp_hr_recruitment_existing_fields.xml',
        'views/egp_hr_recruitment_hr_applicant_list_view.xml',
        'views/hired_position_view.xml',
        'views/egp_hr_job_views.xml',

        # Committee View files
        'views/egp_hr_recruitment_committee_agent_view.xml',
        'views/egp_hr_recruitment_committee_team_views.xml',
        'views/committee_team_language.xml',

        # Skills and Job Information View files
        'views/egp_hr_recruitment_skills.xml',
        'views/employee_job_info_view.xml',

        # Recruitment Kanban View files
        'views/egp_hr_recruitment_inheritng_canban_box.xml',

        # Website Recruitment View files
        'views/template.xml',
        'views/website_menus.xml',
        'views/customize_web_footer_template.xml',
        'views/apply_job_template.xml',
        'views/inherit_job_templates.xml',
        'views/res_company_views.xml',
        'views/inherit_apply_template.xml',

        # Contact Us View files
        'views/website_new_contact_us_form.xml',
        'views/website_contact_us_views.xml',

        # Wizard View files
        'wizard/hr_applicant_empty_report_wizard.xml',
        'wizard/reply_wizard_view.xml',
    ],
    'controllers': [
        'controllers/main.py',
    ],
    'assets': {
        'web.assets_frontend': [
            'egp_hr_recruitment/static/src/js/custom_job_detail.js',
            'egp_hr_recruitment/static/src/js/portal_location.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
