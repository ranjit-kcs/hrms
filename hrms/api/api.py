import frappe
import json

# -------------------- GET ALL --------------------
@frappe.whitelist()
def get_all_lead():
    try:
        docs = frappe.get_all("Lead", fields=["*"], ignore_permissions=True)
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
        return {"success": True, "data": doc}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Lead - Create Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to create Lead"}

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
def create_hospital(**kwargs):
    try:
        doc = frappe.new_doc("Hospital")
        for k, v in kwargs.items():
            doc.set(k, v)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "data": doc}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Hospital - Create Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to create Hospital"}


@frappe.whitelist()
def get_all_opportunity():
    try:
        docs = frappe.get_all("Opportunity", fields=["*"], ignore_permissions=True)
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
def get_all_car():
    try:
        docs = frappe.get_all("CAR", fields=["*"], ignore_permissions=True)
        return {"success": True, "data": docs}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "CAR - GetAll Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to fetch CAR records"}


@frappe.whitelist()
def create_car(**kwargs):
    try:
        doc = frappe.new_doc("CAR")
        for k, v in kwargs.items():
            doc.set(k, v)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "data": doc}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "CAR - Create Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "message": "Failed to create CAR"}


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
    




@frappe.whitelist(allow_guest=True)
def save_location():
    payload = frappe.local.form_dict.get("payload")
    if isinstance(payload, str):
        payload = frappe.parse_json(payload)

    raw = payload
    data = payload
    address = {}

    # --------------------------------------------------
    # 🔹 STEP 1: NORMALIZE PAYLOAD (ALL APIs)
    # --------------------------------------------------

    # Azure Maps
    if raw.get("addresses") and isinstance(raw["addresses"], list):
        first = raw["addresses"][0]
        address = first.get("address", {})
        data = address
        position = first.get("position")

    # OpenStreetMap
    elif raw.get("address"):
        address = raw.get("address", {})
        data = raw
        position = f'{raw.get("lat")},{raw.get("lon")}'

    # Generic fallback
    else:
        address = raw
        position = raw.get("position")

    # --------------------------------------------------
    # 🔹 STEP 2: DISPLAY NAME (PRIORITY ORDER)
    # --------------------------------------------------
    displayname = (
        data.get("display_name")
        or address.get("freeformAddress")
        or address.get("label")
        or address.get("name")
        or raw.get("name")
        or ""
    )

    # --------------------------------------------------
    # 🔹 STEP 3: LAT / LON
    # --------------------------------------------------
    latitude = longitude = None

    if raw.get("lat") and raw.get("lon"):
        latitude = float(raw["lat"])
        longitude = float(raw["lon"])

    elif position:
        latitude, longitude = map(float, position.split(","))

    # --------------------------------------------------
    # 🔹 STEP 4: ADDRESS FIELDS (UNIFIED)
    # --------------------------------------------------
    road = (
        address.get("road")
        or address.get("street")
        or address.get("streetName")
        or address.get("streetNameAndNumber")
    )

    suburb = (
        address.get("suburb")
        or address.get("municipalitySubdivision")
        or address.get("neighbourhood")
        or address.get("quarter")
    )

    city = (
        address.get("city")
        or address.get("municipality")
        or address.get("localName")
        or address.get("city_district")
        or address.get("town")
    )

    state = (
        address.get("state")
        or address.get("countrySubdivision")
        or address.get("state_district")
        or address.get("countrySubdivisionName")
    )

    postcode = (
        address.get("postcode")
        or address.get("postalCode")
        or address.get("zip")
    )

    # --------------------------------------------------
    # 🔹 STEP 5: BOUNDING BOX (ALL FORMATS)
    # Always → [south, north, west, east]
    # --------------------------------------------------
    boundingbox = None

    # OpenStreet
    if isinstance(data.get("boundingbox"), list) and len(data["boundingbox"]) == 4:
        boundingbox = data["boundingbox"]

    # Azure
    elif address.get("boundingBox"):
        bbox = address["boundingBox"]
        ne_lat, ne_lon = map(str.strip, bbox["northEast"].split(","))
        sw_lat, sw_lon = map(str.strip, bbox["southWest"].split(","))
        boundingbox = [sw_lat, ne_lat, sw_lon, ne_lon]

    # GeoJSON
    elif raw.get("bbox") and len(raw["bbox"]) == 4:
        west, south, east, north = raw["bbox"]
        boundingbox = [str(south), str(north), str(west), str(east)]

    # Fallback → generate small box
    elif latitude and longitude:
        d = 0.0001
        boundingbox = [
            str(latitude - d),
            str(latitude + d),
            str(longitude - d),
            str(longitude + d)
        ]

    if not boundingbox:
        frappe.throw("Unable to resolve bounding box")

    # --------------------------------------------------
    # 🔹 STEP 6: SAVE DOC
    # --------------------------------------------------
    doc = frappe.new_doc("Location Description")
    doc.display_name = displayname
    doc.bounding_box = json.dumps(boundingbox)
    doc.latitude = latitude
    doc.longitude = longitude
    doc.road = road
    doc.suburb = suburb
    doc.city = city
    doc.state = state
    doc.postcode = postcode

    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "name": doc.name,
        "display_name": displayname,
        "latitude": latitude,
        "longitude": longitude
    }



@frappe.whitelist(allow_guest=True)
def find_location_by_latlon(lat, lon, buffer=0.0001):
    lat = float(lat)
    lon = float(lon)
    buffer = float(buffer)

    locations = frappe.get_all(
        "Location Description",
        fields=["name", "display_name", "bounding_box"]
    )

    for loc in locations:
        if not loc.bounding_box:
            continue

        try:
            south, north, west, east = map(
                float, json.loads(loc.bounding_box)
            )

            # 🔹 Expand bounding box
            south -= buffer
            north += buffer
            west  -= buffer
            east  += buffer

            if south <= lat <= north and west <= lon <= east:
                return {
                    "found": True,
                    "name": loc.name,
                    "display_name": loc.display_name
                }

        except Exception:
            continue

    return {
        "found": False,
        "message": "No location found for given coordinates"
    }
