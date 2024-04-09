# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime
# from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import json
import base64


# class AuthSignupInheritValues(AuthSignupHome):
#     @http.route("/web/signup", type="http", auth="public", website=True, sitemap=False)
#     def web_auth_signup(self, *args, **kw):
#         qcontext = self.get_auth_signup_qcontext()
#         response = super(AuthSignupInheritValues, self).web_auth_signup(*args, **kw)
#         user = (
#             request.env["res.users"]
#             .sudo()
#             .search([("login", "=", qcontext.get("login"))])
#         )
#
#         organization_model = request.env["organization.account"].sudo().search([])
#         company = request.env["res.company"].sudo().search([])
#         if request.httprequest.method == "POST":
#             if kw.get("org_type"):
#                 org_type = kw.get("org_type")
#                 org_type_int = int(org_type)
#                 employee_size = kw.get("employee_size")
#                 industry = kw.get("industry")
#                 additional_fields = {
#                     "organization_type": org_type_int,
#                     "employee_size": employee_size,
#                     "industry": industry,
#                     "is_company": True,
#                 }
#                 user.sudo().write(additional_fields)
#                 org_type_str = kw.get("org_type")
#                 organization_model.sudo().create(
#                     {
#                         "organization_name": kw.get("name"),
#                         "email": kw.get("login"),
#                         "phone": kw.get("phone"),
#                         "organization_type": int(org_type_str),
#                         "employee_size": kw.get("employee_size"),
#                         "industry": kw.get("industry"),
#                         "city": kw.get("city"),
#                         "street": kw.get("street"),
#                         "zip": kw.get("zip"),
#                     }
#                 )
#                 company.sudo().create(
#                     {
#                         "name": kw.get("name"),
#                         "email": kw.get("login"),
#                         "phone": kw.get("phone"),
#                     }
#                 )
#                 template = request.env.ref(
#                     "auth_signup.mail_template_user_signup_account_created",
#                     raise_if_not_found=False,
#                 )
#                 return self.web_login(*args, **kw)
#
#         return request.render(
#             "mental_health.signup_page",
#             {},
#         )
#

class MentalHealth(http.Controller):
    # GET: /user/dashboard
    @http.route(
        ["/dashboard", "/user/dashboard","/my"], auth="user", website=True, csrf=False
    )
    def user_dashboard(self,uid=0,**kw):
        user=request.env.user
        display=False
        doctor=False
        is_in_group=user.has_group('mental_health.company_group')
        if (is_in_group):
            display=True
        is_in_doctor=user.has_group('mental_health.doctor_group')
        if (is_in_doctor):
            doctor=True
        uid=int(uid)
        show=False
        if uid==0:
            user_details = {
                "user_name": http.request.env.user.partner_id.name,
                "user_email": http.request.env.user.partner_id.email,
                "user_phone": http.request.env.user.partner_id.phone,
                "user_city": http.request.env.user.partner_id.city,
                "user_street": http.request.env.user.partner_id.street,
                "user_postcode": http.request.env.user.partner_id.zip,
            }
            show=True
            editable=True
        elif uid>0:
            org_id=http.request.env.user.id
            organization_account = request.env['organization.account'].sudo().search([('associated_user', '=', org_id)])
            res_user= request.env['res.users'].sudo().search([('id','=',uid)])
            if res_user.organization_account.id == organization_account.id:
                show=True
            user_details={
                "user_name": res_user.partner_id.name,
                "user_email": res_user.partner_id.email,
                "user_phone": res_user.partner_id.phone,
                "user_city": res_user.partner_id.city,
                "user_street": res_user.partner_id.street,
                "user_postcode": res_user.partner_id.zip,
            }
            editable=False
        patient_id = (
            request.env["patient.personal.info"]
            .sudo()
            .search([("email", "=", user_details["user_email"])])
        )
        search_domain = [
            ("patient_ref", "=", patient_id.id),
            ("requested_appointment_date", ">=", datetime.now().strftime("%Y-%m-%d")),
            ("state", "!=", "served"),
        ]
        appoint_model = request.env["book.appointment"].sudo().search(search_domain)

        search_domain_history = [
            ("patient_ref", "=", patient_id.id),
            # ("requested_appointment_date", "<", datetime.now().strftime("%Y-%m-%d")),
            ("state",'=','served')
        ]
        appoint_history = (
            request.env["book.appointment"].sudo().search(search_domain_history)
        )
        companies=request.env["res.company"].sudo().search([])
        user=request.env.user.id
        associated_user=request.env['organization.account'].sudo().search([('associated_user','=',user)])
        print(associated_user)
        employees=[]
        if associated_user:
            employees=request.env['res.users'].sudo().search([('organization_account','=',associated_user.id)])
        print(editable)
        print(doctor)
        appointments_for_doctor=[]
        served=[]
        accepted_appointments=[]
        if doctor==True:
            doctor_user_email=request.env.user.login
            doctor_detail=request.env['doctor.list.model'].sudo().search([('contact_email','=',doctor_user_email)])
            appointments_for_doctor=request.env['book.appointment'].sudo().search([('doctor_model_id','=',doctor_detail.id),('state','=','draft')])
            served=request.env['book.appointment'].sudo().search([('doctor_model_id','=',doctor_detail.id),('state','=','served') ])
            accepted_appointments=request.env['book.appointment'].sudo().search([('doctor_model_id','=',doctor_detail.id),('state','=','approved')])
        return request.render(
            "mental_health.user_dashboard_template",
            {
                "user_details": user_details,
                "appoint_model": appoint_model,
                "appoint_history": appoint_history,
                "companies":companies,
                "employees":employees,
                "edit":editable,
                "show":show,
                "disp":display,
                "doct":doctor,
                "appointments":appointments_for_doctor,
                "served":served,
                "accepted":accepted_appointments
            },
        )

    @http.route('/patient_history',auth="user",website=True, csrf=False)
    def patient_history(self,id=0,**kw):
        id=int(id)
        if id > 0:
            user = request.env.user
            doctor=False
            is_in_doctor = user.has_group('mental_health.doctor_group')
            if (is_in_doctor):
                doctor=True
                patient=request.env['patient.personal.info'].sudo().search([('id','=',id)])
                if patient:
                    is_associated=request.env['book.appointment'].sudo().search([('doctor_model_id.contact_email','=',user.login),('patient_ref.email','=',patient.email),('state','!=','reject')])
                    if  len(is_associated)>0:
                        appoint_history=request.env['book.appointment'].sudo().search([('doctor_model_id.contact_email','=',request.env.user.login),('patient_ref.email','=',patient.email),('state','=','served')])
                        print("show detail")
                        return request.render("mental_health.show_patient_history",{'patient':patient,'appoint_history':appoint_history})
    @http.route('/submit/save_changes', methods=['POST'], csrf=False, auth='user', website=True)
    def save_changes(self, **post):
        user=request.env.user.id
        organization_account=request.env['organization.account'].sudo().search([('associated_user','=',user)])
        associated_company=organization_account.associate_company
        partner=request.env.user.partner_id
        organization_account.sudo().write({
            'organization_name':post.get("name"),
            'phone':post.get("phone"),
            'city':post.get("city"),
            'street':post.get("street"),
            'zip':post.get("zip")
        })
        associated_company.sudo().write({
            'name':post.get("name"),
            'phone':post.get("phone"),
            'city':post.get("city"),
            'street':post.get("street"),
            'zip':post.get("zip")
        })
        partner.sudo().write({
            'name': post.get("name"),
            'phone': post.get("phone"),
            'city': post.get("city"),
            'street': post.get("street"),
            'zip': post.get("zip")
        })
        associat_user=request.env.user
        associat_user.sudo().write({
            'name': post.get("name"),
            'phone': post.get("phone"),
            'city': post.get("city"),
            'street': post.get("street"),
            'zip': post.get("zip")
        })
        return request.redirect('/dashboard')
    @http.route('/submit/new_employee', methods=['POST'], csrf=False, auth='user', website=True)
    def create_employee(self,**post):
        user=request.env.user.id
        partner=request.env.user.partner_id.id
        company=request.env['res.company'].sudo().search([('partner_id','=',partner)])
        name=post.get("name")
        email=post.get("email")
        phone=post.get("phone")
        city=post.get("city")
        street=post.get("street")
        zip=post.get("zip")
        dublicate=request.env['res.users'].sudo().search([('login','=',email)])
        if dublicate:
            return request.redirect('/dashboard')
        # company_ids=request.httprequest.form.getlist('company_ids')
        associated_user=request.env['organization.account'].sudo().search([('associated_user','=',user)])
        print(associated_user)
        # print(company_ids)
        print(email)

        new_user=request.env['res.users'].sudo().create({
            'login':email,
            'name':name,
            'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
            'phone':phone,
            'email':email,
            'city':city,
            'street':street,
            'zip':zip,
            # 'company_ids':[(6,0,company_ids)],
            'company_id':company.id,
            'organization_account':associated_user.id,
        })
        print(new_user.id)
        associated_user.sudo().write({
            'org_users_page': [(4, new_user.id, 0)]
        })
        return request.redirect("/dashboard")

    # @http.route('/associated_employee_dashboard', auth='user', website=True)
    # def associated_employee_dashboard(self,id=0, **kw):
    #
    #     return request.render("mental_health.associated_employee_dashboard",{})
    @http.route('/mental_health/unlink_user', type='json', auth='user')
    def unlink_user(self, user_id):
        model = request.env['res.users']
        result = model.unlink_user(user_id)
        return {'success': result}
    # GET: /find-doctor
    @http.route(["/find-doctors", "/doctors"], auth="public", website=True, csrf=False)
    def find_doctor(self, **kw):
        doctors_all = request.env["doctor.list.model"].sudo().search([])
        doctors = doctors_all.read(
            ["doctor_full_name", "profile_picture", "specialty", "id"]
        )

        return request.render("mental_health.find_doctor", {"doctors": doctors})

    # GET: /doctor/<int:id>
    @http.route("/doctor/<int:id>", auth="public", website=True, csrf=False)
    def find_doctor_id(self, id, **kw):
        doctor = (
            request.env["doctor.list.model"].sudo().search([("id", "=", id)], limit=1)
        )
        doctor_details = doctor.read(
            [
                "doctor_full_name",
                "profile_picture",
                "specialty",
                "id",
                "qualifications",
                "contact_phone",
                "contact_email",
                "office_address",
                "availability",
                "experience_years",
                "work_experience",
            ]
        )

        available_dates = (
            request.env["doctor.working.hours.slot"]
            .sudo()
            .get_specified_doctor_available_dates(id)
        )
        formatted_dates = [date.strftime("%Y/%m/%d") for date in available_dates]
        return request.render(
            "mental_health.doctor_profile_template",
            {
                "doctor_details": doctor_details,
                "formatted_dates": formatted_dates,
            },
        )

    # GET: /schedule-an-appointment/<int:id>
    @http.route(
        "/schedule-an-appointment/<int:id>",
        auth="public",
        website=True,
        csrf=False,
        cors="*",
    )
    def make_an_appointment(self, id, **kw):
        doctor = (
            request.env["doctor.list.model"].sudo().search([("id", "=", id)], limit=1)
        )
        doctor_details = doctor.read(
            [
                "doctor_full_name",
                "profile_picture",
                "specialty",
                "id",
                "qualifications",
                "contact_phone",
                "contact_email",
                "office_address",
                "availability",
                "experience_years",
                "work_experience",
            ]
        )
        time_slots = (
            request.env["appointment.schedule.model"]
            .sudo()
            .search(
                [
                    ("doctor_id", "=", id),
                    ("date", "=", "01/08/2024"),
                    ("slot_status", "=", "not_booked"),
                ]
            )
        )

        available_dates = (
            request.env["doctor.working.hours.slot"]
            .sudo()
            .get_specified_doctor_available_dates(id)
        )
        formatted_dates = [date.strftime("%Y/%m/%d") for date in available_dates]

        return request.render(
            "mental_health.schedule_an_appointment_template",
            {
                "doctor": doctor,
                "formatted_dates": formatted_dates,
                "time_slots": time_slots,
            },
        )

    # GET: /org-types
    @http.route(
        "/org-types/",
        type="http",
        methods=["GET"],
        auth="public",
        website=True,
        csrf=False,
        cors="*",
    )
    def get_org_types(self, **kw):
        organization_type = request.env["organization.type"].sudo().search([])
        print(organization_type)
        if organization_type:
            organization_type_serialized = organization_type.read(["type"])
            return http.Response(
                json.dumps(organization_type_serialized),
                content_type="application/json",
            )
        # return http.Response(
        #     json.dumps(
        #         {
        #             "organization_type": None,
        #         }
        #     ),
        #     content_type="application/json",
        # )

    # GET: /available-time-slots/<date>
    @http.route(
        "/available-time-slots/",
        type="http",
        methods=["POST"],
        auth="public",
        website=True,
        csrf=False,
        cors="*",
    )
    def available_time_slots(self, **kw):
        date = kw.get("date")
        doc_id = kw.get("doc_id")

        time_slots = (
            request.env["appointment.schedule.model"]
            .sudo()
            .search(
                [
                    ("doctor_id", "=", int(doc_id)),
                    ("date", "=", date),
                    ("slot_status", "=", "not_booked"),
                ]
            )
        )
        for ts in time_slots:
            print(ts.slot_start_time)
        serialized_slots = time_slots.read(["slot_start_time", "slot_end_time"])

        if time_slots:
            return http.Response(
                json.dumps(serialized_slots),
                content_type="application/json",
            )
        return http.Response(
            json.dumps(
                {
                    "time_slot": 0,
                }
            ),
            content_type="application/json",
        )

    # Appointment schedule form
    @http.route("/book-an-appointment", auth="user", website=True, csrf=False, cors="*")
    def book_an_appointment(self, **kw):
        if request.httprequest.method == "POST":
            slot_id = kw.get("slot_time")
            time_slots = (
                request.env["appointment.schedule.model"]
                .sudo()
                .search(
                    [
                        ("id", "=", int(slot_id)),
                    ],
                    limit=1,
                )
            )

            doctor = (
                request.env["doctor.list.model"]
                .sudo()
                .search([("id", "=", int(kw.get("doctor_id")))], limit=1)
            )
            consultation_type = request.env["consultation.medium"].sudo().search([])
            user_details = {
                "user_name": http.request.env.user.partner_id.name,
                "user_email": http.request.env.user.partner_id.email,
                "user_phone": http.request.env.user.partner_id.phone,
                "user_city": http.request.env.user.partner_id.city,
                "user_street": http.request.env.user.partner_id.street,
                "user_postcode": http.request.env.user.partner_id.zip,
            }
            user_model_domain=[("company_id","=", http.request.env.user.company_id.id),("login","=",http.request.env.user.partner_id.email)]
            user_model=request.env['res.users'].sudo().search(user_model_domain)
            form_data = {
                "doctor_fullname": doctor.doctor_full_name,
                "doctor_image": doctor.profile_picture,
                "doctor_id": doctor.id,
                "org_name":user_model.company_id.name,
                "appoint_date": kw.get("schedule_date"),
                "appoint_slot_start": time_slots.slot_start_time,
                "appoint_slot_end": time_slots.slot_end_time,
                "consultation_type": consultation_type,
                "slot_id": slot_id,
            }
            
            # print(form_data)
            return request.render(
                "mental_health.appointment_form_template",
                {"form_data": form_data, "user_details": user_details},
            )

        return request.render("mental_health.homepage", {})

    # POST: booking information
    @http.route(
        "/book-an-appointment-now", auth="public", website=True, csrf=False, cors="*"
    )
    def book_an_appointment_now(self, **kw):
        appointment_model = request.env["book.appointment"].sudo().search([])
        patient_model = request.env["patient.personal.info"].sudo().search([])

        if request.httprequest.method == "POST":
            slot_id = kw.get("slot_id")
            time_slots = (
                request.env["appointment.schedule.model"]
                .sudo()
                .search(
                    [
                        ("id", "=", int(slot_id)),
                    ],
                    limit=1,
                )
            )
            doctor = (
                request.env["doctor.list.model"]
                .sudo()
                .search([("id", "=", int(kw.get("doctor_id")))], limit=1)
            )
            user_details = {
                "user_name": http.request.env.user.partner_id.name,
                "user_email": http.request.env.user.partner_id.email,
                "user_phone": http.request.env.user.partner_id.phone,
                "user_city": http.request.env.user.partner_id.city,
                "user_street": http.request.env.user.partner_id.street,
                "user_postcode": http.request.env.user.partner_id.zip,
            }
            form_data = {
                "doctor_fullname": doctor.doctor_full_name,
                "appoint_date": kw.get("schedule_date"),
                "appoint_slot_start": time_slots.slot_start_time,
                "appoint_slot_end": time_slots.slot_end_time,
                "slot_id": slot_id,
            }

            appointment_type = kw.get("appointment_type")
            consult_type = kw.get("consult_type")
            consult_medium = kw.get("consult_medium")
            gender = kw.get("gender")
            gp_referral = kw.get("gp")
            gp_referral_attachment = gp_referral.read()
            if gp_referral is None or gp_referral.filename == "":
                gp_referral_attachment = None
            else:
                gp_referral_attachment = base64.b64encode(gp_referral_attachment)

            domain = [("email", "=", http.request.env.user.partner_id.email)]
            is_patient_already_registered = (
                request.env["patient.personal.info"].sudo().search_count(domain)
            )
            # Creating patient if doesn't exist before creating a new appointment
            if not is_patient_already_registered:
                parsed_dob_date = datetime.strptime(kw.get("dob"), "%m/%d/%Y")
                formatted_dob_date = parsed_dob_date.strftime("%Y-%m-%d")
                patient_record = {
                    "patient_name": http.request.env.user.partner_id.name,
                    "date_of_birth": formatted_dob_date,
                    "gender": gender,
                    "email": http.request.env.user.partner_id.email,
                    "mobile": http.request.env.user.partner_id.phone,
                    "address": http.request.env.user.partner_id.city,
                    "street": http.request.env.user.partner_id.street,
                    "post_code": http.request.env.user.partner_id.zip,
                }

                is_patient_created = patient_model.sudo().create(patient_record)

            current_patient_domain = [
                ("email", "=", http.request.env.user.partner_id.email)
            ]
            current_patient_ = (
                request.env["patient.personal.info"]
                .sudo()
                .search(current_patient_domain)
            )
            parsed_appoint_date = datetime.strptime(kw.get("schedule_date"), "%m/%d/%Y")
            formatted_appoint_date = parsed_appoint_date.strftime("%Y-%m-%d")
            appointment_record = {
                "patient_ref": current_patient_.id,
                "appointment_type": appointment_type,
                "consult_type": consult_type,
                "consultation_medium": consult_medium,
                "doctor_model_id": int(kw.get("doctor_id")),
                "requested_appointment_date": formatted_appoint_date,
                "appointment_slot_start_time": time_slots.slot_start_time,
                "appointment_slot_end_time": time_slots.slot_end_time,
                "gp_referall_doc": gp_referral_attachment,
            }

            new_appointment = request.env['book.appointment'].sudo().create(appointment_record)

        return http.request.redirect("/dashboard")

    @http.route("/", auth="public", website=True, csrf=False)
    def index(self, **kw):
        return request.render("mental_health.homepage", {})

    @http.route("/services", auth="public", website=True, csrf=False)
    def services(self, **kw):
        return request.render("mental_health.homepage", {})

    @http.route("/practice_info", auth="public", website=True, csrf=False)
    def practice_info(self, **kw):
        return request.render("mental_health.homepage", {})

    @http.route("/about_us", auth="public", website=True, csrf=False)
    def about_us(self, **kw):
        return request.render("mental_health.homepage", {})

    # @http.route("/book_appointment", auth="public", website=True, csrf=False)
    # def book_appointment(self, **kw):
    #     return request.render("mental_health.book_appointment_template", {})

    @http.route("/contact_us", auth="public", website=True, csrf=False)
    def contact_us(self, **kw):
        return request.render("mental_health.homepage", {})

    # @http.route('/mental_health/mental_health/objects', auth='public')
    # def list(self, **kw):
    #     return http.request.render('mental_health.listing', {
    #         'root': '/mental_health/mental_health',
    #         'objects': http.request.env['mental_health.mental_health'].search([]),
    #     })

    # @http.route('/mental_health/mental_health/objects/<model("mental_health.mental_health"):obj>', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('mental_health.object', {
    #         'object': obj
    #     })
