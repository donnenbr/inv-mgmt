import csv

# number of freezers and shelves to create.  we must fit on average 4 vials per lot and we have 6.7 million lots!!!
NUM_FREEZERS = 277
SHELVES_PER_FREEZER = 10

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

FIELD_NAMES = ["barcode", "type", "parent_barcode", "parent_position"]

freezer_data = []
for i in range(NUM_FREEZERS):
	freezer_data.append({
		"barcode": f"freezer-{i+1}", 
		"type": "freezer"})
with open("freezers.csv","wt") as f:
	wtr = csv.DictWriter(f, fieldnames=["barcode", "type"])
	wtr.writeheader()
	wtr.writerows(freezer_data)
	f.flush()

# 10 shelves per freezer
barcode = SHELF_BC
shelf_data = []
for freezer in freezer_data:
	for i in range(SHELVES_PER_FREEZER):
		barcode += 1
		# barcode, type, parent, position
		shelf_data.append({
			"barcode": f"{barcode}",
			"type": "shelf",
			"parent_barcode": freezer['barcode'],
			"parent_position": f"{i+1:02}"})
with open("shelves.csv","wt") as f:
	wtr = csv.DictWriter(f, fieldnames=FIELD_NAMES)
	wtr.writeheader()
	wtr.writerows(shelf_data)
	f.flush()
	
# lastly, the racks
barcode = RACK_BC
rack_data = []
for shelf in shelf_data:
	for row in range(NUMBER_ROWS):
		for col in range(NUMBER_COLUMNS):
			barcode += 1
			# barcode, type, parent, position
			rack_data.append({
				"barcode": f"{barcode}",
				"type": "rack",
				"parent_barcode": shelf['barcode'],
				"parent_position": f"{row+1},{col+1}"})
with open("racks.csv","wt") as f:
	wtr = csv.DictWriter(f, fieldnames=FIELD_NAMES)
	wtr.writeheader()
	wtr.writerows(rack_data)
	f.flush()

