from odoo import models, fields, api


class ConsultationMedium(models.Model):
    _name = "consultation.medium"
    _rec_name = "medium"
    
    medium = fields.Char("Consultation Medium")
    
class OrganizationType(models.Model):
    _name = "organization.type"
    _rec_name = "type"
    
    type = fields.Char("Type")
    
    
class OrganizationalUsers(models.Model):
    # _name="organizational.users"
    _inherit="res.users"
    
    
    
    page_ref_ = fields.Many2one("organization.account")
