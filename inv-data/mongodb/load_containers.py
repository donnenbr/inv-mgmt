from pymongo import MongoClient

import csv

client = MongoClient("mongodb://localhost:27017/inv-mgmt")
db = client.get_database("inv-mgmt")

files = ('freezers', 'shelves', 'racks', 'vials')

coll = db.get_collection("container")
coll.drop()

for fname in files:
	file_path = f"/media/bobby/Removable 1TB/inv-data/input-files/{fname}.csv"
	print(f"loading {fname} ...") 
	with open(file_path,"rt") as f:
		rec_num = 0
		rdr = csv.DictReader(f)
		containers = []
		for row in rdr:
			if row.get('barcode') == 'barcode' or row.get('lot') == 'name':
				print(f"*** bad {row}")
			row["_id"] = row.pop('barcode')
			lot = row.get("lot")
			if lot:
				row['amount'] = float(row['amount'])
				row['concentration'] = float(row['concentration'])
			containers.append(row)
			rec_num += 1
			if rec_num%10000 == 0:
				print(f"{rec_num}")
				coll.insert_many(containers)
				containers.clear()
		if len(containers):
			coll.insert_many(containers)
