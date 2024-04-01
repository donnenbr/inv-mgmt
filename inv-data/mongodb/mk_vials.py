import csv
from random import randint
from datetime import datetime

# barcode starting points - extra big because of the vials
SHELF_BC = 100000000
BOX_BC = 200000000
RACK_BC = 300000000
VIAL_BC = 400000000

# units of measure
VOLUME_UOM = 'uL'
CONCENTRATION_UOM = 'uM'
# volumes will be between these values
MIN_VOLUME = 200
MAX_VOLUME = 750
# all concentrations will be the same ala Merck
CONCENTRATION_VALUE = 10.0

# matches what is in container_type.  same for shelves and racks
NUMBER_ROWS = NUMBER_COLUMNS = 10

def gen_position(racks):
	positions = []
	for row in range(NUMBER_ROWS):
		for col in range(NUMBER_COLUMNS):
			positions.append(f"{row+1},{col+1}")
	for rack in racks:
		for pos in positions:
			yield (rack,pos)

FIELD_NAMES = ["barcode", "type", "parent_barcode", "parent_position", "lot", "amount", "unit", "concentration", "concentration_unit"]

# load lot names and calculate locations
lots = []
racks = []
print("loading lots ...")
with open("lot.csv","rt") as f:
	rdr = csv.DictReader(f)
	for rec in rdr:
		lots.append(rec['name'])
		
print("loading racks ...")
with open("racks.csv","rt") as f:
	rdr = csv.DictReader(f)
	for rec in rdr:
		racks.append(rec['barcode'])
		
print("generate vials ...")
gp = gen_position(racks)
break_out = False
barcode = VIAL_BC
num_vials = 0
with open("vials.csv","wt") as f:
	wtr = csv.DictWriter(f, fieldnames=FIELD_NAMES)
	wtr.writeheader()
	for lot in lots:
		for i in range(randint(1,5)):
			try:
				parent_bc,parent_pos = next(gp)
				barcode += 1
				volume = randint(MIN_VOLUME,MAX_VOLUME)
				wtr.writerow({
					"barcode": f"{barcode}",
					"type": "vial",
					"parent_barcode": parent_bc,
					"parent_position": parent_pos,
					"lot": lot,
					"amount": volume,
					"unit": VOLUME_UOM,
					"concentration": CONCENTRATION_VALUE,
					"concentration_unit": CONCENTRATION_UOM
				});
				num_vials += 1
			except StopIteration:
				break_out = true
				break
		if break_out:
			break
	f.flush()
print(f"*** created {num_vials} vials")

