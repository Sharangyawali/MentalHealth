# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from . import functions


class mental_health(models.Model):
    _name = "book.appointment"
    _description = "Appointement Record"
    _inherit = "mail.thread"
    _rec_name = "ref"

    ref = fields.Char(readonly=1, default=lambda self: "New", string="Appointment ID")
    patient_ref = fields.Many2one(
        "patient.personal.info", string="Patient", required=True, tracking=True
    )
    appointment_type = fields.Selection(
        [
            ("Psychiatry", "Psychiatry"),
            ("Dermatology", "Dermatology"),
        ],
        default="Psychiatry",
        string="Appointment Type",
        required=True,
        tracking=True,
    )
    consult_type = fields.Selection(
        [
            ("initial_consult", "Initial Consult"),
            ("follow_up_consult", "Follow Up Consult"),
        ],
        default="initial_consult",
        string="Consult Type",
        required=True,
        tracking=True,
    )
    hospital_location_id = fields.Many2one(
        "hospital.location", string="Hospital Location", tracking=True,
    )
    doctor_model_id = fields.Many2one(
        "doctor.list.model", string="Requested Doctor", required=True, tracking=True
    )
    timezone = fields.Many2one(
        "timezone.model", string="TimeZone", tracking=True
    )
    requested_appointment_date = fields.Date(
        string="Requested Appointment Date", tracking=True
    )
    appointment_slot_start_time = fields.Float(
        "Requested Appointment Slot Start", required=True, tracking=True
    )
    appointment_slot_end_time = fields.Float(
        "Requested Appointment Slot End", required=True, tracking=True
    )
    gp_referall_doc = fields.Binary("GP Referall Image")
    consultation_medium = fields.Many2one(
        "consultation.medium", "Consultation Medium", required=True, tracking=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("reject", "Rejected"),
            ("served","Served")
        ],
        default="draft",
        tracking=True,
    )

    @api.model
    def create(self, vals):
        vals["ref"] = self.env['ir.sequence'].next_by_code("mental.health.appointment.sequence")
        print(vals['ref'])
        appointment= super(mental_health, self).create(vals)
        template_ref = self.env.ref('mental_health.appointment_successfully_booked_mail').sudo()
        template_ref2=self.env.ref('mental_health.appointment_request_for_doctor').sudo()
        mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        if template_ref:
            print(template_ref.email_from)
            template_ref.email_from=mail_server.smtp_user
            template_ref.email_to = appointment.patient_ref.email
            template_ref.body_html = (
                f"<h5>Dear {appointment.patient_ref.patient_name},</h5>"
                f"<p>Your appointment request for booking on {appointment.requested_appointment_date} for slot {appointment.appointment_slot_start_time}-{appointment.appointment_slot_end_time} has been successfully submitted to doctor {appointment.doctor_model_id.doctor_full_name}</p>"
                f"<p>Thank you for using our service</p>"
                f"<h5>PsychCare Services Telehealth</h5>"
            )
            template_ref.send_mail(appointment.id, force_send=True)
        if template_ref2:
            print(template_ref2.email_from)
            template_ref2.email_from=mail_server.smtp_user
            template_ref2.email_to = appointment.doctor_model_id.contact_email
            template_ref2.body_html = (
                f"<h5>Dear {appointment.doctor_model_id.doctor_full_name},</h5>"
                f"<p>Appointment request for booking on {appointment.requested_appointment_date} for slot {appointment.appointment_slot_start_time}-{appointment.appointment_slot_end_time} has been received from {appointment.patient_ref.patient_name}</p>"
                f"<p>Thank you for using our service</p>"
                f"<h5>PsychCare Services Telehealth</h5>"
            )
            template_ref2.send_mail(appointment.id, force_send=True)
        return appointment

    # def successfully_booked_mail(self):
    #     template_ref = self.env.ref('mental_health.appointment_successfully_booked_mail')
    #     if template_ref:
    #         template_ref.email_to = self.patient_ref.email
    #         template_ref.body_html = (
    #             f"<h5>Dear {self.patient_ref.patient_name},</h5><hr/>"
    #             f"<p>Your appointment request for booking on {self.requested_appointment_date} for slot {self.appointment_slot_start_time}-{self.appointment_slot_end_time} <hr/> has been successfully submitted to doctor {self.doctor_model_id.doctor_full_name}</p>"
    #             f"<p>Thank you for using our service</p><hr/>"
    #             f"<h5>PsychCare Services Telehealth</h5>"
    #         )
    #         return template_ref.send_mail(self.id, force_send=True)

    def approve_request(self):
        self.state = "approved"

    def reject_request(self):
        self.state = "reject"

    # # Here we will get the list of available appointment dates for the specified doctor
    # @api.model
    # def compute_available_appointment_date(self):
    #     record = self
    #     if record.doctor_model_id:
    #         booking_available_dates_ref = self.env['appointment.schedule.model'].search([
    #                 ('doctor_id', '=', record.doctor_model_id.id),
    #                 ('slot_status', 'not in', ['on_buffer', 'booked'])
    #             ])
    #         available_dates = booking_available_dates_ref.mapped('date')
    #         available_date_list = []
    #         if available_dates:
    #             for date in available_dates:
    #                 string_date = str(date)
    #                 available_date_tuple = (string_date,string_date)
    #                 available_date_list.append(available_date_tuple)

    #         date_list = set(available_date_list)
    #         return date_list
    #         print(f'The available date selection is {date_list}')

    # return available_dates

    # when rejected the slot should be released so that another patient can book that slot



    def write(self, vals):
        result = super(mental_health, self).write(vals)
        mail_server = self.env['ir.mail_server'].sudo().search([], limit=1)
        if "state" in vals and vals["state"] == "approved":
            template_ref=self.env.ref('mental_health.appointment_request_accepted_mail').sudo()
            appointment_ref = self.env["appointment.schedule.model"].search(
                [
                    ("doctor_id", "=", self.doctor_model_id.id),
                    (
                        "slot_start_time",
                        "=",
                        self.appointment_slot_start_time
                        # float(self.float_to_time(self.appointment_slot_start_time)),
                    ),
                    (
                        "slot_end_time",
                        "=",
                        self.appointment_slot_end_time
                        # float(self.float_to_time(self.appointment_slot_end_time)),
                    ),
                    (
                        "date",
                        "=",
                        fields.Date.to_date(self.requested_appointment_date),
                    ),  # Convert to date for accurate comparison
                ],
                limit=1,
            )
            print(f"The appointment ref is {appointment_ref}")
            print(f"The appointment ref is {appointment_ref}")
            print(f"The appointment ref is {appointment_ref}")
            print(f"The appointment ref is {appointment_ref}")

            if appointment_ref:
                appointment_ref.write({"slot_status": "booked"})
            else:
                # Handle the case where the corresponding appointment slot is not found
                raise ValidationError("Corresponding appointment slot not found.")
            if template_ref:
                print(template_ref.email_from)
                template_ref.email_from = mail_server.smtp_user
                template_ref.email_to = self.patient_ref.email
                template_ref.body_html = (
                    f"<h5>Dear {self.patient_ref.patient_name},</h5>"
                    f"<p>Your appointment request for booking on {self.requested_appointment_date} for slot {self.appointment_slot_start_time}-{self.appointment_slot_end_time} has been successfully submitted to doctor {self.doctor_model_id.doctor_full_name}</p>"
                    f"<p>Thank you for using our service</p>"
                    f"<h5>PsychCare Services Telehealth</h5>"
                )
                template_ref.send_mail(self.id, force_send=True)
        elif "state" in vals and vals["state"] == "reject":
            template_ref2=self.env.ref('mental_health.appointment_request_rejected_mail').sudo()
            if template_ref2:
                print(template_ref2.email_from)
                template_ref2.email_from = mail_server.smtp_user
                template_ref2.email_to = self.patient_ref.email
                template_ref2.body_html = (
                    f"<h5>Dear {self.patient_ref.patient_name},</h5>"
                    f"<p>Sorry! Your appointment request for booking on {self.requested_appointment_date} for slot {self.appointment_slot_start_time}-{self.appointment_slot_end_time} has been rejected by doctor {self.doctor_model_id.doctor_full_name}</p>"
                    f"<p>Please contact to administration or try for other slots</p>"
                    f"<h5>PsychCare Services Telehealth</h5>"
                )
                template_ref2.send_mail(self.id, force_send=True)
        return result

    def float_to_time(self, float_time):
        # Convert float_time to hours, minutes, and seconds
        hours, remainder = divmod(float_time * 3600, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format the result
        time_format = "{:02}.{:02}".format(int(hours), int(minutes))

        return time_format

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100


class PatientPersonalInfo(models.Model):
    _name = "patient.personal.info"
    _description = "Patient"
    _inherit = "mail.thread"
    _rec_name = "patient_name"

    patient_name = fields.Char("Patient Name")
    profile_picture = fields.Binary("Profile")
    date_of_birth = fields.Date("Date of Birth")
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")], string="Gender"
    )
    email = fields.Char("Email Address")
    mobile = fields.Char("Mobile No")
    address = fields.Char("Address")
    street = fields.Char("Street No")
    post_code = fields.Char("Post Code")
    suburb = fields.Char("Suburb")
    comments = fields.Text("Comments")

    # this is insurance related info
    medicare_card_no = fields.Char("Medicare Card Number")
    medicare_card_expiry = fields.Date("Medicare Card Expiry Date")

    # this below is for the credit debit card details
    credit_debit_card_no = fields.Char("Credit/Debit Card No")
    credit_debit_expiry = fields.Date("Credit/Debit Expiry Date")
    card_holder_name = fields.Char("Card Holder Name")
    card_security_code = fields.Char("Security Code No")

    # @api.model
    # def create(self, vals):
    #     record=super(PatientPersonalInfo, self).create(vals)
    #     card_no=self.env['ir.sequence'].next_by_code("mental.health.employee.sequence")
    #     if card_no:
    #         email=vals['email']
    #         user=self.env['res.users'].sudo().search('login','=',email)
    #         company=user.company_id.name
    #         print(vals['medicare_card_no'])
    #     return record

class DoctorList(models.Model):
    _name = "doctor.list.model"
    _description = "Doctor List Model"
    _inherit = "mail.thread"
    _rec_name = "doctor_full_name"

    doctor_full_name = fields.Char("Doctor Name",required=True)
    profile_picture = fields.Binary("Profile Picture")
    specialty = fields.Char("Specialty")
    qualifications = fields.Text("Qualifications")
    contact_phone = fields.Char("Contact Phone",required=True)
    contact_email = fields.Char("Contact Email",required=True)
    office_address = fields.Text("Office Address")
    availability = fields.Text("Availability")
    appointment_duration = fields.Float("Appointment Duration")
    accepting_new_patients = fields.Boolean("Accepting New Patients")
    insurance_accepted = fields.Char("Insurance Accepted")
    languages_spoken = fields.Char("Languages Spoken")
    experience_years = fields.Integer("Years of Experience")
    hospital_affiliations = fields.Char("Hospital Affiliations")
    professional_memberships = fields.Char("Professional Memberships")
    license_number = fields.Char("License Number")
    license_expiration_date = fields.Date("License Expiration Date")
    reviews_and_ratings = fields.Text("Reviews and Ratings")
    emergency_contact = fields.Char("Emergency Contact")
    telemedicine_available = fields.Boolean("Telemedicine Available")
    additional_notes = fields.Text("Additional Notes")
    work_experience = fields.Html("Work Experience")
    gender=fields.Selection([('male','Male'),('female','Female'),('others','Others')],string="Gender",requried=True)

    @api.model
    def create(self, vals):
        print("vals are",vals)
        record=super(DoctorList,self).create(vals)
        login=vals.get('contact_email')
        name=vals.get('doctor_full_name')
        phone=vals.get('contact_phone')
        self.env['res.users'].sudo().create({
            'login':login,
            'name':name,
            'phone':phone,
            'email':login,
            'is_company':False,
            'groups_id':[(6,0,[self.env.ref('mental_health.doctor_group').id,
                                              self.env.ref('base.group_portal').id])]
        })
        return record

    def generate_schedule(self):
        return {
            "name": "Enter Schedule",
            "type": "ir.actions.act_window",
            "res_model": "generate.schedule.wizard.model",
            "view_mode": "form",
            "view_id": self.env.ref("mental_health.generate_schedule_wizard_model").id,
            "target": "new",
            "context": {"default_doctor_list_model_id": self.id},
        }

    def send_approve_mail(self):
        pass

    class AppointmentScheduleModel(models.Model):
        _name = "appointment.schedule.model"

        date = fields.Date("Date")
        slot_status = fields.Selection(
            [
                ("not_booked", "Not Booked"),
                ("on_buffer", "On Buffer"),
                ("booked", "Booked"),
            ],
            default="not_booked",
        )
        day = fields.Selection(
            [
                ("sunday", "Sunday"),
                ("monday", "Monday"),
                ("tuesday", "Tuesday"),
                ("wednesday", "Wednesday"),
                ("thursday", "Thursday"),
                ("friday", "Friday"),
                ("saturday", "Saturday"),
            ],
            string="WeekDay",
        )
        slot_start_time = fields.Float("")
        slot_end_time = fields.Float("")
        doctor_id = fields.Many2one("doctor.list.model")

    # unavailable_events = fields.One2many('calender.event','doctor_id',string="Unavailable Events")

    class GenerateScheduleWizardModel(models.TransientModel):
        _name = "generate.schedule.wizard.model"

        start_date = fields.Date("Start Date")
        end_date = fields.Date("End Date")

        def generate_schedule_wizard_method(self):
            doctor_id = self.env.context.get("default_doctor_list_model_id")
            self.env["doctor.working.hours.slot"].search(
                [("doctor_id", "=", doctor_id)]
            )
            doctor_record = self.env["doctor.list.model"].search(
                [("id", "=", doctor_id)], limit=1
            )
            # start_date_object = datetime.strptime(self.start_date,'%Y-%m-%d')
            day_index = self.start_date.weekday()

            # this below is for generating date schedule
            date_difference = (self.end_date - self.start_date).days
            current_date = self.start_date
            date_list = []
            for _ in range(date_difference):
                date_list.append(current_date + timedelta(days=1))
                current_date = current_date + timedelta(days=1)
            print(f"The date difference is {date_difference}")
            print(f"The date list for schedule are  {date_list}")

            # this below is for generating the schedule for required time gap
            for date in date_list:
                record_to_delete = self.env["appointment.schedule.model"].search(
                    [('doctor_id', '=', doctor_record.id), ('date', '=', date)])
                record_to_delete.unlink()
                day_name = date.strftime("%A").lower()
                print(f"The day name are :{day_name}")
                search = self.env["doctor.working.hours"].search(
                    [
                        ("doctor_id", "=", doctor_id),
                        # ("working_schedule_ids.day_of_week", "=", day_name),
                    ]
                )
                # print("doctors_ids",search)
                # search=search.working_schedule_ids.search([('day_of_week','=',day_name)],limit=1)
                print(search.working_schedule_ids.slot_ids)
                for reco in search.working_schedule_ids:
                    if reco.day_of_week==day_name:
                        for sl in reco.slot_ids:
                            self.env["appointment.schedule.model"].create(
                                            {
                                                "date": date,
                                                "day": sl.day_of_week,
                                                "doctor_id": doctor_record.id,
                                                "slot_start_time": sl.slot_start_time,
                                                "slot_end_time": sl.slot_end_time,
                                            }
                                        )
                    else:
                        pass

            #     doctor_record = self.env["doctor.list.model"].search(
            #         [("id", "=", doctor_id)], limit=1
            #     )
            #     record_to_delete = self.env["appointment.schedule.model"].search(
            #     [('doctor_id', '=', doctor_record.id), ('date', '=', date)])
            #     record_to_delete.unlink()
            #     for rec in response:
            #         print(f"DOctor Record is {doctor_record}")
            #         print(f"DOctor Record is {doctor_record}")
            #         print(f"DOctor Record is {doctor_record}")
            #         print(f"DOctor Record is {doctor_record}")
            #         if doctor_record:
            #             self.env["appointment.schedule.model"].create(
            #                 {
            #                     "date": date,
            #                     "day": rec.day_of_week,
            #                     "doctor_id": doctor_record.id,
            #                     "slot_start_time": rec.slot_start_time,
            #                     "slot_end_time": rec.slot_end_time,
            #                 }
            #             )
            #         else:
            #             # Handle the case where the doctor record is not found based on the given doctor_id
            #             pass  # You might want to log an error or handle it in some way
            # print(f"The returned records are {response}")


class HospitalLocation(models.Model):
    _name = "hospital.location"
    _description = "Hospital Location"
    _rec_name = "hospital_name"

    hospital_name = fields.Char("Hospital Name")
    hospital_location = fields.Char("Location")


class TimeZone(models.Model):
    _name = "timezone.model"
    _rec_name = "tz"

    tz = fields.Char("TimeZone")


# class ResourceCalender(models.Model):
#     _inherit = 'calender.event'

#     doctor_id = fields.Many2one('doctor.list.model','Doctor')
#     unavailable_dates = fields.Many2many('calendar.event', 'unavailable_dates_rel', 'doctor_id', 'event_id', string='Unavailable Dates')


class UnavailableDate(models.Model):
    _name = "doctor.unavailable.date"
    _rec_name = "start_date"

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    unavailable_date = fields.Date("Unavailable Date")
    is_half_day = fields.Boolean("Half Day")
    duration = fields.Float("Duration(In Days)", compute="_compute_duration")

    @api.depends("start_date", "end_date")
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                start_date_object = rec.start_date
                end_date_object = rec.end_date
                diff = end_date_object - start_date_object
                if diff.days == 0:
                    rec.duration = 1
                else:
                    rec.duration = diff.days
            else:
                rec.duration = 0

    @api.onchange("is_half_day", "unavailable_date")
    def _onchange_is_half_day(self):
        if self.is_half_day and self.unavailable_date:
            self.start_date = self.unavailable_date
            self.end_date = self.unavailable_date
            self.duration = 1
        else:
            pass

            # Execute your method or logic here


class DoctorDates(models.Model):
    _name = "doctor.dates"

    doctor_id = fields.Many2one("doctor.list.model", string="Doctor")
    unavailable_dates = fields.Many2many(
        "doctor.unavailable.date", string="Doctor Unavailable Dates"
    )
    # all_unavailable_dates = fields.

    @api.constrains("unavailable_dates")
    def check_validity(self):
        for record in self:
            doctor_id = record.doctor_id
            print(f"Tbe doctor id is {doctor_id}")
            date_set = record.unavailable_dates
            date_list = date_set.filtered(lambda x: x.start_date and x.end_date)
            print(date_list)
            date_dict = {}
            for date_record in date_list:
                print(
                    f"Start Date is {date_record.start_date} and End date is {date_record.end_date}"
                )
                date_key = (date_record.start_date, date_record.end_date)
                print(f"Data Key is {date_key}")
                value = date_dict.get(date_key)
                print(f"Tne duplicate key is {value}")
                if date_key in date_dict:
                    raise ValidationError(
                        "Duplicate Start Date and end Date for the same doctor"
                    )
                date_dict[date_key] = doctor_id.id
                print(f"Data dictionary is {date_dict}")

    @api.model
    def get_unavailable_dates(self, doctor_id):
        print(f"The doctor id is {doctor_id}")
        unavailable_date_ref = self.search([("doctor_id", "=", doctor_id)])
        doctor_unavailable_set = unavailable_date_ref.unavailable_dates
        doctor_unavailable_recordset = doctor_unavailable_set.filtered(
            lambda x: x.start_date and x.end_date
        )
        date_list=[]
        new_sorted_array=[]
        unavailable_date_list = []
        for rec in doctor_unavailable_recordset:
            if rec.start_date:
                unavailable_date_list.append(rec.start_date)
            if rec.end_date:
                unavailable_date_list.append(rec.end_date)

            # # set is used for getting the unique list of dates
            if rec.duration:
                date_list = [
                    date
                    for record in doctor_unavailable_set
                    for date in (
                        record.start_date + timedelta(days=i)
                        for i in range(int(record.duration))
                    )
                ]
        if date_list:
            unique_unavailable_dates = sorted(set(date_list))
            new_sorted_array = sorted(set(unavailable_date_list + unique_unavailable_dates))
            print(f"The date list is {new_sorted_array}")
        return new_sorted_array
        # print(f'The unique dates are as follows {unique_unavailable_dates}')


# class WorkingHours(models.Model):
#     _name = 'doctor.working.hours'
#     _description = 'Doctor Working Hours'


#     doctor_id = fields.Many2one('doctor.list.model','Doctor',required=True,unique=True)
#     working_hour_name = fields.Char("Working Time Info")
#     working_hours_id = fields.One2many('working.date','doctor_working_hours_id')

#     @api.constrains('doctor_id')
#     def check_doctor_uniqueness(self):
#         for record in self:
#             if self.search_count([('doctor_id','=',record.doctor_id.id)]) > 1:
#                 raise ValidationError("Error!! Doctor already has assigned working hours...")

# class WorkingDate(models.Model):
#     _name = 'working.date'
#     _description = 'Working Date'

#     @api.model
#     def get_week_days(self):
#         return [
#             ('0','Sunday'),
#             ('1','Monday'),
#             ('2','Tuesday'),
#             ('3','Wednesday'),
#             ('4','Thursday'),
#             ('5','Friday'),
#             ('6','Saturday'),
#         ]
#     day = fields.Selection(selection=get_week_days,default='0',string='Day',required=True)
#     start_hour = fields.Float(string="Work From",required=True,index=True,
#                               help="Start and End time of Working"
#                               )
#     end_hour = fields.Float(string="Work to",required=True)
#     doctor_working_hours_id = fields.Many2one('doctor.working.hours')

#     @api.onchange('start_hour','end_hour')
#     def _onchange_work_hours(self):
#         # avoid negativepr after midnight work hours
#         self.start_hour = min(self.start_hour,23.99)
#         self.start_hour = max(self.start_hour,0.0)
#         self.end_hour = min(self.end_hour,24)
#         self.end_hour = max(self.end_hour,0.0)

#         self.end_hour = max(self.start_hour,self.end_hour)

#     @api.constrains('start_hour','end_hour')
#     def check_hour_value(self):
#         if(self.end_hour <= self.start_hour ):
#             raise ValueError("Start And End time cannot be less or even match")


# class SlotDefine(models.Model):
#     _name ='slot.define.model'

#     doctor_id = fields.Many2one('doctor.list.model')
#     slot_duration = fields.Float("Slot Duration",default="")
#     # available_slots = fields.Many2many('')

#     @api.onchange('doctor_id','slot_duration')
#     def compute_available_slots(self):
#         if self.doctor_id and self.slot_duration:
#             doctor_working_hours_ref=self.env['doctor.working.hours'].search([
#                 ('doctor_id','=',self.doctor_id.id)
#             ])
#             working_hour_set = doctor_working_hours_ref.working_hours_id
#             working_list = working_hour_set.filtered(lambda x: x.day and x.start_hour and x.end_hour)
#             for rec in working_list:
#                 i_start_value = int(rec.start_hour)
#                 i_start_hour_minutes = (rec.start_hour - i_start_value) * 60
#                 i_end_hour = int(rec.end_hour)
#                 i_end_hour_minutes = (rec.end_hour - i_end_hour) * 60
#                 hour_diff = int(rec.end_hour-rec.start_hour)
#                 min_diff = round(abs(i_end_hour_minutes - i_start_hour_minutes))
#                 slot_interval = int(self.slot_duration)*60 + int((self.slot_duration - int(self.slot_duration))*60)
#                 print(f"The slot interval is {slot_interval}")
#                 total_work_minutes = hour_diff * 60 + min_diff
#                 print(f"The total work minutes is {total_work_minutes}")

#                 #calculate the number of intervals
#                 num_intervals = total_work_minutes // slot_interval

#                 #calculate the remaining time after distributing intervals
#                 remaining_minutes = total_work_minutes % slot_interval

#                 # calculate the duration  of each interval
#                 interval_duration = total_work_minutes // num_intervals
#                 # Convert float to datetime
#                 current_time = datetime.strptime(str(int(rec.start_hour)) + ':' + str(int(i_start_hour_minutes)), '%H:%M')


#                 for i in range(num_intervals):
#                     end_time = current_time + timedelta(minutes=interval_duration)
#                     print(f"The start time is {current_time} and end_time is {end_time}")
#                     current_time = end_time

#                 # current_time = start_time_string
#                 print(f"Current time is {rec.start_hour+self.slot_duration}")
#                 slot_duration = timedelta(minutes=self.slot_duration)


#     # def calculate_time_diff(self,)
#     @api.constrains('slot_duration')
#     def _slot_validation(self):
#                 # Get today's date
#         today = datetime.now().date()

#         #Getting the last appointment date to make view for calender view

#         # Calculate one month from today
#         # default_calender_appointment_d
#         one_month_later = today + timedelta(days=30)

#         # Generate a list of dates from today to one month ahead
#         date_list = [datetime.now().date()+timedelta(days=x) for x in range((one_month_later - today).days + 1)]

#         # Below is for calculating the total number of unavailable dates
#         unavailable_dates = self.env['doctor.dates'].get_unavailable_dates(self.doctor_id.id)
#         holiday_recordset = self.env['set.holiday.model'].search([])
#         holiday_dates_list = holiday_recordset.mapped('holiday_date')

#         total_unavailable_dates = sorted(set(unavailable_dates + holiday_dates_list))

#         # THIS BELOW IS THE TOTAL AVAILABLE LIST OF DATES FOR SPECIFIED PERIOD OF TIME
#         filtered_available_date_list = [date for date in date_list if date not in total_unavailable_dates]
#         print(f"Total total_available_dates dates are :{filtered_available_date_list}")


#         self.env['doctor.dates'].get_unavailable_dates(1)
#         for slot in self:
#             if functions.float_to_time(slot.slot_duration) < '00:00' or functions.float_to_time(slot.slot_duration) > '23:59':
#                 raise ValidationError('The slot value must be between 0.00 and 23.59')

#     @api.model
#     def get_available_doctors(self):
#         pass

#         # print(f"The response i got from backend is {response}")
#         # return response

#     def get_booked_slot(self):
#         appointment_dictionary = {
#             'doctor_id':1,
#             'appointment_date':'',
#             'available_appointment_slots':[],
#             'booked_appointment_slots':[]

#         }
#         appointment_calender_days = 60
#         # Get today's date
#         today = datetime.now().date()

#         # Calculate one month from today
#         one_month_later = today + timedelta(days=30)

#         # Generate a list of dates from today to one month ahead
#         date_list = [datetime.now().date()+timedelta(days=x) for x in range((one_month_later - today).days + 1)]

#         # Print the list of dates
#         print(date_list)


#     # for i in range(appointment_calender_days):
