from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal


class EgpHrRecruitmentController(http.Controller):
    @http.route('/hrJob/', auth='public', website=True)
    def index(self, **km):
        # return "Hello world"
        # return template data
        return http.request.render('egp_hr_recruitment.subjects', {
            'subjects':
                ["Maths", "Programing", "Networking", "Arabic"],
        })

    # display model data on website
    #     hrJob = http.request.env['hr.job'].search([('state', 'in', ('position_active'))])
    #     return http.request.render('hr.job', {
    #         'courses': hrJob,
    #     })

    # passing route name with string value
    @http.route('/job/<name>', auth='public', website=True)
    def display_route_name(self, name):
        return '<h1>{}</h1>'.format(name)

    # passing route name with integer value
    @http.route('/job/id/<int:id>', auth='public', website=True)
    def display_route_name_integer(self, id):
        return '<h1>{}</h1>'.format(type(id).__name__)

    # display model data in route
    @http.route('/academy/<model("hr.job"):course>', auth='public', website=True)
    def display_job_details(self,course):
        return http.request.render('egp_hr_recruitment.course_detail', {'course':course})


# add class for available vacancies in my account menu
class EgpHrRecruitmentCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(EgpHrRecruitmentCustomerPortal, self)._prepare_home_portal_values(counters)
        vacancies = http.request.env['hr.job'].search_count([])  # Count the available vacancies
        values.update({
            'vacancies': vacancies,
        })
        return values



