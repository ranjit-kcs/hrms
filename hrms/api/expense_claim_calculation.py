import frappe
from frappe.utils import get_first_day, get_last_day, add_months, today, flt

@frappe.whitelist()
def calculate_monthly_travel_expenses(method=None):
    """Auto-calculates total travel distance and amount for each employee 
       using approved CheckIn Journey records (docstatus=1, ec_submitted=0). 
       Groups by month + vehicle, creates separate expense rows per month,
       and marks CheckIn Journeys as ec_submitted=1 after processing.
    """
    try:
        from_date = get_first_day(add_months(today(), -1))
        to_date = get_last_day(add_months(today(), -1))

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
                "location",
            ],
            order_by="date asc",
        )

        if not journeys:
            frappe.logger().info("No approved unsubmitted journeys found.")
            return

        employee_data = {}

        for j in journeys:
            emp = j.get("employee")
            if not emp:
                continue

            date = j.get("date")
            month_key = date.strftime("%Y-%m")
            vehicle = (j.get("vehicle_type") or "Bike").strip().capitalize()
            distance = flt(j.get("distance") or 0)

            checkin_desc = j.get("checkin_description") or "No check-in details"
            checkout_desc = j.get("checkout_description") or "No checkout details"

            combined_desc = (
                f"{date} | Check-in: {checkin_desc} | "
                f"Checkout: {checkout_desc} ({distance:.2f} KM)"
            )

            employee_data \
                .setdefault(emp, {}) \
                .setdefault(month_key, {}) \
                .setdefault(vehicle, {
                    "total_distance": 0,
                    "descriptions": [],
                    "journey_ids": [],
                })

            emp_month_vehicle = employee_data[emp][month_key][vehicle]

            emp_month_vehicle["total_distance"] += distance
            emp_month_vehicle["descriptions"].append(combined_desc)
            emp_month_vehicle["journey_ids"].append(j.get("name"))

        total_claims = 0
        updated_journeys = []

        for emp, month_data in employee_data.items():

            employee_name = frappe.db.get_value("Employee", emp, "employee_name") or emp
            branch = frappe.db.get_value("Employee", emp, "branch")

            if not branch:
                continue

            branch_doc = frappe.db.get_value(
                "Branch",
                branch,
                ["car_rate_per_km", "bike_rate_per_km"],
                as_dict=True
            )

            if not branch_doc:
                continue

            company = (
                frappe.defaults.get_user_default("Company")
                or frappe.db.get_single_value("Global Defaults", "default_company")
            )

            expense_claim = frappe.new_doc("Expense Claim")
            expense_claim.employee = emp
            expense_claim.posting_date = to_date
            expense_claim.purpose = "Travel"
            expense_claim.company = company

            total_amount = 0
            employee_journey_ids = []

            for month_key, vehicle_data in month_data.items():

                month_start = get_first_day(month_key + "-01")
                month_end = get_last_day(month_key + "-01")

                for vehicle, data in vehicle_data.items():

                    if vehicle.lower() == "car":
                        rate_per_km = flt(branch_doc.car_rate_per_km or 0)
                    else:
                        rate_per_km = flt(branch_doc.bike_rate_per_km or 0)

                    if not rate_per_km:
                        print(f"⚠️ Missing rate for {vehicle} in {branch}, skipping.")
                        continue

                    total_distance = data["total_distance"]
                    amount = total_distance * rate_per_km
                    total_amount += amount

                    employee_journey_ids.extend(data["journey_ids"])

                    desc_lines = [
                        f"{i+1}. {line}"
                        for i, line in enumerate(data["descriptions"])
                    ]

                    description = (
                        f"Auto-generated travel summary for {employee_name} ({vehicle})<br>"
                        f"Branch: {branch}<br>"
                        f"Month: {month_key}<br>"
                        f"Period: {month_start} to {month_end}<br><br>"
                        + "<br>".join(desc_lines)
                        + f"<br><br>Total Distance: {total_distance:.2f} KM<br>"
                        f"Rate per KM: ₹{rate_per_km}<br>"
                        f"Total Amount: ₹{amount:.2f}"
                    )

                    expense_claim.append(
                        "expenses",
                        {
                            "expense_date": month_end,
                            "expense_type": "Travel",
                            "description": description,
                            "amount": amount,
                            "sanctioned_amount": amount,
                        },
                    )

            if not expense_claim.expenses:
                continue

            expense_claim.flags.ignore_mandatory = True
            expense_claim.insert(ignore_permissions=True)
            frappe.db.commit()

            for journey_id in employee_journey_ids:
                frappe.db.set_value("CheckIn Journey", journey_id, "ec_submitted", 1)
                updated_journeys.append(journey_id)

            frappe.db.commit()
            total_claims += 1

    except Exception as e:
        frappe.log_error("Monthly Travel Expense Scheduler Error", frappe.get_traceback())