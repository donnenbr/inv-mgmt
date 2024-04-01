from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions

import csv

auth = PasswordAuthenticator('invmgmt','invmgmt123');
cluster = Cluster.connect('couchbase://localhost', ClusterOptions(auth))
cb = cluster.bucket('inv-mgmt')

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
num_reagents = len(reagents)
rec_num = 0
cb_coll = cb.collection('reagent')
for (k,v) in reagents.items():
	cb_coll.insert(k,v)
	rec_num += 1
	if rec_num%1000 == 0:
		print(f"{rec_num}/{num_reagents}")

