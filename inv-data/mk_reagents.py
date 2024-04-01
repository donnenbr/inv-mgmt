import sqlite3 as db
import csv
from random import randint

conn = db.connect("inv-data.db")
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

sql = "insert into reagent (name,smiles) values (?,?)"

ins_data = []
with open("/media/bobby/ntfs/rdss-data/ChemAcx_Numeric_Annotation_1000000.csv","rt") as f:
	rdr = csv.DictReader(f)
	for row in rdr:
		ins_data.append((row['molIdx'],row['canonical_smile']))
		if len(ins_data) >= 1000:
			cur.executemany(sql, ins_data)
			ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(sql, ins_data)
conn.commit()

# make lots
reagent_data = []
cur.execute("select id,name from reagent")
for row in cur.fetchall():
	reagent_data.append(row)
	
sql = "insert into lot (reagent_id,name) values (?,?)"
ins_data = []
for row in reagent_data:
	num_lots = randint(3,10)
	for i in range(num_lots):
		ins_data.append((row[0],f"{row[1]}-{i}"))
	if len(ins_data) >= 1000:
		cur.executemany(sql,ins_data)
		ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(sql,ins_data)
	
conn.commit()
		
conn.close()
