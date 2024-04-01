from pymongo import MongoClient

import csv

client = MongoClient("mongodb://localhost:27017/inv-mgmt")
db = client.get_database("inv-mgmt")

print("loading lot data ...")
coll = db.get_collection("lot")
# delete any existing data
coll.drop()
rec_num = 0
with open("/media/bobby/Removable 1TB/inv-data/input-files/lot.csv","rt") as f:
	rdr = csv.DictReader(f)
	lots = []
	for row in rdr:
		row["_id"] = row.pop('name')
		row["upper_reagent"] = row["reagent"].upper()
		lots.append(row)
		rec_num += 1
		if rec_num%10000 == 0:
			print(f"{rec_num}")
			coll.insert_many(lots)
			lots.clear()
	if len(lots):
		coll.insert_many(lots)

