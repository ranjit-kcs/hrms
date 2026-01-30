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
    """Optimized Monthly Travel Expense Generator"""

    try:
        from_date = get_first_day(add_months(today(), -1))
        to_date = get_last_day(add_months(today(), -1))

        frappe.logger().info(f"Travel expense calculation {from_date} → {to_date}")

        # ------------------------------------------------------------------
        # Fetch all approved & unsubmitted journeys
        # ------------------------------------------------------------------
        journeys = frappe.get_all(
            "Checkin Journey",
            filters={
                "ec_submitted": 0,
                "docstatus": 1,
            },
            fields=[
                "name",
                "employee",
                "date",
                "distance",
                "vehicle_type",
                "checkin_description",
                "checkout_description",
            ],
            order_by="employee, date",
        )

        if not journeys:
            frappe.logger().info("No Checkin Journeys found")
            return

        # ------------------------------------------------------------------
        #  Group journeys → employee → month → vehicle
        # ------------------------------------------------------------------
        employee_map = {}
        employee_journey_map = {}
        all_employees = set()

        for j in journeys:
            if not j.employee:
                continue

            all_employees.add(j.employee)
            employee_journey_map.setdefault(j.employee, []).append(j.name)

            month_key = j.date.strftime("%Y-%m")
            vehicle = (j.vehicle_type or "Bike").strip().capitalize()
            distance = flt(j.distance or 0)

            checkin_desc = j.checkin_description or "No check-in details"
            checkout_desc = j.checkout_description or "No checkout details"

            combined_desc = (
                f"{j.date} | Check-in: {checkin_desc} | "
                f"Checkout: {checkout_desc} ({distance:.2f} KM)"
            )

            employee_map \
                .setdefault(j.employee, {}) \
                .setdefault(month_key, {}) \
                .setdefault(vehicle, {
                    "total_distance": 0,
                    "descriptions": [],
                    "journey_ids": [],
                })

            bucket = employee_map[j.employee][month_key][vehicle]
            bucket["total_distance"] += distance
            bucket["descriptions"].append(combined_desc)
            bucket["journey_ids"].append(j.name)

        # ------------------------------------------------------------------
        # Prefetch Employee + Branch + Rates (NO loop DB calls)
        # ------------------------------------------------------------------
        employees = frappe.get_all(
            "Employee",
            filters={"name": ["in", list(all_employees)]},
            fields=["name", "employee_name", "branch"],
        )
        employee_info = {e.name: e for e in employees}

        branches = {e.branch for e in employees if e.branch}
        branch_rates = frappe.get_all(
            "Branch",
            filters={"name": ["in", list(branches)]},
            fields=["name", "car_rate_per_km", "bike_rate_per_km"],
        )
        branch_map = {b.name: b for b in branch_rates}

        company = (
            frappe.defaults.get_user_default("Company")
            or frappe.db.get_single_value("Global Defaults", "default_company")
        )

        journeys_to_update = []
        total_claims = 0

        # ------------------------------------------------------------------
        #  Create ONE Expense Claim per employee
        # ------------------------------------------------------------------
        for emp, month_data in employee_map.items():

            emp_doc = employee_info.get(emp)
            if not emp_doc or not emp_doc.branch:
                continue

            branch_doc = branch_map.get(emp_doc.branch)
            if not branch_doc:
                continue

            expense_claim = frappe.new_doc("Expense Claim")
            expense_claim.employee = emp
            expense_claim.posting_date = to_date
            expense_claim.company = company
            expense_claim.purpose = "Travel"

            employee_journey_ids = []

            for month_key, vehicle_data in month_data.items():
                month_start = get_first_day(month_key + "-01")
                month_end = get_last_day(month_key + "-01")

                for vehicle, data in vehicle_data.items():
                    rate = (
                        flt(branch_doc.car_rate_per_km)
                        if vehicle.lower() == "car"
                        else flt(branch_doc.bike_rate_per_km)
                    )

                    if not rate:
                        continue

                    amount = data["total_distance"] * rate
                    employee_journey_ids.extend(data["journey_ids"])

                    desc_lines = [
                        f"{i+1}. {line}"
                        for i, line in enumerate(data["descriptions"])
                    ]

                    description = (
                        f"Auto-generated travel summary for {emp_doc.employee_name} ({vehicle})<br>"
                        f"Branch: {emp_doc.branch}<br>"
                        f"Month: {month_key}<br>"
                        f"Period: {month_start} to {month_end}<br><br>"
                        + "<br>".join(desc_lines)
                        + f"<br><br>Total Distance: {data['total_distance']:.2f} KM<br>"
                        f"Rate per KM: ₹{rate}<br>"
                        f"Total Amount: ₹{amount:.2f}"
                    )

                    expense_claim.append(
                        "expenses",
                        {
                            "expense_date": to_date,
                            "expense_type": "Travel",
                            "description": description,
                            "amount": amount,
                            "sanctioned_amount": amount,
                        },
                    )

            if not expense_claim.expenses:
                continue

            # --------------------------------------------------------------
            #  Insert claim → ONLY then mark journeys
            # --------------------------------------------------------------
            expense_claim.flags.ignore_mandatory = True
            expense_claim.insert(ignore_permissions=True)

            journeys_to_update.extend(employee_journey_ids)
            total_claims += 1

        # ------------------------------------------------------------------
        # Bulk update journeys ONLY if claim created
        # ------------------------------------------------------------------
        if journeys_to_update:
            frappe.db.set_value(
                "Checkin Journey",
                {"name": ["in", journeys_to_update]},
                "ec_submitted",
                1,
            )

        # frappe.db.commit()

        frappe.logger().info(
            f"Travel Expense Completed: {total_claims} claims, "
            f"{len(journeys_to_update)} journeys updated"
        )

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Monthly Travel Expense Scheduler Error",
        )
        raise
