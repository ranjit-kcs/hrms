import frappe
from frappe.utils import (
    get_first_day,
    get_last_day,
    add_months,
    today,
    flt,
)


@frappe.whitelist()
def calculate_monthly_travel_expenses():

    try:
        prev_month = add_months(today(), -1)
        from_date = get_first_day(prev_month)
        to_date = get_last_day(prev_month)

        frappe.logger().info(f"Travel expense calculation {from_date} → {to_date}")

        journeys = frappe.get_all(
            "Checkin Journey",
            filters={"ec_submitted": 0, "docstatus": 1},
            fields=[
                "name", "employee", "date", "distance",
                "vehicle_type", "checkin_description",
                "checkout_description",
            ],
            order_by="date",
        )

        if not journeys:
            return

        # -------------------------
        # Group Journeys
        # -------------------------
        grouped = {}
        employees = set()

        for j in journeys:

            emp = j.employee
            employees.add(emp)

            month = j.date.strftime("%Y-%m")
            vehicle = (j.vehicle_type or "").capitalize()
            distance = flt(j.distance)

            desc = (
                f"{j.date} | Check-in: {j.checkin_description or 'N/A'} | "
                f"Checkout: {j.checkout_description or 'N/A'} "
                f"({distance:.2f} KM)"
            )

            bucket = grouped.setdefault(emp, {}) \
                .setdefault(month, {}) \
                .setdefault(vehicle, {"dist": 0, "desc": [], "ids": []})

            bucket["dist"] += distance
            bucket["desc"].append(desc)
            bucket["ids"].append(j.name)

        # -------------------------
        # Prefetch Employee + Branch
        # -------------------------
        emp_docs = {
            e.name: e for e in frappe.get_all(
                "Employee",
                filters={"name": ["in", list(employees)]},
                fields=["name", "employee_name", "branch"],
            )
        }

        branches = {e.branch for e in emp_docs.values() if e.branch}

        branch_docs = {
            b.name: b for b in frappe.get_all(
                "Branch",
                filters={"name": ["in", list(branches)]},
                fields=["name", "car_rate_per_km", "bike_rate_per_km"],
            )
        }

        company = (
            frappe.defaults.get_user_default("Company")
            or frappe.db.get_single_value("Global Defaults", "default_company")
        )

        journeys_to_update = []
        claim_count = 0

        # -------------------------
        # Create Claims
        # -------------------------
        for emp, months in grouped.items():

            emp_doc = emp_docs.get(emp)

            #  Validation - Employee Missing
            if not emp_doc:
                frappe.throw(f"Employee record not found for {emp}")

            # Validation - Branch Missing
            if not emp_doc.branch:
                frappe.throw(
                    f"Branch is not selected for Employee "
                    f"{emp_doc.employee_name} ({emp})"
                )

            branch_doc = branch_docs.get(emp_doc.branch)

            #  Validation - Branch Rate Missing
            if not branch_doc:
                frappe.throw(
                    f"Branch '{emp_doc.branch}' is missing rate configuration"
                )

            claim = frappe.new_doc("Expense Claim")
            claim.employee = emp
            claim.posting_date = to_date
            claim.company = company
            claim.purpose = "Travel"

            for month, vehicles in months.items():

                for vehicle, data in vehicles.items():

                    rate = (
                        flt(branch_doc.car_rate_per_km)
                        if vehicle.lower() == "car"
                        else flt(branch_doc.bike_rate_per_km)
                    )

                    if not rate:
                        continue

                    amount = data["dist"] * rate

                    description = (
                        f"{emp_doc.employee_name} - {vehicle} ({month})<br>"
                        + "<br>".join(data["desc"])
                        + f"<br>Total Distance: {data['dist']:.2f} KM"
                        + f"<br>Rate: ₹{rate}"
                        + f"<br>Total: ₹{amount:.2f}"
                    )

                    claim.append("expenses", {
                        "expense_date": to_date,
                        "expense_type": "Travel",
                        "description": description,
                        "amount": amount,
                        "sanctioned_amount": amount,
                    })

                    journeys_to_update.extend(data["ids"])

            if claim.expenses:
                claim.flags.ignore_mandatory = True
                claim.insert(ignore_permissions=True)
                claim_count += 1

        # -------------------------
        # Bulk Journey Update
        # -------------------------
        if journeys_to_update:
            frappe.db.set_value(
                "Checkin Journey",
                {"name": ["in", journeys_to_update]},
                "ec_submitted",
                1,
            )

        frappe.logger().info(
            f"Travel Expense Completed: {claim_count} claims, "
            f"{len(journeys_to_update)} journeys updated"
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Travel Expense Error"
        )
        raise
