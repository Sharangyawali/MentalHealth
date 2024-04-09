from odoo import http, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from werkzeug.utils import redirect
import pyotp

class AuthSignupOverride(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if request.httprequest.method == 'POST':
            user_found=request.env['res.users'].sudo().search([('login','=',qcontext.get('login'))])
            if(user_found):
                qcontext["error"] = _("Another user is already registered using this email address.")
            elif qcontext.get('password') != qcontext.get('confirm_password'):
                qcontext["error"] = _("Password and confirm password are not same")
            else:
                otp_secret = pyotp.random_base32()
                totp = pyotp.TOTP(otp_secret)
                otp = totp.now()

                qcontext['otp_secret'] = otp_secret
                qcontext['otp'] = otp
                qcontext['otp_verified'] = False
                qcontext['otp_enabled']=True
                qcontext['phone']=kw.get("phone")
                qcontext['city']=kw.get("city")
                qcontext['street']=kw.get("street")
                qcontext['zip']=kw.get("zip")
                type=kw.get("type")
                if type == 'organization':
                    qcontext['organization_type'] = kw.get("org_type")
                    qcontext['employee_size'] = kw.get("employee_size")
                    qcontext['industry'] = kw.get("industry")
                    created_user=request.env['res.users'].sudo().create({
                        'login':qcontext.get('login'),
                        'password':qcontext.get('password'),
                        'otp_verified':qcontext.get('otp_verified'),
                        'name':qcontext.get('name'),
                        'otp_enabled':qcontext.get('otp_enabled'),
                        'otp':qcontext.get('otp'),
                        'phone':qcontext.get('phone'),
                        'city': qcontext.get('city'),
                        'street': qcontext.get('street'),
                        'zip': qcontext.get('zip'),
                        'email':qcontext.get('login'),
                        'organization_type': qcontext.get('organization_type'),
                        'employee_size': qcontext.get('employee_size'),
                        'industry': qcontext.get('industry'),
                        'is_company': True,
                        'groups_id': [(6, 0, [request.env.ref('mental_health.company_group').id,
                                              request.env.ref('base.group_portal').id])]
                    })
                else:
                    created_user = request.env['res.users'].sudo().create({
                        'login': qcontext.get('login'),
                        'password': qcontext.get('password'),
                        'otp_verified': qcontext.get('otp_verified'),
                        'name': qcontext.get('name'),
                        'otp_enabled': qcontext.get('otp_enabled'),
                        'otp': qcontext.get('otp'),
                        'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                        'phone': qcontext.get('phone'),
                        'city': qcontext.get('city'),
                        'street': qcontext.get('street'),
                        'zip': qcontext.get('zip'),
                        'email': qcontext.get('login'),
                    })
                request.env['res.users'].sudo().send_mail_otp_contain(qcontext.get('login'),qcontext.get('name'),qcontext.get('otp'),'account validation ')
                request.session['qcontext_data'] = qcontext
                return request.redirect(f'/web/verify_otp?id={created_user.id}')
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if request.httprequest.method == 'POST':
            user_found=request.env['res.users'].sudo().search([('login','=',qcontext.get('login'))])
            if qcontext.get('token'):
                password = kw.get('password')
                confirm_password = kw.get('confirm_password')
                if user_found:
                    if password == confirm_password:
                        user_found.sudo().write({
                            'password': password,
                            'change_password': False
                        })
                        return request.redirect('/web/login')
                    else:
                        qcontext['error'] = _("Password and confirm password must be same.")
                else:
                    qcontext['error'] = _("Password change failed. Please try again.")
            else:
                if user_found:
                    otp_secret = pyotp.random_base32()
                    totp = pyotp.TOTP(otp_secret)
                    otp = totp.now()
                    qcontext['otp_secret'] = otp_secret
                    qcontext['otp'] = otp
                    qcontext['otp_enabled'] = True
                    user_found.sudo().write({
                        'otp':qcontext['otp'],
                        'otp_enabled': qcontext.get('otp_enabled'),
                    })
                    request.env['res.users'].sudo().send_mail_otp_contain(qcontext.get('login'),user_found.name,qcontext.get('otp'),'password reset ')
                    request.session['qcontext_data'] = qcontext
                    return request.redirect(f'/web/verify_otp?id={user_found.id}')
                else:
                    qcontext['error']=_("No account with this email")

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route('/web/verify_otp', type='http', auth='public',csrf=False, website=True, sitemap=False)
    def verify_otp(self,id='',*args, **kw):
        qcontext = request.session.pop('qcontext_data',{})
        if not qcontext:
            if not id:
                return request.redirect('/web/login')

        if request.httprequest.method == 'POST':
            entered_otp = kw.get('otp')
            if id:
                search_user=request.env['res.users'].sudo().search([('id','=',id)])
            else:
                search_user=request.env['res.users'].sudo().search([('login','=',qcontext.get('login'))])
            if search_user.otp_verified==False:
                if entered_otp:
                    if qcontext.get('otp'):
                        otp = qcontext.get('otp')
                    elif id:
                        otp= search_user.otp
                    if otp==entered_otp:
                        qcontext['otp_verified'] = True
                        qcontext['otp_enabled']=False
                        search_user.sudo().write({
                            'otp_verified':True,
                            'otp_enabled':False,
                            'otp':'',
                        })
                        return request.redirect('/web/login')
                    else:
                        qcontext['error'] = _("Invalid OTP. Please try again.")
                else:
                    qcontext['error'] = _("OTP verification failed. Please try again.")
            else:
                if entered_otp:
                    if qcontext.get('otp'):
                        otp = qcontext.get('otp')
                    elif id:
                        otp= search_user.otp
                    if otp==entered_otp:
                        qcontext['otp_enabled']=False
                        qcontext['change_password']=True
                        search_user.sudo().write({
                            'otp_enabled':False,
                            'otp':'',
                            'change_password':True,
                        })
                        request.session['qcontext_data'] = qcontext
                        return request.redirect(f'/web/change_password?id={search_user.id}')
                    else:
                        qcontext['error'] = _("Invalid OTP. Please try again.")
                else:
                    qcontext['error'] = _("OTP verification failed. Please try again.")

        request.session['qcontext_data'] = qcontext

        response= request.render('custom_auth.otp_verification', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route('/web/change_password', type='http', auth='public', csrf=False, website=True, sitemap=False)
    def cahnge_password(self, id='', *args, **kw):
        qcontext = request.session.pop('qcontext_data',{})
        qcontext['error']=_('')
        if not qcontext:
            if not id:
                return request.redirect('/web/login')
        if request.httprequest.method == 'POST':
            password = kw.get('password')
            confirm_password=kw.get('confirm_password')
            if id:
                search_user=request.env['res.users'].sudo().search([('id','=',id)])
            elif qcontext.get('login'):
                search_user=request.env['res.users'].sudo().search([('login','=',qcontext.get('login'))])
            if search_user:
                if password==confirm_password:
                    if search_user.change_password==True:
                        search_user.sudo().write({
                            'password':password,
                            'change_password':False
                        })
                        return request.redirect('/web/login')
                    else:
                        qcontext['error'] = _("Password change failed. Please try again.")
                else:
                    qcontext['error'] = _("Password and confirm password must be same.")
            else:
                qcontext['error'] = _("Password change failed. Please try again.")

        response = request.render('custom_auth.change_password', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def send_otp_email(self, email, otp):
        # Implement your logic to send OTP through email (e.g., using the 'mail' module)
        # You can use Odoo's mail template or your custom email sending logic
        pass



