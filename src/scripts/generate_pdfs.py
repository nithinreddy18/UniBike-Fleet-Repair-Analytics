import subprocess
import sys
import os

try:
    import fpdf  # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])

from fpdf import FPDF


def generate_manual_1():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    content = """Bicycle Maintenance Manual: Derailleurs and Gears

1. Adjusting the Rear Derailleur
The rear derailleur shifts the chain across the rear cassette.
Step 1: Shift the chain onto the smallest cog.
Step 2: Locate the barrel adjuster on the rear derailleur. Turn it counter-clockwise to increase tension if shifting to larger cogs is sluggish. Turn it clockwise to decrease tension if shifting to smaller cogs is sluggish.
Step 3: Check the High (H) and Low (L) limit screws. The H screw aligns the pulley with the smallest cog. The L screw aligns it with the largest cog. Adjust them carefully to prevent the chain from falling off.

2. Fixing a Dropped Chain
If your chain drops frequently, your limit screws are likely out of adjustment.
Step 1: Put the chain back on the chainring manually.
Step 2: Check the front derailleur alignment. It should be parallel to the chainrings with 1-3mm clearance.
"""
    for line in content.split("\n"):
        pdf.cell(
            200, 10, txt=line.encode("latin-1", "replace").decode("latin-1"), ln=True
        )

    os.makedirs("data", exist_ok=True)
    pdf.output("data/derailleur_manual.pdf")
    print("Generated data/derailleur_manual.pdf")


def generate_manual_2():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    content = """Bicycle Maintenance Manual: Tires and Brakes

1. Fixing a Flat Tire
A flat tire is the most common bicycle issue.
Step 1: Remove the wheel from the bike.
Step 2: Use tire levers to pry one side of the tire off the rim.
Step 3: Remove the old inner tube and find the puncture. Also check the inside of the tire for thorns or glass.
Step 4: Slightly inflate the new inner tube and place it inside the tire.
Step 5: Seat the tire back onto the rim and inflate to the recommended PSI printed on the tire sidewall.

2. Adjusting Brake Pads
Brake pads must hit the rim squarely to be effective.
Step 1: Loosen the brake pad bolt using an Allen key.
Step 2: Align the pad so it is flat against the rim braking surface.
Step 3: Ensure it does not touch the tire, which can cause a blowout.
Step 4: Tighten the bolt securely.
"""
    for line in content.split("\n"):
        pdf.cell(
            200, 10, txt=line.encode("latin-1", "replace").decode("latin-1"), ln=True
        )

    pdf.output("data/tires_brakes_manual.pdf")
    print("Generated data/tires_brakes_manual.pdf")


if __name__ == "__main__":
    generate_manual_1()
    generate_manual_2()
