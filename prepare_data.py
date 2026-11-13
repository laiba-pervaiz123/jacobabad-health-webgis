"""
prepare_data.py
Reads the Excel file and writes insert_data.sql (INSERT statements for PostGIS).
Run:  python prepare_data.py
"""
import re
import openpyxl

EXCEL = "Jacobabad_Medical_Facilities_final.xlsx"
OUT = "insert_data.sql"

# facility_type -> category used on the website
CATEGORY = {
    "Hospital": "Hospitals",
    "Cardiac Facility": "Hospitals",
    "Medical Center": "Medical Centers & Clinics",
    "Clinic": "Medical Centers & Clinics",
    "MCH Center": "Medical Centers & Clinics",
    "Diagnostic Lab": "Diagnostic Labs",
    "Pharmacy": "Pharmacies & Medical Stores",
    "Medical Store": "Pharmacies & Medical Stores",
}


def clean_hours(h):
    h = (h or "").strip()
    if not h or h.lower() == "not confim":
        return "Not confirmed"
    if h.lower() == "open 24 hours":
        return "Open 24 hours"
    h = re.sub(r"(?i)(\d)\s*(am|pm)", lambda m: f"{m.group(1)} {m.group(2).upper()}", h)
    return h.replace("-", " - ")


def q(text):
    """Escape a value for SQL."""
    return "'" + str(text).replace("'", "''") + "'"


wb = openpyxl.load_workbook(EXCEL, data_only=True)
ws = wb.worksheets[0]

rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    if r[1] is None:
        continue
    _id, name, ftype, contact, address, lat, lon, hours = r[:8]
    rows.append((name.strip(), ftype.strip(), CATEGORY[ftype.strip()],
                 (contact or "Not listed").strip(), (address or "").strip(),
                 clean_hours(hours), float(lat), float(lon)))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("-- Data for table medical_facilities (generated from Excel)\n")
    f.write("-- NOTE: ST_MakePoint takes LONGITUDE first, then LATITUDE\n\n")
    f.write("TRUNCATE medical_facilities RESTART IDENTITY;\n\n")
    f.write("INSERT INTO medical_facilities "
            "(name, facility_type, category, contact, address, operating_hours, geom) VALUES\n")
    lines = []
    for name, ftype, cat, contact, addr, hours, lat, lon in rows:
        lines.append(f"({q(name)}, {q(ftype)}, {q(cat)}, {q(contact)}, {q(addr)}, {q(hours)},\n"
                     f" ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326))")
    f.write(",\n".join(lines) + ";\n\n")
    f.write("-- Check: should return 25\nSELECT COUNT(*) FROM medical_facilities;\n")

print(f"Done. {len(rows)} facilities written to {OUT}")
