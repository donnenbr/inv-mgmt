from pymongo import MongoClient

import csv

client = MongoClient("mongodb://localhost:27017/inv-mgmt")
db = client.get_database("inv-mgmt")

print("loading reagent data ...")
reagents = {}
with open("/media/bobby/Removable 1TB/inv-data/input-files/reagent.csv","rt") as f:
	rdr = csv.DictReader(f)
	for row in rdr:
		key = row.pop('name')
		row['lots'] = []
		reagents[key] = row
		
print("loading lot data ...")
lots = {}
with open("/media/bobby/Removable 1TB/inv-data/input-files/lot.csv","rt") as f:
	rdr = csv.DictReader(f)
	for row in rdr:
		key = row.pop('name')
		lots[key] = row
		reag = reagents[row['reagent']]
		reag['lots'].append(key)
del lots

print("inserting reagents ...")
coll = db.get_collection("reagent")
# delete any existing data
coll.drop()

num_reagents = len(reagents)
rec_num = 0
arr = []
for (k,v) in reagents.items():
	data = v.copy()
	data["_id"] = k
	arr.append(data)
	rec_num += 1
	if rec_num%10000 == 0:
		print(f"{rec_num}/{num_reagents}")
		coll.insert_many(arr)
		arr.clear()
if len(arr):
	coll.insert_many(arr)


