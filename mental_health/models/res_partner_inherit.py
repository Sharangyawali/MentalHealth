from odoo import fields, models,api


class Partner(models.Model):
    _inherit = "res.partner"

    # company_id=fields.Many2one("res.company",compute="_company_id",store=True)
    #
    # @api.depends('email','mobile')
    # def _company_id(self):
    #     for rec in self:
    #         company=self.env["res.company"].search([('partner_id','=',rec.id)],limit=1)
    #         print(company)
    #         rec.company_id = company.id if company else False

    @api.model
    def create(self, values):
        record = super(Partner, self).create(values)
        if values.get('is_company')==True:
            company=self.env['res.company'].sudo().create({
                'name': values.get('name', ''),
                'partner_id': record.id,
                'email': values.get('email', ''),
                'phone': values.get('phone', ''),
                'city': values.get('city', ''),
                'street': values.get('street', ''),
                'zip': values.get('zip', ''),
            })
        return record