import frappe
# from frappe.auth import LoginManager


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
        "home_page": "/hrms/home"
    }



@frappe.whitelist()
def reset_user_device_id(user):
    """Reset the device_id of a user to empty string."""
    # Optional: check permission
    if not frappe.has_permission("User", "write"):
        frappe.throw("Not permitted to reset device ID")

    # Reset the field
    frappe.db.set_value("User", user, "device_id", "")
    frappe.db.commit()

    return {"message": "Device ID reset successfully."}