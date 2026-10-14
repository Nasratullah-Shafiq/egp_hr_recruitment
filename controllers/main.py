from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class AuthSignupHomeInherit(AuthSignupHome):

    def get_auth_signup_qcontext(self):
        qcontext = super().get_auth_signup_qcontext()

        # Add phone from the HTTP request
        qcontext['phone'] = request.params.get('phone')

        return qcontext

    def do_signup(self, qcontext):

        values = {
            'login': qcontext.get('login'),
            'name': qcontext.get('name'),
            'phone': qcontext.get('phone'),
            'password': qcontext.get('password'),
        }

        if values.get('password') != qcontext.get('confirm_password'):
            raise ValueError(
                "Passwords do not match; please retype them."
            )

        self._signup_with_values(
            qcontext.get('token'),
            values
        )


class CustomHrRecruitment(WebsiteHrRecruitment):

    @http.route(['/jobs/apply/<model("hr.job"):job>'], type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        # 1. Execute Odoo's original controller logic first
        response = super(CustomHrRecruitment, self).jobs_apply(job, **kwargs)

        # 2. Fetch the countries from the database
        countries = request.env['res.country'].sudo().search([])
        degrees = request.env['hr.recruitment.degree'].sudo().search([])
        # 3. Inject the 'countries' variable into the template's context
        response.qcontext['countries'] = countries
        response.qcontext['degrees'] = degrees
        return response


class PortalDependentDropdowns(http.Controller):
    # 2. JSON Route to fetch provinces based on country
    @http.route(['/get_provinces'], type='json', auth="public", methods=['POST'], website=True)
    def get_provinces(self, country_id):
        provinces = request.env['res.country.state'].sudo().search_read(
            [('country_id', '=', int(country_id))],
            ['id', 'name']
        )
        return provinces

    # 3. JSON Route to fetch districts based on province
    @http.route(['/get_districts'], type='json', auth="public", methods=['POST'], website=True)
    def get_districts(self, province_id):
        districts = request.env['employee.district'].sudo().search_read(
            [('province_id', '=', int(province_id))],
            ['id', 'name']
        )
        return districts



