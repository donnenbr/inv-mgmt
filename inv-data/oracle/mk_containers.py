import cx_Oracle as db

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

CONTAINER_INSERT_SQL = "insert into container(barcode,type_id) values (:1, :2)"
CONT_CONT_INSERT_SQL = "insert into container_container (container_id,parent_container_id,position) values (:1, :2, :3)"

conn = db.connect(dsn="localhost/freepdb1", user="invmgmt", password="BobbyBear#58")
cur = conn.cursor()

cur.execute("delete from container_container")
cur.execute("delete from container")
conn.commit()

sql = "select id,name,number_rows,number_columns from container_type"
container_types = {}
cur.execute(sql)
for row in cur.fetchall():
	id,name,number_rows,number_columns = row
	container_types[name] = { "id":id, "number_rows":number_rows, "number_columns":number_columns }
# print(container_types)

# dict to hold barcde : container id relationship
container_d = {}

# 277 freezers
print("freezers ...")
ins_data = []
freezer_type_id = container_types['freezer']['id']
for i in range(NUM_FREEZERS):
	ins_data.append((f"freezer-{i+1}",freezer_type_id))
cur.executemany(CONTAINER_INSERT_SQL, ins_data)
conn.commit()

# 10 shelves per freezer
print("shelves ...")
barcode = SHELF_BC
cur.execute("select id from container where type_id = :1", (freezer_type_id,))
shelf_data = []
for row in cur.fetchall():
	for i in range(SHELVES_PER_FREEZER):
		barcode += 1
		# barcode, parent, position
		shelf_data.append((f"{barcode}",row[0],f"{i+1:02}"))
ins_data.clear()
shelf_type_id = container_types['shelf']['id']
for row in shelf_data:
	ins_data.append((row[0],shelf_type_id))
cur.executemany(CONTAINER_INSERT_SQL, ins_data)
ins_data.clear()
cur.execute("select id,barcode from container where type_id = :1", (shelf_type_id,))
for row in cur.fetchall():
	container_d[row[1]] = row[0]
for row in shelf_data:
	barcode,parent_id,position = row
	shelf_id = container_d[barcode]
	ins_data.append((shelf_id,parent_id,position))
cur.executemany(CONT_CONT_INSERT_SQL, ins_data)
conn.commit()
del shelf_data
container_d.clear()

# racks - fill the shelves
print("racks ...")
rack_type_id = container_types['rack']['id']
num_rows = container_types['shelf']['number_rows']
num_cols = container_types['shelf']['number_columns']
rack_data = []
barcode = RACK_BC
cur.execute("select id from container where type_id = :1", (shelf_type_id,))
for row in cur.fetchall():
	for shelf_row in range(num_rows):
		for shelf_col in range(num_cols):
			barcode += 1
			pos = f"{shelf_row+1},{shelf_col+1}"
			# barcode, parent, position
			rack_data.append((f"{barcode}",row[0],pos))
ins_data.clear()
for row in rack_data:
	ins_data.append((row[0],rack_type_id))
cur.executemany(CONTAINER_INSERT_SQL, ins_data)
ins_data.clear()
cur.execute("select id,barcode from container where type_id = :1", (rack_type_id,))
for row in cur.fetchall():
	container_d[row[1]] = row[0]
for row in rack_data:
	barcode,parent_id,position = row
	rack_id = container_d[barcode]
	ins_data.append((rack_id,parent_id,position))
cur.executemany(CONT_CONT_INSERT_SQL, ins_data)
conn.commit()
# keeping container_d for the next step

# now create EMPTY slots in the racks
num_rows = container_types['rack']['number_rows']
num_cols = container_types['rack']['number_columns']
ins_data.clear()
for rack_id in container_d.values():
	for rack_row in range(num_rows):
		for rack_col in range(num_cols):
			pos = f"{rack_row+1},{rack_col+1}"
			ins_data.append((None,rack_id,pos))
	if len(ins_data) >= 1000:
		cur.executemany(CONT_CONT_INSERT_SQL, ins_data)
		ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(CONT_CONT_INSERT_SQL, ins_data)
	ins_data.clear()
conn.commit()

conn.close()
