import frappe
from frappe import _
from frappe.utils import today
from frappe.utils import get_first_day, get_last_day, today
from frappe.utils import cint
from frappe.utils import getdate, now_datetime
from datetime import datetime, timedelta

def validate_session_and_device():
    # Only run check for API requests targeting our attendance_app endpoints
    cmd = frappe.form_dict.get("cmd")
    if cmd and cmd.startswith("hrms.api.attendance_app."):
        # Allow login endpoint to be accessed without session check
        if cmd == "hrms.api.attendance_app.login":
            return

        # 1. Enforce no guest access
        if frappe.session.user == "Guest":
            frappe.throw(_("Session expired or unauthorized access. Please login."), frappe.PermissionError)

        # 2. Enforce device ID match (extra security)
        # Skip device check for Administrator or System Manager
        if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles():
            user_device_id = frappe.db.get_value("User", frappe.session.user, "device_id")
            if user_device_id:
                req_device_id = frappe.get_request_header("X-Device-Id") or frappe.get_request_header("x-device-id")
                if not req_device_id or req_device_id != user_device_id:
                    frappe.throw(_("Access denied. Please access from your authorized mobile device."), frappe.PermissionError)

@frappe.whitelist(allow_guest=True)
def login(email, password, device_id):
    user = frappe.db.get_value("User", {"email": email}, ["name", "device_id"], as_dict=True)

    if not user:
        frappe.throw("Invalid credentials")

    # DEVICE CHECK BEFORE LOGIN
    if user.device_id and user.device_id != device_id:
        frappe.throw("You are already logged in from another mobile. Contact your HR.")

    # NOW authenticate user
    frappe.local.login_manager.authenticate(user=user.name, pwd=password)
    frappe.local.login_manager.post_login()

    # Save device_id first time
    if not user.device_id:
        frappe.db.set_value("User", user.name, "device_id", device_id)

    return {
        "status": "device_match" if user.device_id else "first_login",
        "message": "Logged In",
    }

@frappe.whitelist()
def get_current_user_info() -> dict:
	current_user = frappe.session.user
	user = frappe.db.get_value(
		"User", current_user, ["name", "first_name", "full_name", "user_image"], as_dict=True
	)
	user["roles"] = frappe.get_roles(current_user)

	return user

@frappe.whitelist()
def get_current_employee_info() -> dict:
	current_user = frappe.session.user
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": current_user, "status": "Active"},
		[
			"name",
			"first_name",
			"employee_name",
			"designation",
			"department",
			"company",
			"reports_to",
			"user_id",
			"image",
			"field_employee",
            "skip_location_validation",
            "is_manager",
            "holiday_list"
		],
		as_dict=True,
	)
	return employee

@frappe.whitelist()
def get_all_geofence():
    """
    Return all Geofence records for the logged-in user (linked via User field),
    including location details from its child table Geofence Details.
    """
    user = frappe.session.user  # current logged-in user (email)

    geofences = frappe.get_all(
        "Geofence",
        fields=["name", "user"],
        filters={"user": user},
        limit=999999,
    )

    result = []
    for g in geofences:
        details = frappe.get_all(
            "Geofence Details",
            fields=["location", "latitude", "longitude", "radius"],
            filters={"parent": g.name},
        )
        g["fence"] = details
        result.append(g)

    return result

from frappe.utils import now

@frappe.whitelist()
def create_employee_checkin(
    log_type,
    latitude=None,
    longitude=None,
    device_id=None,
    reference_dn=None,
    reference_dt=None,
    location=None,
    description=None,
):

    employee = get_current_employee_info()

    if not employee:
        return {
            "success": False,
            "message": "Employee not found"
        }

    try:

        checkin_time = now()

        doc = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": employee.name,
            "time": checkin_time,
            "log_type": log_type,
            "latitude": latitude,
            "longitude": longitude,
            "device_id": device_id,
            "reference_dt":reference_dt,
            "reference_dn":reference_dn,
            "location": location,
            "description": description,
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Employee Checkin Created Successfully",
            "name": doc.name,
            "time": checkin_time
        }

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Create Employee Checkin Error"
        )

        return {
            "success": False,
            "message": str(e)
        }

# =========================================================
# Dashboard Summary
# Leave Application, Attendance Request, Present, Absent
# =========================================================

@frappe.whitelist()
def get_dashboard_summary():
	employee = get_current_employee_info()

	if not employee:
		return {}

	employee_name = employee.name

	first_day = get_first_day(today())
	last_day = get_last_day(today())

	return {
		"attendance_request_count": frappe.db.count(
			"Attendance Request",
			{
				"employee": employee_name,
				"from_date": ["between", [first_day, last_day]]
			}
		),

		"leave_application_count": frappe.db.count(
			"Leave Application",
			{
				"employee": employee_name,
				"from_date": ["between", [first_day, last_day]]
			}
		),

		"present_count": frappe.db.count(
			"Attendance",
			{
				"employee": employee_name,
				"status": "Present",
				"attendance_date": ["between", [first_day, last_day]]
			}
		),

		"absent_count": frappe.db.count(
			"Attendance",
			{
				"employee": employee_name,
				"status": "Absent",
				"attendance_date": ["between", [first_day, last_day]]
			}
		)
	}

# =========================================================
# Employee Check-in
# Default Load 10 Records
# =========================================================

@frappe.whitelist()
def get_all_employee_checkin(limit=10, page=1):
	employee = get_current_employee_info()

	if not employee:
		return []

	start = (int(page) - 1) * int(limit)

	return frappe.get_all(
		"Employee Checkin",
		filters={
			"employee": employee.name
		},
		fields=[
			"name",
			"time",
			"log_type",
			"device_id",
			"latitude",
			"longitude",
			"reference_dt",
			"reference_dn",
			"creation"
		],
		order_by="time desc",
		start=start,
		page_length=limit
	)

# =========================================================
# Current Month Attendance
# =========================================================

@frappe.whitelist()
def get_current_month_attendance(start_date=None, end_date=None):
	employee = get_current_employee_info()

	if not employee:
		return []

	if start_date and end_date:
		first_day = start_date
		last_day = end_date
	else:
		first_day = get_first_day(today())
		last_day = get_last_day(today())

	return frappe.get_all(
		"Attendance",
		filters={
			"employee": employee.name,
			"attendance_date": ["between", [first_day, last_day]]
		},
		fields=[
			"name",
			"attendance_date",
			"status",
			"in_time",
			"out_time",
			"working_hours"
		],
		order_by="attendance_date desc"
	)

@frappe.whitelist()
def get_employee_holidays(start_date=None, end_date=None):
	employee = get_current_employee_info()

	if not employee:
		return []

	if not employee.holiday_list:
		return []

	filters = {
		"parent": employee.holiday_list
	}
	if start_date and end_date:
		filters["holiday_date"] = ["between", [start_date, end_date]]

	holidays = frappe.get_all(
		"Holiday",
		filters=filters,
		fields=[
			"holiday_date",
			"description",
			"weekly_off"
		],
		order_by="holiday_date asc"
	)

	return holidays

# =========================================================
# Attendance Requests
# Default Load 10 Records
# =========================================================

@frappe.whitelist()
def get_attendance_requests(limit=10, page=1):

	employee = get_current_employee_info()

	if not employee:
		return []

	start = (int(page) - 1) * int(limit)

	return frappe.get_all(
		"Attendance Request",
		filters={
			"employee": employee.name
		},
		fields=[
			"name",
			"from_date",
			"to_date",
			"reason",
			"explanation",
			"half_day",
			"docstatus",
			"creation"
		],
		order_by="creation desc",
		start=start,
		page_length=limit
	)

# =========================================================
# Leave Applications
# Default Load 10 Records
# =========================================================

@frappe.whitelist()
def get_leave_applications(limit=10, page=1):

	employee = get_current_employee_info()

	if not employee:
		return []

	start = (int(page) - 1) * int(limit)

	return frappe.get_all(
		"Leave Application",
		filters={
			"employee": employee.name
		},
		fields=[
			"name",
			"leave_type",
			"from_date",
			"to_date",
			"status",
			"total_leave_days",
			"leave_balance",
			"half_day",
			"description",
			"creation"
		],
		order_by="creation desc",
		start=start,
		page_length=limit
	)

@frappe.whitelist()
def create_attendance_request(
    employee,
    reason,
    from_date,
    to_date,
    explanation=None
):
    try:
        doc = frappe.get_doc({
            "doctype": "Attendance Request",
            "employee": employee,
            "reason": reason,
            "from_date": from_date,
            "to_date": to_date,
            "explanation": explanation
        })

        doc.insert(ignore_permissions=True)

        return {
            "success": True,
            "message": "Attendance Request Created Successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Create Attendance Request Error"
        )

        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def create_leave_application(
    employee,
    leave_type,
    from_date,
    to_date,
    half_day=0,
    description=None
):
    try:
        doc = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": employee,
            "leave_type": leave_type,
            "from_date": from_date,
            "to_date": to_date,
            "half_day": cint(half_day),
            "half_day_date": from_date if cint(half_day) else None,
            "description": description
        })

        doc.insert(ignore_permissions=True)

        return {
            "success": True,
            "message": "Leave Application Created Successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Create Leave Application Error"
        )

        return {
            "success": False,
            "message": str(e)
        }

# HR Settings
@frappe.whitelist()
def get_hr_settings() -> dict:
	settings = frappe.db.get_singles_dict("HR Settings", cast=True)
	return frappe._dict(
		allow_multi_face_check_in=settings.allow_multi_face_check_in,
		not_validate_geolocation=settings.not_validate_geolocation,
	)


@frappe.whitelist()
def get_leave_types():

    employee = get_current_employee_info()

    if not employee:
        return []

    from hrms.hr.doctype.leave_application.leave_application import get_leave_details
    from frappe.utils import today

    leave_details = get_leave_details(
        employee.name,
        today()
    )

    allocation = leave_details.get(
        "leave_allocation",
        {}
    )

    res = []

    has_lwp = False

    for leave_type, details in allocation.items():

        if leave_type == "Leave Without Pay":
            has_lwp = True

        res.append({
            "leave_type": leave_type,
            "remaining_leaves": details.get(
                "remaining_leaves",
                0.0
            ),
            "total_leaves": details.get(
                "total_leaves",
                0.0
            )
        })

    if not has_lwp:

        res.append({
            "leave_type": "Leave Without Pay",
            "remaining_leaves": 9999.0,
            "total_leaves": 9999.0
        })

    return res

@frappe.whitelist()
def get_hr_settings():
	return frappe.db.get_value("HR Settings", None, ["not_validate_geolocation"], as_dict=True)

@frappe.whitelist()
def get_map_config():
    from hrms.api.runtime_config import get_frontend_config, get_map_urls
    config = get_frontend_config()
    urls = get_map_urls()
    return {
        "azure_key": config.get("AZURE_KEY"),
        "distance_url": urls.get("distance_url"),
        "distance_response": urls.get("distance_response"),
        "location_url": urls.get("location_url"),
        "location_response": urls.get("location_response")
    }

# -------------------- GET ALL --------------------
@frappe.whitelist()
def get_all_branch(search_term="", limit=20):
    try:
        filters = {}
        if search_term:
            docs = frappe.get_all("Branch", fields=["*"], or_filters=[
                ["Branch", "name", "like", f"%{search_term}%"],
                ["Branch", "branch", "like", f"%{search_term}%"]
            ], limit=limit, ignore_permissions=True)
        else:
            docs = frappe.get_all("Branch", fields=["*"], limit=limit, ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "branch - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch branch records"}

@frappe.whitelist()
def get_all_customers(search_term="", limit=20):
    try:
        if search_term:
            docs = frappe.get_all("Customer", fields=["*"], or_filters=[
                ["Customer", "name", "like", f"%{search_term}%"],
                ["Customer", "customer_name", "like", f"%{search_term}%"],
                ["Customer", "customer_type", "like", f"%{search_term}%"]
            ], limit=limit, ignore_permissions=True)
        else:
            docs = frappe.get_all("Customer", fields=["*"], limit=limit, ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Customer - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch Customer records"}
    
@frappe.whitelist()
def create_customer(**kwargs):
    try:
        doc = frappe.new_doc("Customer")
        for key, value in kwargs.items():
            doc.set(key, value)

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "data": doc
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer - Create Error")
        frappe.local.response["http_status_code"] = 500

        return {
            "success": False,
            "message": str(e)   #  exact error message
        }
 
# -------------------- GET ALL --------------------
@frappe.whitelist()
def get_all_lead(search_term="", limit=20):
    try:
        if search_term:
            docs = frappe.get_all("Lead", fields=["*"], or_filters=[
                ["Lead", "name", "like", f"%{search_term}%"],
                ["Lead", "first_name", "like", f"%{search_term}%"],
                ["Lead", "mobile_no", "like", f"%{search_term}%"],
                ["Lead", "salutation", "like", f"%{search_term}%"]
            ], limit=limit, ignore_permissions=True)
        else:
            docs = frappe.get_all("Lead", fields=["*"], limit=limit, ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Lead - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch Lead records"}

# -------------------- CREATE --------------------

@frappe.whitelist()
def create_lead(**kwargs):
    try:
        doc = frappe.new_doc("Lead")
        for key, value in kwargs.items():
            doc.set(key, value)

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "data": doc
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Lead - Create Error")
        frappe.local.response["http_status_code"] = 500

        return {
            "success": False,
            "message": str(e)   #  exact error message
        }


@frappe.whitelist()
def get_all_opportunity(search_term="", limit=20):
    try:
        if search_term:
            docs = frappe.get_all("Opportunity", fields=["*"], or_filters=[
                ["Opportunity", "name", "like", f"%{search_term}%"],
                ["Opportunity", "party_name", "like", f"%{search_term}%"],
                ["Opportunity", "opportunity_from", "like", f"%{search_term}%"]
            ], limit=limit, ignore_permissions=True)
        else:
            docs = frappe.get_all("Opportunity", fields=["*"], limit=limit, ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Opportunity - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch Opportunity records"}


@frappe.whitelist()
def create_opportunity(**kwargs):
    try:
        doc = frappe.new_doc("Opportunity")
        for k, v in kwargs.items():
            doc.set(k, v)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "data": doc}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Opportunity - Create Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to create Opportunity"}


@frappe.whitelist()
def create_checkin_journey(**kwargs):
    try:
        doc = frappe.new_doc("Checkin Journey")
        doc.update(kwargs)
        doc.insert(ignore_permissions=True)
        return {
            "success": True,
            "data": doc
        }
 
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "CheckIn Journey - Create Error") 
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def get_all_hospital():
    try:
        docs = frappe.get_all("Hospital", fields=["*"], ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Hospital - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch Hospital records"}
 
@frappe.whitelist()
def get_all_car():
    try:
        docs = frappe.get_all("CAR", fields=["*"], ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "CAR - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch CAR records"}
     
 
