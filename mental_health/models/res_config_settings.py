# from odoo import models,fields

# class ResConfigSettings(models.TransientModel):
#     _inherit = ['res.config.settings']

#     default_slot_duration = fields.Float("Default Slot Duration",default_model='slot.define.model',config_parameter='mental_health.default_slot_duration')
#     average_working_hours = fields.Float('Average Working Hours',
#                                          default_model='doctor.working.hours',
#                                          config_parameter='mental_health.average_working_hours'
#                                          )
#     default_appointment_calender_period = fields.Integer("Default Appointment Calender Period",
#                                                          default_model="doctor.dates",
#                                                          config_parameter='mental_health.default_appointment_calender_period'
#                                                          )
from odoo import models, fields, api

class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    # Add your custom fields here
    default_slot_duration = fields.Float("Default Slot Duration",default_model='slot.define.model',config_parameter='mental_health.default_slot_duration')

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        res.update(
            default_slot_duration=self.env['ir.config_parameter'].sudo().get_param('mental_health.default_slot_duration')
        )
        return res

    def set_values(self):
        super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('mental_health.default_slot_duration', self.default_slot_duration)