from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions

import csv

auth = PasswordAuthenticator('invmgmt','invmgmt123');
cluster = Cluster.connect('couchbase://localhost', ClusterOptions(auth))
cb = cluster.bucket('inv-mgmt')
cb_coll = cb.collection('lot')

print("loading lot data ...")
rec_num = 0
with open("/media/bobby/Removable 1TB/inv-data/input-files/lot.csv","rt") as f:
	rdr = csv.DictReader(f)
	for row in rdr:
		key = row.pop('name')
		cb_coll.insert(key, row)
		if rec_num%1000 == 0:
			print(f"{rec_num}")
		
