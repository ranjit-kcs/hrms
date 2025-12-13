from collections.abc import Generator

import requests

import frappe
from frappe.utils import add_days, date_diff

import os
import json

country_info = {}


@frappe.whitelist(allow_guest=True)
def get_country(fields=None):
	global country_info
	ip = frappe.local.request_ip

	if ip not in country_info:
		fields = ["countryCode", "country", "regionName", "city"]
		res = requests.get(
			"https://pro.ip-api.com/json/{ip}?key={key}&fields={fields}".format(
				ip=ip, key=frappe.conf.get("ip-api-key"), fields=",".join(fields)
			)
		)

		try:
			country_info[ip] = res.json()

		except Exception:
			country_info[ip] = {}

	return country_info[ip]


def get_date_range(start_date: str, end_date: str) -> list[str]:
	"""returns list of dates between start and end dates"""
	no_of_days = date_diff(end_date, start_date) + 1
	return [add_days(start_date, i) for i in range(no_of_days)]


def generate_date_range(start_date: str, end_date: str, reverse: bool = False) -> Generator[str, None, None]:
	no_of_days = date_diff(end_date, start_date) + 1

	date_field = end_date if reverse else start_date
	direction = -1 if reverse else 1

	for n in range(no_of_days):
		yield add_days(date_field, direction * n)


def get_employee_email(employee_id: str) -> str | None:
	employee_emails = frappe.db.get_value(
		"Employee",
		employee_id,
		["prefered_email", "user_id", "company_email", "personal_email"],
		as_dict=True,
	)

	return (
		employee_emails.prefered_email
		or employee_emails.user_id
		or employee_emails.company_email
		or employee_emails.personal_email
	)

from frappe.utils import get_site_path

def update_frontend_settings(doc, method):
    print("function is working")

    # Get value safely
    value = frappe.db.get_single_value("System Settings", "azure_key_") or ""

    # ✅ WRITE TO SITE PUBLIC FOLDER (NOT apps/)
    file_path = get_site_path("public", "hrms", "settings.env")

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write content
    content = f"AZURE_KEY={value}\n"
    with open(file_path, "w") as f:
        f.write(content)

    print("Updated file:", file_path)