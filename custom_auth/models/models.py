from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    otp_enabled = fields.Boolean(string="Enable OTP", default=False)
    otp_verified = fields.Boolean(string="OTP Verified", default=False)
    otp=fields.Char(string="OTP")
    change_password=fields.Boolean(string="Change Password Enabeled",default=False)
    def send_mail_otp_contain(self,to,name,otp_value,data):
        template_ref = self.env.ref('custom_auth.res_users_otp_email_template')
        mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        print(to)
        print(data)
        print(template_ref.email_from)
        template_ref.email_from=mail_server.smtp_user
        template_ref.email_to=to
        template_ref.body_html= (f'<p>Hello {name},</p> <p>Your OTP for {data} is: <strong>{otp_value}</strong></p><p>Thank you for using our service!</p>')
        if template_ref.send_mail(self.id, force_send=True):
            print("Mail sent successfully")

