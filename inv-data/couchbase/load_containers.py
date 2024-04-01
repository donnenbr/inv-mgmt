from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions

import csv

files = ('freezers', 'shelves', 'racks', 'vials')

auth = PasswordAuthenticator('invmgmt','invmgmt123');
cluster = Cluster.connect('couchbase://localhost', ClusterOptions(auth))
cb = cluster.bucket('inv-mgmt')
cb_coll = cb.collection('container')

for fname in files:
	file_path = f"/media/bobby/Removable 1TB/inv-data/input-files/{fname}.csv"
	print(f"loading {fname} ...") 
	with open(file_path,"rt") as f:
		rec_num = 0
		rdr = csv.DictReader(f)
		for row in rdr:
			if row.get('barcode') == 'barcode' or row.get('lot') == 'name':
				print(f"*** bad {row}")
			key = row.pop('barcode')
			lot = row.get("lot")
			"""
			if lot:
				row['amount'] = float(row['amount'])
				row['concentration'] = float(row['concentration'])
			cb_coll.insert(key, row)
			rec_num += 1
			if rec_num%1000 == 0:
				print(f"{rec_num}")
			"""
