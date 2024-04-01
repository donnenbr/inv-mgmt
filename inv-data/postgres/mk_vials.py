import psycopg2 as db
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

CONTAINER_INSERT_SQL = """insert into container
	(barcode,type_id,lot_id,amount,unit,concentration,concentration_unit)
	values (%s, %s, %s, %s, %s, %s, %s)"""
CONT_CONT_UPDATE_SQL = "update container_container set container_id=%(container_id)s where id=%(location_id)s"

conn = db.connect(dbname='postgres',user='invmgmt',password='BobbyBear#58',host='localhost',port=5432)
cur = conn.cursor()
cur.arraysize = 1000

sql = "select id,name,number_rows,number_columns from container_type"
container_types = {}
cur.execute(sql)
for row in cur.fetchall():
	id,name,number_rows,number_columns = row
	container_types[name] = { "id":id, "number_rows":number_rows, "number_columns":number_columns }
# print(container_types)

# clear out any vial data
vial_type_id = container_types['vial']['id']
cur.execute("""update container_container set container_id = null where parent_container_id in (
	select id from container where type_id = %s) and container_id is not null""",(vial_type_id,))
cur.execute("delete from container where type_id = %s", (vial_type_id,))
conn.commit()

# this is faster than fetchall()
lot_ids = []
cur.execute("select id from lot")
while True:
	rows = cur.fetchmany()
	if not rows:
		break
	for row in rows:
		lot_ids.append(row[0])
		
ins_data = []
barcode = VIAL_BC
for lot_id in lot_ids:
	for i in range(randint(1,5)):
		barcode += 1
		volume = randint(MIN_VOLUME,MAX_VOLUME)
		ins_data.append((barcode,vial_type_id,lot_id,volume,VOLUME_UOM,CONCENTRATION_VALUE,CONCENTRATION_UOM))
		if len(ins_data) >= 1000:
			cur.executemany(CONTAINER_INSERT_SQL, ins_data)
			ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(CONTAINER_INSERT_SQL, ins_data)
	ins_data.clear()
conn.commit()

# now locate them and use named params
vial_ids = []
cur.execute("select id from container where type_id = %(cont_type_id)s", {"cont_type_id":vial_type_id})
while True:
	rows = cur.fetchmany()
	if not rows:
		break
	for row in rows:
		vial_ids.append(row[0])
rack_type_id = container_types['rack']['id']
location_ids = []
# because we know the type id is a number
cur.execute(f"""select id from container_container where container_id is null
	and parent_container_id in (select id from container where type_id={rack_type_id})""")
while True:
	rows = cur.fetchmany()
	if not rows:
		break
	for row in rows:
		location_ids.append(row[0])
print(f"vials {len(vial_ids)}, locs {len(location_ids)}")
del ins_data
update_data = []
for vial_id,location_id in zip(vial_ids,location_ids):
	update_data.append({"container_id":vial_id,"location_id":location_id})
	if len(update_data) >= 1000:
		cur.executemany(CONT_CONT_UPDATE_SQL, update_data)
		update_data.clear()
if len(update_data) > 0:
	cur.executemany(CONT_CONT_UPDATE_SQL, update_data)
	update_data.clear()
conn.commit()

conn.close()
