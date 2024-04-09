from odoo import models, fields, api


class OrgAccountClass(models.Model):
    _name = "organization.account"
    _rec_name = "organization_name"

    organization_name = fields.Char("Name")
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    organization_type = fields.Many2one("organization.type", "Organization Type")
    employee_size = fields.Char("Employee Size")
    industry = fields.Char("Industry")
    city = fields.Char("City")
    street = fields.Char("Street")
    zip = fields.Char("Zip")
    logo = fields.Binary("Logo", attachment=True)
    org_users_page = fields.One2many("res.users", "organization_account",string="User page",ondelete='cascade')
    associated_user=fields.Many2one("res.users",store=True,ondelete='cascade')
    associate_company=fields.Many2one("res.company",compute="_associated_company",store=True)

    @api.depends('associated_user')
    def _associated_company(self):
        for rec in self:
            partner=rec.associated_user.partner_id
            company=self.env['res.company'].sudo().search([('partner_id','=',partner.id)])
            rec.associate_company=company.id
