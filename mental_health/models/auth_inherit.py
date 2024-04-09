from odoo import fields, models,api


class Signup(models.Model):
    _inherit = "res.users"

    organization_type = fields.Many2one("organization.type")
    employee_size = fields.Char()
    industry = fields.Char()
    organization_account=fields.Many2one("organization.account",string="Organization Account")
    # company_ids = fields.Many2many('res.company',
    #                                default=lambda self: self._get_custom_default_companies(),required=False)
    # company_id = fields.Many2one('res.company', default=lambda self: self._get_custom_default_company(),required=False)
    #
    # def _get_custom_default_companies(self):
    #     if self.organization_account:
    #         company_ids = self.organization_account.associate_company
    #         return [(6, 0, company_ids.ids)]
    #     else:
    #         return self.env.company.ids
    # def _get_custom_default_company(self):
    #     if self.organization_account:
    #         company=self.organization_account.associate_company
    #         return company
    #     else:
    #         return self.env.company.id

    @api.model
    def create(self, values):
        record = super(Signup, self).create(values)
        if values.get('is_company') == True:
            organization=self.env['organization.account'].sudo().create({
                'organization_name': values.get('name', ''),
                'associated_user':record.id,
                'email': values.get('email', ''),
                'phone': values.get('phone', ''),
                'city': values.get('city', ''),
                'street': values.get('street', ''),
                'zip': values.get('zip', ''),
                'organization_type': values.get('organization_type', ''),
                'employee_size': values.get('employee_size', ''),
                'industry': values.get('industry', ''),
            })
            print(record)
            print(record.partner_id)
            partner_id = record.partner_id
            print(partner_id)
            if partner_id:
                print(partner_id.id)
                company = self.env['res.company'].search([('partner_id','=',partner_id.id)])
                if company:
                    print(company)
                    print(company.id)
                    record.sudo().write({
                        'company_ids':[(6, 0, [company.id])],
                        'company_id': company.id,
                    })
        return record

    @api.model
    def unlink_user(self, user_id):
        user = self.env['res.users'].sudo().browse(user_id)
        if user:
            user.sudo().unlink()
            return True
        return False