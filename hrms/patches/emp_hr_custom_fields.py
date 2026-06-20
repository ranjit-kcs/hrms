import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    create_custom_fields(
        {

            "Employee":[

                {
                    "fieldname": "skip_location_validation",
                    "fieldtype": "Check",
                    "label": "Skip Location Validation",
                    "insert_after": "field_employee",
                }

            ],
            "HR Settings":[
                {
                    "fieldname": "not_validate_geolocation",
                    "fieldtype": "Check",
                    "label": "Not Validate Geolocation",
                    "insert_after": "allow_geolocation_tracking",
                }
            ]
        }
    )