import frappe


# Run-Time Configuration 
@frappe.whitelist()
def get_frontend_config():
    if frappe.session.user == "Guest":
        frappe.throw("Not permitted")

    return {
        "AZURE_KEY": frappe.db.get_single_value(
            "System Settings",
            "azure_key"
        )
    }

@frappe.whitelist()
def get_map_urls():
    if frappe.session.user == "Guest":
        frappe.throw("Not permitted")

    # Fetch API names from System Settings
    distance_api = frappe.db.get_single_value(
        "System Settings", "distance_api"
    )
    location_api = frappe.db.get_single_value(
        "System Settings", "location_api"
    )

    # Fetch Distance API details
    distance_data = frappe.db.get_value(
        "URL Response Fields",
        {"name": distance_api},
        ["url", "response"],
        as_dict=True
    )

    # Fetch Location API details
    location_data = frappe.db.get_value(
        "URL Response Fields",
        {"name": location_api},
        ["url", "response"],
        as_dict=True
    )

    return {
        "distance_url": distance_data.url if distance_data else None,
        "distance_response": distance_data.response if distance_data else None,

        "location_url": location_data.url if location_data else None,
        "location_response": location_data.response if location_data else None,
    }

