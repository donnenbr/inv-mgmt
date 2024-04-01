import psycopg2 as db
import csv
from random import randint

conn = db.connect(dbname='postgres',user='invmgmt',password='BobbyBear#58',host='localhost',port=5432)
cur = conn.cursor()

print("reagents ...")
sql = "insert into reagent (name,smiles) values (%s, %s)"
ins_data = []
with open("/media/bobby/Removable 1TB/RDSS-MoleculeAnnotations-master/test_data//ChemAcx_Numeric_Annotation_1000000.csv","rt") as f:
	rdr = csv.DictReader(f)
	for row in rdr:
		ins_data.append((row['molIdx'],row['canonical_smile']))
		if len(ins_data) >= 10000:
			cur.executemany(sql, ins_data)
			ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(sql, ins_data)
conn.commit()

print("lots ...")
# make lots
reagent_data = []
cur.execute("select id,name from reagent")
for row in cur.fetchall():
	reagent_data.append(row)
	
sql = "insert into lot (reagent_id,name) values (%(reagent_id)s, %(name)s)"
ins_data = []
for row in reagent_data:
	num_lots = randint(3,10)
	for i in range(num_lots):
		ins_data.append({'reagent_id':row[0], 'name':f"{row[1]}-{i}"})
	if len(ins_data) >= 10000:
		cur.executemany(sql,ins_data)
		ins_data.clear()
if len(ins_data) > 0:
	cur.executemany(sql,ins_data)
	
conn.commit()
		
conn.close()
