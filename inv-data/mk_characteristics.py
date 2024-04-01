import sqlite3 as db
import csv
from random import randint

conn = db.connect("characteristics.db")
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

sql = "insert into reagent_characteristics (reagent_name,mol_wt,num_hydrogens,num_nitrogens,primary_amines,secondary_amines) " + \
	"values (:reagent, :mol_wt, :num_hydrogens, :num_nitrogens, :primary_amines, :secondary_amines)"

ins_data = []
with open("ChemAcx_Numeric_Annotation_1000000.csv","rt") as f:
	rdr = csv.DictReader(f)
	num_rows = 0
	for row in rdr:
		d = { "reagent": row['molIdx'] }
		d['mol_wt'] = randint(50,200)
		d['num_hydrogens'] = randint(0, 20)
		d['num_nitrogens'] =  randint(0, 20)
		d['primary_amines'] =  randint(0, 5)
		d['secondary_amines'] =  randint(0, 5)
		# print(d)
		ins_data.append(d)
		if len(ins_data) >= 1000:
			num_rows += len(ins_data)
			print(f"insert {num_rows}")
			cur.executemany(sql, ins_data)
			ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(sql, ins_data)
conn.commit()
		
conn.close()
