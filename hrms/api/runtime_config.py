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

