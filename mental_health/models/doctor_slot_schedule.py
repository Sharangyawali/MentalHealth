from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError
from . import functions
from datetime import datetime, timedelta


class DoctorWorkingHours(models.Model):
    _name = 'doctor.working.hours'
    _description = 'Doctor Working Hours'

    doctor_id = fields.Many2one('doctor.list.model', string='Doctor')
    # Assuming slots are in minutes
    slot_duration = fields.Float(string='Slot Duration', default=00.30)
    working_schedule_ids = fields.One2many(
        'every.day.working.schedule', 'working_hour_model_id')

    @api.constrains('slot_duration')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot_duration) < '00:00' or functions.float_to_time(slot.slot_duration) > '23:59':
                raise ValidationError(
                    'The slot value must be between 0.00 and 23.59')

    @api.constrains('doctor_id')
    def check_doctor_uniqueness(self):
        for record in self:
            if self.search_count([('doctor_id', '=', record.doctor_id.id)]) > 1:
                raise ValidationError(
                    "Error!! Doctor already has assigned working hours...")


class DoctorWorkingHoursSlot(models.Model):
    _name = 'doctor.working.hours.slot'
    _description = 'Doctor Working Hours Slot'
    _rec_name = 'related_name'

    every_day_schedule_id = fields.Many2one(
        'every.day.working.schedule', string='Working Hours')
    slot_start_time = fields.Float(string='Slot Start Time')
    slot_end_time = fields.Float(string='Slot End Time')
    related_name = fields.Char(compute="compute_name")
    day_of_week = fields.Selection(
        related='every_day_schedule_id.day_of_week', string='Day of Week', store=True)
    doctor_id = fields.Many2one(
        'doctor.list.model', string='Doctor', compute='_compute_doctor', store=True)

    # applicable_dates_ids = fields.One2many(
    #     'slot.applicable.date', 'slot_id', string='Applicable Dates')
    @api.depends('every_day_schedule_id')
    def _compute_doctor(self):
        for record in self:
            record.doctor_id = record.every_day_schedule_id.working_hour_model_id.doctor_id

    @api.model
    def create(self, values):
        record = super(DoctorWorkingHoursSlot, self).create(values)
        # record._update_applicable_dates()
        return record

    def write(self, values):
        res = super(DoctorWorkingHoursSlot, self).write(values)
        self._update_applicable_dates()
        return res

    def _update_applicable_dates(self):
        # Clear existing applicable dates
        self.applicable_dates_ids.unlink()

        # Calculate applicable dates for the next 30 days where the day matches day_of_week
        current_date = fields.Date.today()
        for _ in range(30):
            if current_date.strftime('%A').lower() == self.day_of_week:
                self.applicable_dates_ids.create(
                    {'applicable_date': current_date})

            current_date += timedelta(days=1)

    @api.depends('slot_start_time', 'slot_end_time')
    def compute_name(self):
        for rec in self:
            # self.get_specified_doctor_available_dates()
            # Adjust the format as needed
            rec.related_name = f"{rec.slot_start_time}-{rec.slot_end_time}"


# this method will get the available dates for selected  doctors

    def get_specified_doctor_available_dates(self, doctor_id):
        # Get today's date
        today = datetime.now().date()

        # Calculate one month from today
        one_month_later = today + timedelta(days=30)

        # Generate a list of dates from today to one month ahead
        date_list = [datetime.now().date()+timedelta(days=x)
                     for x in range((one_month_later - today).days + 1)]
        
        print(f"The date lis tji si sis n{date_list}")

        # Below is for calculating the total number of unavailable dates
        unavailable_dates = self.env['doctor.dates'].get_unavailable_dates(
            doctor_id)
        holiday_recordset = self.env['set.holiday.model'].search([])
        holiday_dates_list = holiday_recordset.mapped('holiday_date')

        total_unavailable_dates = sorted(
            set(unavailable_dates + holiday_dates_list))

        # THIS BELOW IS THE TOTAL AVAILABLE LIST OF DATES FOR SPECIFIED PERIOD OF TIME
        if date_list:
            # return total_unavailable_dates
            filtered_available_date_list = [
            date for date in date_list if date not in total_unavailable_dates]

            print(
                f"Total total_available_dates dates are :{filtered_available_date_list}")
            # this will return the available dates if the doctor
            return filtered_available_date_list
        else:
            return UserError('Error OCcured ')

    def get_doctor_slot_on_specified_date(self, booking_requested_date, doctor_id):

        requested_doctor = self.env['doctor.list.model'].search(
            'id', '=', 'doctor_id.id')
        booking_requested_date = '2020-12-06'

        # Get the already booked appointment slot of the doctor for specified date
        booked_appointment_list = self.env['book.appointment'].search([
            ('doctor_model_id', '=', doctor_id),
            ('appointment_date', '=', booking_requested_date),
            ('status', 'in', ['draft', 'approved'])
        ])
        # this below will give the booked slot
        booked_slot = booked_appointment_list.mapped('appointment_slot')

        # Get the corresponding day of the slot
        date_string = booking_requested_date
        date_object = datetime.strptime(date_string, '%Y-%m-%d')

        corresponding_day_of_week_in_integer = date_object.weekday()

        # Mapping integers to day names
        day_names = ['Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[corresponding_day_of_week_in_integer]


class SlotApplicableDate(models.Model):
    _name = 'slot.applicable.date'
    _description = 'Applicable Date for Doctor Working Hours Slot'

    slot_id = fields.Many2one('doctor.working.hours.slot', string='Working Hours Slot')
    applicable_date = fields.Date(string='Applicable Date')
        # this is for getting the list of available doctor with available time
    # based on the date provided by the user
    # def get_available_doctor(self,specified_date):
    #     doctor_working_hour_ref = self.env['doctor.working.hours'].search([])

    #     # to store all doctor available slot with other info
    #     doctor_available_slot_dictionary = []

    #     for doc_rec in doctor_working_hour_ref:
    #         if doc_rec.doctor_id:
    #             # convert the specified date into day
    #             specified_date_str = '2024-01-10'
    #             specified_date = fields.Date.from_string(specified_date_str)

    #             # Convert to a datetime.date object
    #             specified_datetime = datetime.combine(specified_date, datetime.min.time())
    #             day_of_week_index = specified_datetime.weekday()
    #             doc_rec.day_of_week

    #             # Get the day of the week as a string
    #             days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #             day_of_week_string = days_of_week[day_of_week_index]

    #             working_schedule_ids = doc_rec.working_schedule_ids.mapped('id')
    #             each_day_remaining_list = []
    #             for id in working_schedule_ids:
    #                 each_day_slot_list =id.slot_ids
    #                 slot_for_specific_day_list = each_day_slot_list.filtered(lambda x: x.slot_status == 'not_booked')

    #                 each_day_remaining_list.append({
    #                     'day_of_week':id.day_of_week,
    #                     'not_booked_slot':slot_for_specific_day_list
    #                 })

    #             # add the doctor with corresponding available slot in array
    #             doctor_available_slot_dictionary.append({
    #                 'doctor_id':doc_rec.doctor_id,
    #                 'slot_info':each_day_remaining_list
    #             })
    #     return doctor_available_slot_dictionary

    # # when patient books date with credentials like doctor_id,date and slot
    # def book_slot_and_disable(self,doctor_id,date,slot):
    #     doc_work_hours_id = self.env['doctor.working.hours'].search([
    #         ('doctor_id','=',doctor_id)
    #     ])
    #     doc_work_hours_id.working_schedule_ids({
    #         # now find the corresponding booked date after finding date
    #         # we will find the requested slot and finally we will make
    #         # that slot status booked
    #     })


class EveryDayWorkingSchedule(models.Model):
    _name = 'every.day.working.schedule'
    _description = 'Work Schedule'
    _rec_name = 'day_of_week'

    day_of_week = fields.Selection([
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ], default="sunday", string='Day of Week')

    # Assuming you store time as floats (e.g., 9.5 for 9:30 AM)
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    working_hour_model_id = fields.Many2one('doctor.working.hours')

    # Computed field for Slots
    slot_ids = fields.One2many('doctor.working.hours.slot', 'every_day_schedule_id',
                               string='Slots', compute='_compute_slots', store=True)

    @api.onchange('start_time', 'end_time')
    def _onchange_work_hours(self):
        # avoid negativepr after midnight work hours
        self.start_time = min(self.start_time, 23.99)
        self.start_time = max(self.start_time, 0.0)
        self.end_time = min(self.end_time, 24)
        self.end_time = max(self.end_time, 0.0)

        self.end_time = max(self.start_time, self.end_time)

    @api.constrains('start_time', 'end_time')
    def check_hour_value(self):
        for rec in self:
            if (rec.end_time <= rec.start_time):
                raise ValueError(
                    "Start And End time cannot be less or even match")

    @api.depends('working_hour_model_id.slot_duration','start_time','end_time')
    def _compute_slots(self):
        for record in self:
            slot_duration = record.working_hour_model_id.slot_duration
            if not record.start_time == record.end_time:
                if record.start_time and record.end_time and slot_duration:
                    # Clear existing slots
                    record.slot_ids.unlink()
                    formatted_start_time = float(self.float_to_time(record.start_time))
                    formatted_end_time = float(self.float_to_time(record.end_time))
                    abcd = type(formatted_end_time)
                    print(f"The formatted time type is {abcd}")                    
                    print(f"The formatted time type is {abcd}")                    
                    print(f"The formatted time type is {abcd}")                    
                    print(f"The formatted time type is {abcd}")                    
                    print(f"The formatted start time and end time are {formatted_start_time} and {formatted_end_time}")
                    print(f"The formatted start time and end time are {formatted_start_time} and {formatted_end_time}")
                    print(f"The formatted start time and end time are {formatted_start_time} and {formatted_end_time}")

                    # Calculate slot start times and end times based on start time, end time, and slot duration
                    current_time = formatted_start_time
                    while current_time + record.working_hour_model_id.slot_duration <= formatted_end_time:
                        record.slot_ids.create({
                            'every_day_schedule_id': record.id,
                            'slot_start_time': float(self.float_to_time(current_time)),
                            'slot_end_time': float(self.float_to_time(current_time + record.working_hour_model_id.slot_duration))
                        })
                        current_time += record.working_hour_model_id.slot_duration

    def float_to_time(self,float_time):
        # Convert float_time to hours, minutes, and seconds
        hours, remainder = divmod(float_time * 3600, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format the result
        time_format = "{:02}.{:02}".format(int(hours), int(minutes))
            
        return time_format



        # Example usage
        float_time = 4.75  # Replace this with your float time value
        formatted_time = float_to_time(float_time)
        print("Original float time: {:.2f}".format(float_time))
        print("Formatted time: {}".format(formatted_time))

