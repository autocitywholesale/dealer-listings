#!/usr/bin/env python3
"""Make incoming/<VIN>/build_sheet.pdf (one-page Factory Specifications, from NHTSA vPIC decode in incoming/<VIN>/vpic.json).
Usage: python3 make_specsheet.py VIN [VIN...]   Only real decoded fields are printed; no MSRP/options are invented."""
import json, os, sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
ROOT = os.path.dirname(os.path.abspath(__file__))
def fields(r):
    g = lambda k: (r.get(k) or "").strip()
    def eng():
        p = []
        if g("DisplacementL"): p.append(f"{float(g('DisplacementL')):g}L")
        if g("EngineConfiguration") or g("EngineCylinders"): p.append(f"{g('EngineConfiguration')} {g('EngineCylinders')}-cyl".strip())
        if g("Turbo") == "Yes": p.append("turbo")
        if g("FuelTypePrimary"): p.append(g("FuelTypePrimary").lower())
        s = ", ".join(p)
        if g("EngineHP"): s += f", {g('EngineHP')} hp"
        return s
    plant = ", ".join(x.title() for x in (g("PlantCity"), g("PlantState"), g("PlantCountry").split(" (")[0]) if x)
    if g("PlantCompanyName"): plant = f"{g('PlantCompanyName')} - {plant}"
    rows = [("VIN", g("VIN")), ("Model year", g("ModelYear")), ("Make", g("Make").title()), ("Model", g("Model")), ("Trim", g("Trim")),
            ("Body style", g("BodyClass").replace("/Multipurpose Vehicle [MPV]", "")), ("Doors", g("Doors")), ("Seating", f"{g('Seats')} seats, {g('SeatRows')} rows" if g("Seats") else ""),
            ("Drivetrain", g("DriveType")), ("Engine", eng()), ("Engine code", g("EngineModel")), ("Valvetrain", g("ValveTrainDesign")),
            ("Transmission", g("TransmissionStyle")),
            ("Wheelbase", f"{g('WheelBaseShort')} in" if g("WheelBaseShort") else ""), ("Wheel size", f"{g('WheelSizeFront')} in" if g("WheelSizeFront") else ""),
            ("Curb weight", f"{g('CurbWeightLB')} lb" if g("CurbWeightLB") else ""), ("GVWR class", g("GVWR")), ("Steering", g("SteeringLocation")),
            ("TPMS", g("TPMS")), ("Manufacturer", g("Manufacturer")), ("Assembly plant", plant)]
    return [(k, v) for k, v in rows if v]
def make(vin):
    d = os.path.join(ROOT, "incoming", vin); r = json.load(open(os.path.join(d, "vpic.json")))["Results"][0]
    rows = fields(r); out = os.path.join(d, "build_sheet.pdf")
    c = canvas.Canvas(out, pagesize=letter); W, H = letter
    c.setFillColorRGB(.043, .145, .271); c.rect(0, H - 90, W, 90, fill=1, stroke=0); c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20); c.drawString(50, H - 45, "Factory Specifications")
    c.setFont("Helvetica", 13); c.drawString(50, H - 68, " ".join(x for x in (r["ModelYear"], r["Make"].title(), r["Model"], r.get("Trim", "")) if x))
    y = H - 125; c.setFillColorRGB(0, 0, 0)
    for i, (k, v) in enumerate(rows):
        if i % 2 == 0: c.setFillColorRGB(.95, .96, .97); c.rect(45, y - 6, W - 90, 22, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0); c.setFont("Helvetica-Bold", 10.5); c.drawString(55, y, k)
        c.setFont("Helvetica", 10.5)
        if len(v) > 70: v = v[:68] + "..."
        c.drawString(190, y, v); y -= 22
    c.setFont("Helvetica-Oblique", 9); c.setFillColorRGB(.3, .3, .3)
    c.drawString(50, 70, "Source: NHTSA VIN decode. Factory window sticker not available.")
    c.drawString(50, 57, "Specifications come from the VIN decode only; no MSRP or option/package list is shown. Verify before purchase.")
    c.drawString(50, 44, "Auto City Fredericton - 40 Main St., Fredericton, NB")
    c.save(); print(out)
if __name__ == "__main__":
    for v in sys.argv[1:]: make(v)
