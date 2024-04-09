from odoo import models,fields,api
from odoo.exceptions import ValidationError

class SetHoliday(models.Model):
    _name = 'set.holiday.model'
    _description = 'Holiday'
    _rec_name = 'holiday_name'

    holiday_name = fields.Char('Holiday Name')
    holiday_date = fields.Date('Date')
    

    @api.constrains('holiday_date')
    def check_holiday_date(self):
        for record in self:
            existing_holiday_dates = self.env['set.holiday.model'].search([]).mapped('holiday_date')

            # check for duplicates 
            duplicates = [date for date in self.mapped('holiday_date') if date in existing_holiday_dates]
            if duplicates:
                raise ValidationError(f'Duplicate holiday dates : {", ".join(map(str,duplicates))}')

