# -*- coding: utf-8 -*-

from custom_addons.mental_health.models import functions
from odoo.exceptions import ValidationError
from odoo import api,fields, models, _


class AppointmentOption(models.Model):
    _name = 'mental_health.appointment.option'
    _description = 'Appointment Option'

    name = fields.Char(string="Appointment Option",required=True)
    duration = fields.Float("Duration",required=True)
    user_specific = fields.Boolean(string='User Specific',default=False)
    users_allowed = fields.Many2many('res.users',)

    @api.constrains('duration')
    def _duration_validation(self):
        for option in self:
            if functions.float_to_time(option.duration) < '00:05' or functions.float_to_time(option.duration) > '08:00': 
                raise ValidationError(_('The duration value must be between 0:05 and 8:00'))

class DoctorDates(models.Model):
    _name = 'doctor.dates'

    doctor_name = fields.Many2one('doctor.list.model','Doctor')
    unavailable_dates = fields.One2many('doctor.unavailable.dates','unavailable_id',"Unavailable Dates")

class DoctorUnavilableDate(models.Model):
    _name = "doctor.unavailable.dates"
    _description = "Doctor Unavailable Dates"

    unavailable_id = fields.Many2one("doctor.dates",string="Doctor")
    unavailable_dates = fields.Date("Unavailable Dates")