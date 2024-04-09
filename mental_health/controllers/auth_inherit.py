from odoo import http
from odoo.http import request
from custom_auth.controllers.main import AuthSignupOverride
# from odoo.addons.auth_signup.controllers.main import AuthSignupHome
# from odoo.addons.web.controllers.home import ensure_db
import json
import base64

class AuthSignupInheritValues(AuthSignupOverride):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext=self.get_auth_signup_qcontext()
        res = super(AuthSignupInheritValues, self).web_auth_signup(*args,**kw)
        user = (
            request.env["res.users"]
            .sudo()
            .search([("login", "=", qcontext.get("login"))])
        )
        if request.httprequest.method == "POST":
            additional_fields = {
                "phone": kw.get("phone"),
                "city": kw.get("city"),
                "street": kw.get("street"),
                "zip": kw.get("zip"),
            }
            user.sudo().write(additional_fields)
            type=kw.get("type")
# class AuthSignupInheritValues(AuthSignupHome):
#     @http.route("/web/signup", type="http", auth="public", website=True, sitemap=False)
#     def web_auth_signup(self, *args, **kw):
#         qcontext = self.get_auth_signup_qcontext()
#         response = super(AuthSignupInheritValues, self).web_auth_signup(*args, **kw)
#         user = (
#             request.env["res.users"]
#             .sudo()
#             .search([("login", "=", qcontext.get("login"))])
#         )
#         if request.httprequest.method == "POST":
#             additional_fields = {
#                 "phone": kw.get("phone"),
#                 "city": kw.get("city"),
#                 "street": kw.get("street"),
#                 "zip": kw.get("zip"),
#             }
#             user.sudo().write(additional_fields)
#             template = request.env.ref(
#                 "auth_signup.mail_template_user_signup_account_created",
#                 raise_if_not_found=False,
#             )
#             return self.web_login(*args, **kw)
#         return response
